"""Generate Phase 1 operations, January 2024--December 2025.

Run: python scripts/03_generate_operations.py --output-dir data/staging.
Processed data is read-only; existing staging outputs cannot be overwritten.
Only the seven operational CSVs named in main() are overwritten.

Assumptions: one warehouse, EUR, no WIP, returns or scrap recovery. BOM kg
apply to attempted units, including defective units. Extra process waste is
0.2--1.2% of BOM demand. Units have equal capacity weight. Downtime reduces
nominal capacity; seasonal utilization leaves additional headroom.
Monthly accounting: all receipts precede consumption; no daily stock claim.
One fully received order per material/month, delivered on day 25 after the
supplier's stated lead time. January orders can start in December 2023.
Opening stock is an explicit legacy balance valued at master base cost plus
estimated inbound freight at the documented base rate.
Purchases replenish demand plus roughly 20--35% of monthly demand as stock.
No purchase delays, taxes or rejected receipts. Inbound freight is capitalized
separately from purchase-material value; see docs/financial_model.md. Prices vary around
master base costs with supplier effects and modest inflation. Periodic
weighted-average cost includes opening stock and all monthly receipts.
Money is stored in cents; each component uses largest-remainder issue allocation
with stable production_id ties for each material/month. Unit costs retain eight decimals.
Kaggle records are not joined or sampled; all operations are synthetic.
"""

from pathlib import Path
import calendar
import hashlib

import numpy as np
import pandas as pd

from pipeline_io import output_directory, parse_output_directory, write_csv

from economic_assumptions import (INBOUND_FREIGHT_BASE_EUR_PER_KG, inbound_freight_rate,
                                  validate_freight_assumptions)
from material_valuation import (cents, value_receipt, value_material_month,
                                RECEIPT_COLUMNS, ISSUE_COLUMNS, INVENTORY_COLUMNS)

ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT / 'data' / 'processed'
SEED = 361
MASTER_NAMES = ('products', 'materials', 'suppliers', 'customers',
                'production_lines', 'bom', 'material_suppliers')


def require(condition, message):
    """Fail validation even when Python runs with optimization enabled."""
    if not bool(condition):
        raise ValueError(message)


def load_masters(input_dir=OUT):
    """Read existing master files and check their keys and relationships."""
    masters = {name: pd.read_csv(Path(input_dir) / f'{name}.csv') for name in MASTER_NAMES}
    validate_masters(masters)
    return masters


def validate_masters(masters):
    """Shared read-only master checks for existing and in-memory candidate data."""
    keys = {'products': ['product_id'], 'materials': ['material_id'],
            'suppliers': ['supplier_id'], 'customers': ['customer_id'],
            'production_lines': ['line_id'], 'bom': ['product_id', 'material_id'],
            'material_suppliers': ['material_id', 'supplier_id']}
    for name, frame in masters.items():
        require(not frame.isna().any().any(), f'{name}: missing values')
        require(not frame.duplicated(keys[name]).any(), f'{name}: duplicate key')
    for child, column, parent in [('products', 'line_id', 'production_lines'),
                                  ('bom', 'product_id', 'products'),
                                  ('bom', 'material_id', 'materials'),
                                  ('material_suppliers', 'material_id', 'materials'),
                                  ('material_suppliers', 'supplier_id', 'suppliers')]:
        require(masters[child][column].isin(masters[parent][column]).all(),
                f'{child}: invalid {column}')
    require(masters['products'].product_id.isin(masters['bom'].product_id).all(), 'Missing BOM')
    require(masters['materials'].material_id.isin(masters['material_suppliers'].material_id).all(), 'Missing supplier')
    for name, col in [('bom', 'quantity_kg_per_unit'), ('materials', 'base_unit_cost_eur'),
                      ('production_lines', 'monthly_capacity_units')]:
        require(np.isfinite(masters[name][col].to_numpy(dtype=float)).all()
                and (masters[name][col] > 0).all(), f'{name}: nonpositive/nonfinite {col}')
    require((masters['materials'].unit == 'kg').all(), 'Only kg supported')


