"""Fail-fast Phase 7 runner: verified backup, staging-only build and repeatability.

Run: python -B scripts/06_stage_financial_model.py --output-dir data/staging
Never promotes candidates, writes processed data, runs SQL or opens Power BI.
"""
import argparse
import calendar
import contextlib
import csv
from datetime import datetime
import hashlib
import importlib.util
import io
import json
from pathlib import Path
import platform
import shutil
import subprocess
import sys
import tempfile
import traceback
from zoneinfo import ZoneInfo

import numpy as np
import pandas as pd
from pipeline_io import ROOT, output_directory

GENERATORS = ('02_generate_master_data', '03_generate_operations', '04_generate_financials')
MASTERS = ('products', 'materials', 'suppliers', 'customers', 'production_lines', 'bom', 'material_suppliers')
OPERATIONS = ('months', 'line_month_capacity', 'production', 'material_consumption',
              'purchase_order_lines', 'material_receipts', 'raw_material_inventory')
FINANCIALS = ('manufacturing_costs', 'production_cost_allocation', 'sales', 'finished_goods_inventory', 'operating_expenses')
DATASETS = MASTERS + OPERATIONS + FINANCIALS


def require(condition, message):
    if not condition:
        raise ValueError(message)


def file_hash(path):
    return hashlib.sha256(Path(path).read_bytes()).hexdigest()


def tree_hashes(path):
    path = Path(path)
    return {str(p.relative_to(path)): file_hash(p) for p in sorted(path.rglob('*')) if p.is_file()}


def protected_hashes(root=ROOT):
    result = {}
    for name in ('data/processed', 'data/raw', 'sql', 'powerbi'):
        result.update({f'{name}/{key}': value for key, value in tree_hashes(Path(root)/name).items()})
    return result


def save_json(path, value):
    with Path(path).open('x', encoding='utf-8') as stream:
        json.dump(value, stream, indent=2, allow_nan=False)
        stream.write('\n')


def backup_processed(root, stamp):
    root = Path(root).resolve()
    source = root/'data/processed'
    hashes = tree_hashes(source)
    require(bool(hashes), 'Processed baseline is absent or empty')
    backup = root/'data/backups'/f'processed_{stamp}'
    backup.mkdir(parents=True, exist_ok=False)
    manifest = dict(source=str(source), backup=str(backup), timestamp=stamp, algorithm='SHA-256', files={})
    for relative, digest in hashes.items():
        original, target = source/relative, backup/relative
        target.parent.mkdir(parents=True, exist_ok=True)
        shutil.copyfile(original, target)
        require(file_hash(target) == digest, f'Backup hash mismatch: {relative}')
        entry = dict(sha256=digest, bytes=original.stat().st_size)
        if original.suffix.lower() == '.csv':
            frame = pd.read_csv(original)
            entry.update(columns=frame.columns.tolist(), rows=len(frame))
        manifest['files'][relative] = entry
    require(tree_hashes(source) == hashes, 'Processed baseline changed during backup')
    save_json(backup/'manifest.json', manifest)
    return backup, manifest


def load_generator(name):
    spec = importlib.util.spec_from_file_location(name, ROOT/'scripts'/f'{name}.py')
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def run_logged(command, log):
    result = subprocess.run(command, cwd=ROOT, text=True, encoding='utf-8', errors='replace', capture_output=True)
    with Path(log).open('a', encoding='utf-8') as stream:
        stream.write('COMMAND: '+subprocess.list2cmdline(list(map(str, command)))+'\n')
        stream.write(result.stdout+result.stderr+'\n')
    require(result.returncode == 0, f'Command failed ({result.returncode}): {subprocess.list2cmdline(list(map(str, command)))}; see {log}')


def build(directory, report):
    directory = output_directory(directory)
    for name in GENERATORS:
        run_logged([sys.executable, '-B', str(ROOT/'scripts'/f'{name}.py'), '--output-dir', str(directory)], report/'generation.log')


