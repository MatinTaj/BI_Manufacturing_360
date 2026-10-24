"""Manufacturing 360 BI — Step 2: reproducible master data.
Run from any working directory: python scripts/02_generate_master_data.py --output-dir data/staging
Writes only to an explicit staging directory; processed data is never an output.
All data generated here is synthetic, not real company records.
"""
from pathlib import Path
import numpy as np
import pandas as pd

from pipeline_io import output_directory, parse_output_directory, write_csv

from economic_assumptions import (FAMILIES, VARIANT_SIZE, VARIANT_PRICE,
                                  LINE_FIXED_ACTIVITY, validate_activity_masters, validate_economic_assumptions)

ROOT = Path(__file__).resolve().parent.parent
OUT = ROOT / 'data' / 'processed'
SEED = 360


def validate_masters(frames):
    """Validate candidate masters in memory before any authorized export."""
    from importlib.util import spec_from_file_location, module_from_spec
    spec = spec_from_file_location('operations', ROOT / 'scripts/03_generate_operations.py')
    operations = module_from_spec(spec)
    spec.loader.exec_module(operations)
    operations.validate_masters(frames)
    validate_activity_masters(frames['products'], frames['production_lines'])
    prices = frames['products'].base_selling_price_eur.to_numpy(dtype=float)
    if not np.isfinite(prices).all() or (prices <= 0).any():
        raise ValueError('Selling prices must be finite and positive')


def build_masters(seed=SEED):
    """Pure in-memory construction. Importing this script never writes files."""
    validate_economic_assumptions()
    rng = np.random.default_rng(seed)

    # Stable product keys, names and line assignments; explicit engineering variants.
    product_types = list(FAMILIES)
    products = pd.DataFrame([
        {'product_id': f'P{i:03d}', 'product_name': f'{product_types[(i-1)//4]} {((i-1)%4)+1}',
         'category': product_types[(i-1)//4], 'line_id': f'L{(i-1)%3+1:02d}',
         'base_selling_price_eur': round(FAMILIES[product_types[(i-1)//4]]['price'] * VARIANT_PRICE[(i-1)%4], 2),
         'standard_labor_hours_per_attempt': round(FAMILIES[product_types[(i-1)//4]]['hours'] * VARIANT_SIZE[(i-1)%4], 4),
         'standard_energy_kwh_per_attempt': round(FAMILIES[product_types[(i-1)//4]]['kwh'] * VARIANT_SIZE[(i-1)%4], 4)}
        for i in range(1, 21)
    ])
    materials = pd.DataFrame([
        {'material_id': f'M{i:03d}', 'material_name': n, 'unit': 'kg',
         'base_unit_cost_eur': c}
        for i, (n, c) in enumerate([
            ('Steel', 2.8), ('Aluminium', 5.2), ('Copper', 8.1),
            ('Cast Iron', 2.3), ('Polymer', 3.4), ('Rubber', 4.0),
            ('Stainless Steel', 6.5), ('Composite', 9.2),
            ('Brass', 7.1), ('Industrial Resin', 5.8)
        ], start=1)
    ])
    suppliers = pd.DataFrame([
        {'supplier_id': f'S{i:03d}', 'supplier_name': f'Supplier {i:02d}',
         'lead_time_days': int(rng.integers(4, 22)),
         'on_time_delivery_target': 0.95}
        for i in range(1, 16)
    ])
    customers = pd.DataFrame([
        {'customer_id': f'C{i:03d}', 'customer_name': f'Industrial Customer {i:02d}',
         'segment': ['OEM', 'Tier 1', 'Aftermarket'][(i-1)%3]}
        for i in range(1, 26)
    ])
    lines = pd.DataFrame([
        {'line_id': f'L{i:02d}', 'line_name': f'Production Line {i}',
         'monthly_capacity_units': 6500,
         'support_labor_hours_per_month': LINE_FIXED_ACTIVITY[f'L{i:02d}'][0],
         'base_energy_kwh_per_month': LINE_FIXED_ACTIVITY[f'L{i:02d}'][1]}
        for i in range(1, 4)
    ])

    # Family-specific process inputs; larger variants require more material.
    bom_rows = []
    for number, product in enumerate(products.itertuples(index=False)):
        for mid, kg in FAMILIES[product.category]['bom'].items():
            bom_rows.append({'product_id': product.product_id, 'material_id': mid,
                             'quantity_kg_per_unit': round(kg * VARIANT_SIZE[number % 4], 3)})
    bom = pd.DataFrame(bom_rows)

    # Each raw material has at least one approved supplier.
    source_rows = []
    for mid in materials['material_id']:
        chosen = rng.choice(suppliers['supplier_id'].to_numpy(), size=3, replace=False)
        for sid in chosen:
            source_rows.append({'material_id': mid, 'supplier_id': sid})
    material_suppliers = pd.DataFrame(source_rows)

    frames = {
        'products': products, 'materials': materials, 'suppliers': suppliers,
        'customers': customers, 'production_lines': lines, 'bom': bom,
        'material_suppliers': material_suppliers,
    }
    validate_masters(frames)
    return frames


def main(output_dir):
    target = output_directory(output_dir)
    frames = build_masters()
    for name, frame in frames.items():
        write_csv(frame, name, target)
        print(f'{name:20s} {len(frame):>4} rows -> {target / (name + ".csv")}')
    validate_masters({name: pd.read_csv(target / f'{name}.csv') for name in frames})
    print('PASS: exported master-data keys, foreign keys, values and economic drivers')


if __name__ == '__main__':
    main(parse_output_directory())