def generate_production(masters, months, rng):
    """Split each line's feasible monthly output between its products."""
    capacities, production, consumption = [], [], []
    for month in months.itertuples(index=False):
        season = 0.84 if month.month_number in (8, 12) else 1.0
        for line in masters['production_lines'].itertuples(index=False):
            downtime = round(float(rng.uniform(2, 7)), 2)
            effective = int(np.floor(line.monthly_capacity_units * (1 - downtime / 100)))
            capacities.append(dict(month_id=month.month_id, line_id=line.line_id,
                                   nominal_capacity_units=line.monthly_capacity_units,
                                   downtime_pct=downtime, effective_capacity_units=effective))
            products = masters['products'].query('line_id == @line.line_id').product_id.tolist()
            if not products:
                continue
            total = int(effective * rng.uniform(0.80, 0.94) * season)
            weights = rng.uniform(0.8, 1.2, len(products))
            allocations = rng.multinomial(total, weights / weights.sum())
            for product, attempted in zip(products, allocations):
                pid = f'PR{len(production) + 1:06d}'
                defects = int(rng.binomial(attempted, rng.uniform(0.01, 0.035)))
                production.append(dict(production_id=pid, month_id=month.month_id,
                                       product_id=product, attempted_units=int(attempted),
                                       defective_units=defects, good_units=int(attempted) - defects))
                for bom in masters['bom'].query('product_id == @product').itertuples(index=False):
                    required = round(int(attempted) * bom.quantity_kg_per_unit, 3)
                    waste = round(required * float(rng.uniform(0.002, 0.012)), 3)
                    consumption.append(dict(production_id=pid, material_id=bom.material_id,
                                            required_kg=required, extra_waste_kg=waste,
                                            consumed_kg=round(required + waste, 3)))
    return pd.DataFrame(capacities), pd.DataFrame(production), pd.DataFrame(consumption)