def require_complete_schema(frames, financial, operations):
    from economic_assumptions import PRODUCT_DRIVERS, LINE_DRIVERS
    from material_valuation import RECEIPT_COLUMNS, ISSUE_COLUMNS, INVENTORY_COLUMNS
    requirements = dict(products=PRODUCT_DRIVERS, production_lines=LINE_DRIVERS,
        material_receipts=RECEIPT_COLUMNS, material_consumption=ISSUE_COLUMNS,
        raw_material_inventory=INVENTORY_COLUMNS, production_cost_allocation=financial.PRODUCTION_COLUMNS,
        finished_goods_inventory=financial.INVENTORY_COLUMNS,
        sales=(*financial.COGS_COLUMNS, *financial.OUTBOUND_COLUMNS),
        operating_expenses=('fixed_amount_eur', 'variable_rate_pct', 'variable_driver_amount_eur', 'variable_amount_eur'))
    for name, columns in requirements.items():
        require(set(columns).issubset(frames[name].columns), f'Incomplete revised schema: {name}')
    require(operations.has_component_schema(frames['material_consumption'], frames['material_receipts'], frames['raw_material_inventory']), 'Legacy material schema rejected')
    require(financial.has_finished_goods_schema(frames['production_cost_allocation'], frames['sales'], frames['finished_goods_inventory']), 'Legacy FG schema rejected')
    require(financial.has_outbound_schema(frames['sales']), 'Legacy outbound schema rejected')


def validate_candidate(directory, report, label):
    actual = {p.stem for p in Path(directory).glob('*.csv')}
    require(actual == set(DATASETS), f'Candidate file set mismatch: missing={set(DATASETS)-actual}, extra={actual-set(DATASETS)}')
    frames = {name: pd.read_csv(Path(directory)/f'{name}.csv') for name in DATASETS}
    master, operations, financial = [load_generator(name) for name in GENERATORS]
    require_complete_schema(frames, financial, operations)
    checks = []
    with contextlib.redirect_stdout(io.StringIO()) as output:
        master.validate_masters({name: frames[name] for name in MASTERS})
        operations.validate({name: frames[name] for name in MASTERS}, {name: frames[name] for name in OPERATIONS})
        financial.validate({name: frames[name] for name in MASTERS+OPERATIONS}, {name: frames[name] for name in FINANCIALS})
        financial.run_validation_tests({name: frames[name] for name in MASTERS+OPERATIONS}, {name: frames[name] for name in FINANCIALS})
    checks.append(output.getvalue())
    expected_months = pd.date_range('2024-01-01', '2025-12-01', freq='MS').strftime('%Y-%m-%d').tolist()
    require(frames['months'].month_id.tolist() == expected_months, 'Incorrect calendar')
    for name, frame in frames.items():
        require(not frame.isna().any().any(), f'Null export: {name}')
        numbers = frame.select_dtypes(include='number').to_numpy()
        require(np.isfinite(numbers).all() and (numbers >= 0).all(), f'Invalid numeric export: {name}')
        for col in frame:
            if col.endswith('_date') or col == 'month_id':
                pd.to_datetime(frame[col], format='%Y-%m-%d', errors='raise')
    for date in pd.to_datetime(frames['material_receipts'].receipt_date):
        require(date.day == 25, 'Unexpected material receipt date')
    # Ensure master business IDs/product assignments remain compatible with legacy.
    for name, key in (('products','product_id'), ('materials','material_id'), ('suppliers','supplier_id'),
                      ('customers','customer_id'), ('production_lines','line_id')):
        old = pd.read_csv(ROOT/'data/processed'/f'{name}.csv')
        require(set(old[key]) == set(frames[name][key]), f'Changed business-key domain: {name}')
    old_products = pd.read_csv(ROOT/'data/processed/products.csv').set_index('product_id').sort_index()
    new_products = frames['products'].set_index('product_id').sort_index()
    require(old_products.line_id.equals(new_products.line_id), 'Product line assignment changed')
    with (report/'validation.log').open('a', encoding='utf-8') as stream:
        stream.write(label+'\n'+''.join(checks)+'PASS: strict Phase 1-6 schemas, calendar/date parsing, complete file set and stable master keys\n')
    return frames