def generate_material_flow(masters, months, production, consumption, rng):
    """Buy material and capitalize inbound freight; no I/O until main export."""
    validate_freight_assumptions()
    orders, receipts, inventory = [], [], []
    consumption = consumption.copy().sort_values(['production_id', 'material_id']).reset_index(drop=True)
    for col in ('issued_material_value_eur', 'weighted_average_unit_cost_eur', *ISSUE_COLUMNS):
        consumption[col] = 0.0
    linked = consumption.merge(production[['production_id', 'month_id']], on='production_id', validate='many_to_one')
    require(len(linked) == len(consumption), 'Unknown consumption production ID')
    supplier_effect = {sid: float(rng.uniform(0.97, 1.03)) for sid in sorted(masters['suppliers'].supplier_id)}
    suppliers = masters['suppliers'].set_index('supplier_id')
    months = months.sort_values('month_id')
    for material in masters['materials'].sort_values('material_id').itertuples(index=False):
        mid = material.material_id
        approved = sorted(masters['material_suppliers'].query('material_id == @mid').supplier_id.tolist())
        first_demand = linked[(linked.material_id == mid) & (linked.month_id == months.iloc[0].month_id)].consumed_kg.sum() if len(months) else 0
        opening_mills = int(round(first_demand * 0.25 * 1000))
        initial = value_receipt(opening_mills/1000, material.base_unit_cost_eur, INBOUND_FREIGHT_BASE_EUR_PER_KG)
        opening_purchase, opening_freight = initial['purchase_value_eur'], initial['inbound_freight_eur']
        for number, month in enumerate(months.itertuples(index=False)):
            keys = linked.loc[(linked.material_id == mid) & (linked.month_id == month.month_id), ['production_id', 'material_id']]
            mask = pd.MultiIndex.from_frame(consumption[['production_id', 'material_id']]).isin(pd.MultiIndex.from_frame(keys))
            issue_indices = consumption.index[mask].tolist()
            used_mills = sum(int(round(consumption.at[i, 'consumed_kg'] * 1000)) for i in issue_indices)
            target_mills = int(round(used_mills * float(rng.uniform(0.20, 0.35))))
            received_mills = max(0, used_mills + target_mills - opening_mills)
            purchase_value = freight_value = 0.
            if received_mills:
                supplier = str(rng.choice(approved))
                unit_price = round(material.base_unit_cost_eur * supplier_effect[supplier]
                                   * (1 + 0.002 * number) * float(rng.uniform(0.97, 1.03)), 4)
                receipt_date = pd.Timestamp(month.month_id).replace(day=25)
                order_date = receipt_date - pd.Timedelta(days=int(suppliers.at[supplier, 'lead_time_days']))
                oid = f'PO{len(orders) + 1:06d}'
                orders.append(dict(po_line_id=oid, material_id=mid, supplier_id=supplier,
                                   order_date=order_date.date().isoformat(), expected_receipt_date=receipt_date.date().isoformat(),
                                   ordered_kg=received_mills / 1000, agreed_unit_cost_eur=unit_price))
                values = value_receipt(received_mills/1000, unit_price,
                                       inbound_freight_rate(mid, supplier, month.month_id, number))
                purchase_value, freight_value = values['purchase_value_eur'], values['inbound_freight_eur']
                receipts.append(dict(receipt_id=f'RC{len(receipts) + 1:06d}', po_line_id=oid,
                                     receipt_date=receipt_date.date().isoformat(), received_kg=received_mills / 1000,
                                     landed_unit_cost_eur=values['landed_unit_cost_eur'],
                                     receipt_value_eur=values['receipt_value_eur'],
                                     **{col: values[col] for col in RECEIPT_COLUMNS}))
            ledger, issues = value_material_month(opening_mills/1000, opening_purchase, opening_freight,
                         received_mills/1000, purchase_value, freight_value,
                         [consumption.at[i, 'consumed_kg'] for i in issue_indices])
            for index, values in zip(issue_indices, issues):
                for col, amount in values.items():
                    consumption.at[index, col] = amount
            inventory.append(dict(month_id=month.month_id, material_id=mid, **ledger))
            opening_mills = int(round(ledger['closing_kg'] * 1000))
            opening_purchase = ledger['closing_purchase_material_value_eur']
            opening_freight = ledger['closing_inbound_freight_value_eur']
    order_columns = ['po_line_id', 'material_id', 'supplier_id', 'order_date', 'expected_receipt_date',
                     'ordered_kg', 'agreed_unit_cost_eur']
    receipt_columns = ['receipt_id', 'po_line_id', 'receipt_date', 'received_kg',
                       'landed_unit_cost_eur', 'receipt_value_eur', *RECEIPT_COLUMNS]
    return consumption, pd.DataFrame(orders, columns=order_columns), pd.DataFrame(receipts, columns=receipt_columns), pd.DataFrame(inventory)


def has_component_schema(consumption, receipts, inventory):
    """Legacy audits remain supported; partial upgrades must never pass silently."""
    schemas = ((consumption, ISSUE_COLUMNS), (receipts, RECEIPT_COLUMNS), (inventory, INVENTORY_COLUMNS))
    if not any(set(columns) & set(frame.columns) for frame, columns in schemas):
        return False
    for frame, columns in schemas:
        require(set(columns).issubset(frame.columns), 'Incomplete inbound component schema')
    return True


def validate_material_components(production, consumption, orders, receipts, inventory):
    """Read-only checks for receipt valuation, component WAC, issues and carry."""
    require(has_component_schema(consumption, receipts, inventory), 'Missing inbound component schema')
    for frame, keys in ((consumption, ['production_id', 'material_id']), (orders, ['po_line_id']),
                         (receipts, ['receipt_id']), (inventory, ['month_id', 'material_id'])):
        require(not frame.duplicated(keys).any() and not frame.isna().any().any(), 'Invalid material component keys/nulls')
        numeric = frame.select_dtypes(include='number')
        require(np.isfinite(numeric.to_numpy()).all() and (numeric >= 0).all().all(), 'Invalid component numeric value')
    def money(actual, expected, label):
        # Values must already be booked cents, not merely round to matching cents.
        require(abs(float(actual) - cents(actual)/100) < 1e-8, f'{label}: subcent booked value')
        require(cents(actual) == cents(expected), label)
    def quantity(actual, expected, label):
        require(abs(float(actual)-float(expected)) < 1e-8, label)
    rr = receipts.merge(orders, on='po_line_id', validate='one_to_one')
    require(len(rr) == len(receipts) == len(orders), 'Receipt/PO coverage')
    for row in rr.itertuples(index=False):
        quantity(row.received_kg, row.ordered_kg, 'Receipt quantity')
        quantity(row.purchase_unit_cost_eur, row.agreed_unit_cost_eur, 'Purchase price agrees to PO')
        values = value_receipt(row.received_kg, row.purchase_unit_cost_eur, row.inbound_freight_rate_eur_per_kg)
        for col in ('receipt_value_eur', 'purchase_value_eur', 'inbound_freight_eur', 'landed_receipt_value_eur'):
            money(getattr(row, col), values[col], f'Receipt component: {col}')
        require(abs(row.landed_unit_cost_eur - values['landed_unit_cost_eur']) <= 0.0000000051, 'Landed unit cost')
    rr['month_id'] = pd.to_datetime(rr.receipt_date).dt.strftime('%Y-%m-01')
    linked = consumption.merge(production[['production_id', 'month_id']], on='production_id', validate='many_to_one')
    require(len(linked) == len(consumption), 'Component production FK')
    keys = set(map(tuple, inventory[['month_id', 'material_id']].to_numpy()))
    for movements in (rr, linked):
        require(set(map(tuple, movements[['month_id', 'material_id']].to_numpy())).issubset(keys), 'Component movement outside ledger')
    for row in inventory.itertuples(index=False):
        receipt = rr[(rr.month_id == row.month_id) & (rr.material_id == row.material_id)]
        issues = linked[(linked.month_id == row.month_id) & (linked.material_id == row.material_id)].sort_values('production_id')
        quantity(row.received_kg, receipt.received_kg.sum(), 'Ledger receipt quantity')
        money(row.receipt_purchase_material_value_eur, receipt.purchase_value_eur.sum(), 'Ledger purchase receipts')
        money(row.receipt_inbound_freight_value_eur, receipt.inbound_freight_eur.sum(), 'Ledger freight receipts')
        ledger, expected_issues = value_material_month(
            row.opening_kg, row.opening_purchase_material_value_eur, row.opening_inbound_freight_value_eur,
            row.received_kg, row.receipt_purchase_material_value_eur, row.receipt_inbound_freight_value_eur,
            issues.consumed_kg.tolist())
        for col, value in ledger.items():
            if col.endswith('unit_cost_eur'):
                require(abs(getattr(row, col)-value) <= 0.0000000051, f'Component WAC: {col}')
            elif col.endswith('_kg'):
                quantity(getattr(row, col), value, f'Component kg: {col}')
            else:
                money(getattr(row, col), value, f'Inventory component: {col}')
        for actual, expected in zip(issues.itertuples(index=False), expected_issues):
            for col, value in expected.items():
                if col.endswith('unit_cost_eur'):
                    require(abs(getattr(actual, col)-value) <= 0.0000000051, f'Issue WAC: {col}')
                else:
                    money(getattr(actual, col), value, f'Issue component: {col}')
    for _, group in inventory.sort_values('month_id').groupby('material_id'):
        rows = list(group.itertuples(index=False))
        for before, after in zip(rows, rows[1:]):
            quantity(after.opening_kg, before.closing_kg, 'Component quantity carry')
            for component in ('purchase_material', 'inbound_freight'):
                money(getattr(after, f'opening_{component}_value_eur'),
                      getattr(before, f'closing_{component}_value_eur'), f'Component carry: {component}')