def financial_review(old, new, financial, report):
    rows = []
    for label, data in (('legacy', old), ('candidate', new)):
        for period in ('2024', '2025', 'combined'):
            frames = {name: data[name] if period == 'combined' else data[name][data[name].month_id.str.startswith(period)] for name in FINANCIALS}
            pnl = financial.profit_totals(frames)
            row = dict(dataset=label, period=period, **{key: value/100 for key, value in pnl.items()})
            row['gross_margin_pct'] = pnl['gross_profit']/pnl['revenue']*100 if pnl['revenue'] else None
            row['operating_margin_pct'] = pnl['operating_profit']/pnl['revenue']*100 if pnl['revenue'] else None
            rows.append(row)
    comparison = pd.DataFrame(rows)
    comparison.to_csv(report/'financial_comparison.csv', index=False, float_format='%.8f')
    sales, allocations = new['sales'], new['production_cost_allocation']
    grouped = sales.groupby('product_id')[['units_shipped', 'net_revenue_eur', 'cogs_eur', 'outbound_freight_eur', *financial.COGS_COLUMNS]].sum()
    grouped['gross_profit_eur'] = grouped.net_revenue_eur-grouped.cogs_eur
    grouped['gross_margin_pct'] = grouped.gross_profit_eur/grouped.net_revenue_eur*100
    grouped['contribution_after_outbound_eur'] = grouped.gross_profit_eur-grouped.outbound_freight_eur
    grouped['contribution_after_outbound_pct'] = grouped.contribution_after_outbound_eur/grouped.net_revenue_eur*100
    grouped['net_asp_eur'] = grouped.net_revenue_eur/grouped.units_shipped
    grouped['manufacturing_cogs_per_unit_eur'] = grouped.cogs_eur/grouped.units_shipped
    for col in financial.COGS_COLUMNS:
        grouped[col.replace('_cogs_eur','_cogs_per_unit_eur')] = grouped[col]/grouped.units_shipped
    produced = new['production'].groupby('product_id')[['attempted_units','good_units','defective_units']].sum()
    grouped = grouped.join(produced)
    grouped['defect_rate_pct'] = grouped.defective_units/grouped.attempted_units*100
    bom = new['bom'].merge(new['materials'][['material_id','base_unit_cost_eur']],on='material_id')
    bom['reference_purchase_cost_eur'] = bom.quantity_kg_per_unit*bom.base_unit_cost_eur
    grouped = grouped.join(bom.groupby('product_id')[['quantity_kg_per_unit','reference_purchase_cost_eur']].sum())
    grouped = grouped.join(new['products'].set_index('product_id'))
    grouped['review_flag'] = np.where(grouped.gross_margin_pct < 0, 'negative gross margin',
                             np.where(grouped.gross_margin_pct > 35, 'gross margin above 35% review threshold', 'within review range'))
    grouped.sort_values('gross_margin_pct').to_csv(report/'product_profitability.csv', float_format='%.8f')
    monthly = sales.groupby(['month_id','product_id'])[['units_shipped','net_revenue_eur','cogs_eur','outbound_freight_eur']].sum()
    monthly['gross_profit_eur'] = monthly.net_revenue_eur-monthly.cogs_eur
    monthly['gross_margin_pct'] = monthly.gross_profit_eur/monthly.net_revenue_eur*100
    monthly.sort_values('gross_margin_pct').to_csv(report/'product_month_profitability.csv', float_format='%.8f')
    schema = {}
    for name in DATASETS:
        before, after = old[name], new[name]
        schema[name] = dict(legacy_rows=len(before), candidate_rows=len(after),
            added_columns=[c for c in after if c not in before], removed_columns=[c for c in before if c not in after],
            legacy_columns=before.columns.tolist(), candidate_columns=after.columns.tolist())
    save_json(report/'schema_changes.json', schema)
    diagnostics = new['manufacturing_costs'].merge(new['line_month_capacity'], on=['month_id','line_id'], validate='one_to_one')
    diagnostics['capacity_utilization_pct'] = diagnostics.attempted_units/diagnostics.effective_capacity_units*100
    diagnostics.to_csv(report/'manufacturing_diagnostics.csv',index=False,float_format='%.8f')
    return comparison, grouped