def validate(m, f):
    """Independently reconcile keys, capacity, BOM, receipts and stock ledgers."""
    keys = {'months': ['month_id'], 'line_month_capacity': ['month_id', 'line_id'],
            'production': ['production_id'], 'material_consumption': ['production_id', 'material_id'],
            'purchase_order_lines': ['po_line_id'], 'material_receipts': ['receipt_id'],
            'raw_material_inventory': ['month_id', 'material_id']}
    for name, frame in f.items():
        require(not frame.isna().any().any(), f'{name}: nulls')
        require(not frame.duplicated(keys[name]).any(), f'{name}: duplicate key')
        numbers = frame.select_dtypes(include='number')
        require(np.isfinite(numbers.to_numpy()).all() and (numbers >= 0).all().all(), f'{name}: invalid balance')
        if 'month_id' in frame:
            require(frame.month_id.isin(f['months'].month_id).all(), f'{name}: month FK')
    p, c, o, r, inv = (f[n] for n in ('production', 'material_consumption', 'purchase_order_lines', 'material_receipts', 'raw_material_inventory'))
    component_schema = has_component_schema(c, r, inv)
    cap = f['line_month_capacity']
    require(len(f['months']) == 24 and len(p) == 24 * len(m['products']), 'Incomplete period/product coverage')
    require(not p.duplicated(['month_id', 'product_id']).any(), 'Duplicate production grain')
    for frame, col, parent in [(p, 'product_id', m['products']), (c, 'production_id', p),
                               (c, 'material_id', m['materials']), (o, 'material_id', m['materials']),
                               (o, 'supplier_id', m['suppliers']), (r, 'po_line_id', o),
                               (inv, 'material_id', m['materials']), (cap, 'line_id', m['production_lines'])]:
        require(frame[col].isin(parent[col]).all(), f'Invalid FK: {col}')
    require((p.good_units == p.attempted_units - p.defective_units).all(), 'Output reconciliation')
    used = p.merge(m['products'][['product_id', 'line_id']], on='product_id').groupby(['month_id', 'line_id']).attempted_units.sum()
    indexed_cap = cap.set_index(['month_id', 'line_id'])
    require((used <= indexed_cap.effective_capacity_units.reindex(used.index)).all(), 'Capacity exceeded')
    nominal = cap.line_id.map(m['production_lines'].set_index('line_id').monthly_capacity_units)
    require((cap.nominal_capacity_units == nominal).all(), 'Nominal capacity mismatch')
    require((cap.effective_capacity_units == np.floor(nominal * (1 - cap.downtime_pct / 100))).all(), 'Effective capacity mismatch')
    expected = p.merge(m['bom'], on='product_id')
    actual = c.merge(expected[['production_id', 'material_id', 'attempted_units', 'quantity_kg_per_unit', 'month_id']],
                     on=['production_id', 'material_id'], how='outer', indicator=True, validate='one_to_one')
    require((actual['_merge'] == 'both').all(), 'Missing/invalid BOM consumption')
    require(np.allclose(actual.required_kg, (actual.attempted_units * actual.quantity_kg_per_unit).round(3), atol=0.00001, rtol=0), 'BOM quantity mismatch')
    require(np.allclose(c.consumed_kg, c.required_kg + c.extra_waste_kg, atol=0.00001, rtol=0), 'Waste reconciliation')
    approved = pd.MultiIndex.from_frame(m['material_suppliers'][['material_id', 'supplier_id']])
    require(pd.MultiIndex.from_frame(o[['material_id', 'supplier_id']]).isin(approved).all(), 'Unapproved supplier')
    rr = r.merge(o, on='po_line_id', validate='one_to_one')
    require(len(rr) == len(o), 'Unreceived orders')
    lead = rr.supplier_id.map(m['suppliers'].set_index('supplier_id').lead_time_days)
    require(((pd.to_datetime(rr.receipt_date) - pd.to_datetime(rr.order_date)).dt.days == lead).all(), 'Supplier lead time')
    require((rr.receipt_date == rr.expected_receipt_date).all(), 'Receipt date mismatch')
    require(np.allclose(rr.received_kg, rr.ordered_kg, atol=0.00001, rtol=0), 'Receipt quantity')
    if component_schema:
        validate_material_components(p, c, o, r, inv)
    else:
        require(np.allclose(rr.landed_unit_cost_eur, rr.agreed_unit_cost_eur, atol=0.000001, rtol=0), 'Receipt price')
    require(np.allclose(rr.receipt_value_eur, (rr.received_kg * rr.agreed_unit_cost_eur).round(2), atol=0.010001, rtol=0), 'Purchase receipt valuation')
    rr['month_id'] = pd.to_datetime(rr.receipt_date).dt.strftime('%Y-%m-01')
    receipts = rr.groupby(['month_id', 'material_id'])[['received_kg', 'receipt_value_eur']].sum()
    issues = actual.groupby(['month_id', 'material_id'])[['consumed_kg', 'issued_material_value_eur']].sum()
    require(len(inv) == 24 * len(m['materials']), 'Incomplete inventory coverage')
    ledger = inv.set_index(['month_id', 'material_id'])
    for totals, columns in [(receipts, ['received_kg', 'receipt_value_eur']), (issues, ['consumed_kg', 'issued_material_value_eur'])]:
        require(totals.index.isin(ledger.index).all(), 'Movement outside inventory periods')
        for col in columns:
            require(np.allclose(ledger[col], totals[col].reindex(ledger.index, fill_value=0), atol=0.00001, rtol=0), f'{col}: movement totals')
    require(np.allclose(inv.closing_kg, inv.opening_kg + inv.received_kg - inv.consumed_kg, atol=0.00001, rtol=0), 'Quantity reconciliation')
    receipt_additions = inv.landed_receipt_value_eur if component_schema else inv.receipt_value_eur
    require(np.allclose(inv.closing_value_eur, inv.opening_value_eur + receipt_additions - inv.issued_material_value_eur, atol=0.00001, rtol=0), 'Value reconciliation')
    avg = ((inv.opening_value_eur + receipt_additions) / (inv.opening_kg + inv.received_kg)).fillna(0)
    require(np.allclose(inv.weighted_average_unit_cost_eur, avg, atol=0.00000001, rtol=0), 'Weighted average cost')
    require(np.allclose(inv.issued_material_value_eur, (avg * inv.consumed_kg).round(2), atol=0.010001, rtol=0), 'Issue valuation')
    for _, rows in inv.sort_values('month_id').groupby('material_id'):
        for opening, closing in [('opening_kg', 'closing_kg'), ('opening_value_eur', 'closing_value_eur')]:
            require(np.allclose(rows[opening].iloc[1:], rows[closing].iloc[:-1], atol=0.00001, rtol=0), 'Inventory carry-forward')
    print('PASS: keys / referential integrity / BOM / production capacity')
    print('PASS: approved suppliers / receipt quantities, prices and lead times')
    print('PASS: inventory quantity / value / weighted-average costing / carry-forward / nonnegative balances')


def main(output_dir):
    """Generate, validate, exclusively export to staging, then validate readback."""
    target = output_directory(output_dir)
    hashes = {name: hashlib.sha256((target / f'{name}.csv').read_bytes()).hexdigest() for name in MASTER_NAMES}
    masters = load_masters(target)
    rng = np.random.default_rng(SEED)
    dates = pd.date_range('2024-01-01', '2025-12-01', freq='MS')
    months = pd.DataFrame([dict(month_id=d.date().isoformat(), year=d.year,
                                quarter=d.quarter, month_number=d.month,
                                days_in_month=calendar.monthrange(d.year, d.month)[1]) for d in dates])
    capacity, production, consumption = generate_production(masters, months, rng)
    consumption, orders, receipts, inventory = generate_material_flow(masters, months, production, consumption, rng)
    frames = dict(months=months, line_month_capacity=capacity, production=production,
                  material_consumption=consumption, purchase_order_lines=orders,
                  material_receipts=receipts, raw_material_inventory=inventory)
    validate(masters, frames)
    for name, frame in frames.items():
        write_csv(frame, name, target)
        print(f'{name}.csv: {len(frame):,} rows')
    validate(masters, {name: pd.read_csv(target / f'{name}.csv') for name in frames})
    require(all(hashlib.sha256((target / f'{name}.csv').read_bytes()).hexdigest() == digest
                for name, digest in hashes.items()), 'Master file changed')
    print(f'PASS: master files unchanged; fixed seed {SEED}')


if __name__ == '__main__':
    main(parse_output_directory())