def main(output_dir):
    target = output_directory(output_dir)
    require(target == ROOT/'data/staging', 'Controlled runner requires exactly data/staging')
    require(not target.exists(), 'Staging already exists; refusing to overwrite an existing candidate')
    stamp = datetime.now(ZoneInfo('Europe/Rome')).strftime('%Y%m%dT%H%M%S%f%z')
    report = ROOT/'reports'/f'phase7_{stamp}'
    report.mkdir(parents=True, exist_ok=False)
    before = protected_hashes()
    save_json(report/'protected_manifest_before.json', before)
    try:
        backup, baseline_manifest = backup_processed(ROOT, stamp)
        print(f'Verified legacy backup: {backup}', flush=True)
        run_logged([sys.executable, '-B', '-m', 'unittest', 'discover', '-s', 'tests', '-v'], report/'tests.log')
        build(target, report)
        first = validate_candidate(target, report, 'STAGING EXPORTED CSV VALIDATION')
        first_hashes = tree_hashes(target)
        print('Staging validated; starting isolated reproducibility run.', flush=True)
        with tempfile.TemporaryDirectory(prefix='staging_repro_', dir=ROOT/'data') as temp:
            repeat = output_directory(temp)
            build(repeat, report)
            validate_candidate(repeat, report, 'REPEAT EXPORTED CSV VALIDATION')
            second_hashes = tree_hashes(repeat)
            require(first_hashes == second_hashes, 'Deterministic CSV hashes do not match')
            save_json(report/'reproducibility.json', dict(status='PASS', files=first_hashes,
                      repeat_files=second_hashes, temporary_directory=str(repeat), temporary_directory_removed_after_success=True))
        require(protected_hashes() == before, 'Protected baseline/raw/SQL/Power BI hashes changed')
        old = {name: pd.read_csv(ROOT/'data/processed'/f'{name}.csv') for name in DATASETS}
        financial = load_generator('04_generate_financials')
        comparison, products = financial_review(old, first, financial, report)
        save_json(report/'validation_results.json', dict(status='PASS', backup=str(backup), staging=str(target),
            candidate_csv_count=len(first_hashes), protected_files_unchanged=True, reproducible=True,
            full_export_validation=True, strict_revised_schema=True, promoted=False,
            runtime=dict(python=platform.python_version(), pandas=pd.__version__, numpy=np.__version__),
            seeds=dict(masters=360, operations=361, financials=362),
            source_hashes={str(p.relative_to(ROOT)): file_hash(p) for p in sorted((ROOT/'scripts').glob('*.py'))},
            row_counts={name: len(frame) for name,frame in first.items()}))
        save_json(report/'protected_manifest_after.json', protected_hashes())
        print('PASS: 19 staging CSVs, exported reconciliations, deterministic repeat and protected baseline.', flush=True)
        print(comparison[['dataset','period','revenue','cogs','gross_margin_pct','operating_profit','operating_margin_pct']].to_string(index=False), flush=True)
        print(f'Reports: {report}', flush=True)
        print(products[['product_name','gross_margin_pct','net_asp_eur','manufacturing_cogs_per_unit_eur','review_flag']].sort_values('gross_margin_pct').to_string(),flush=True)
    except Exception as error:
        # Diagnostic artifacts only: never retry generation after a failed check.
        save_json(report/'FAILED.json', dict(status='FAILED', error=str(error), traceback=traceback.format_exc(),
            protected_files_unchanged=protected_hashes()==before, staging=str(target), promoted=False))
        print(f'STOPPED: {error}; failure details: {report / "FAILED.json"}', file=sys.stderr, flush=True)
        raise


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--output-dir', required=True, type=Path)
    main(parser.parse_args().output_dir)
