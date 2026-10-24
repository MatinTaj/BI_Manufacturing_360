"""Phase 2: synthetic financials for the existing 2024--2025 operations.

Run from anywhere: python scripts/04_generate_financials.py --output-dir data/staging
Five financial outputs are created exclusively in the explicit staging directory.
Existing files and processed data are never overwritten. Seed: 362.

Policy: EUR, one warehouse, zero opening finished goods, no WIP/returns/VAT.
Monthly receipts and completion precede month-end shipments (not daily stock).
Labor/energy: product-specific engineering drivers plus line fixed activity.
Rates and resource assumptions are centralized in economic_assumptions.py.
Overhead: EUR 22k--28k/line/month (maintenance, rent, depreciation).
Labor/support/overhead use standard-hour shares; activity/standby energy use
standard-kWh shares. Fixed pools fall back to attempts only with zero activity.
Normal downtime/unused capacity is absorbed by production. A line with zero attempts expenses all its costs as
idle cost, rather than capitalizing them. Zero-good-output batches expense
their entire assigned cost. Such expenses are separate from selling/admin.
Defective-unit costs are absorbed by the good units from the same batch.
Selling prices follow master base prices, 0.15% monthly escalation and +/-2%
variation; discounts: OEM 5--10%, Tier 1 3--7%, Aftermarket 0--3%.
Demand is based on each product's average good monthly output, product effects,
seasonality, modest growth and noise, independently of available stock.
Unfulfilled demand is lost, not revenue or a backlog. Each product/month has
4--7 customer requests; sales contains only fulfilled requests, with requested
and unfulfilled quantities on those rows. Completely unfulfilled requests are
not retained. No minimum margin or artificially generated profit is imposed.
Monthly periodic weighted-average FG costing includes opening value and new
capitalized production cost. Integer cents and largest-remainder allocations
keep line costs, sales COGS and inventory exactly reconciled. Rates/unit costs
are informational; cent rounding can differ from their displayed products.
Selling expense = EUR 26k/month plus 2% revenue; administration = EUR 38k/month
with modest escalation. External outbound freight is a separate shipment-based
selling/distribution expense, excluded from manufacturing and selling/admin pools.
Profit is derived, never randomized. No budgets.
"""

from pathlib import Path
from decimal import Decimal, ROUND_HALF_UP
import hashlib
import importlib.util
from types import SimpleNamespace

import numpy as np
import pandas as pd

from pipeline_io import output_directory, parse_output_directory, write_csv

from finished_goods_valuation import (
    COMPONENTS, COMPONENT_COSTS, CAPITALIZED_COLUMNS, LOSS_COLUMNS,
    PRODUCTION_COLUMNS, COGS_COLUMNS, INVENTORY_COLUMNS,
    booked_cents, value_finished_goods_month, allocate_sales_cogs,
)

from economic_assumptions import (
    MONTHLY_ESCALATION, LABOR_RATE_RANGE_EUR, ENERGY_TARIFF_RANGE_EUR,
    OVERHEAD_RANGE_EUR, SELLING_FIXED_EUR, ADMIN_FIXED_EUR, SELLING_VARIABLE_RATE,
    PRODUCT_DRIVERS, validate_activity_masters, line_activity, validate_economic_assumptions,
    outbound_freight_rate, validate_outbound_freight_assumptions,
)

ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT / 'data' / 'processed'
OUTPUTS = ('manufacturing_costs', 'production_cost_allocation', 'sales',
           'finished_goods_inventory', 'operating_expenses')
SEED = 362


def require(ok, message):
    if not bool(ok):
        raise ValueError(message)


def cents(value):
    """Round a euro amount to integer cents, using commercial rounding."""
    return int((Decimal(str(value)) * 100).quantize(Decimal('1'), rounding=ROUND_HALF_UP))


def split_cents(total, weights):
    """Largest remainder in exact integer arithmetic, retaining fractional drivers.

    Ties use input order; conversion callers sort by stable production_id.
    Zero-weight pools return zeros; the caller must expense the unassigned pool.
    Existing integer shipment splits retain their original behavior.
    """
    require(int(total) == total and total >= 0, 'Invalid cent pool')
    total = int(total)
    decimal_weights = [Decimal(str(x)) for x in weights]
    require(all(w.is_finite() and w >= 0 for w in decimal_weights), 'Invalid allocation weight')
    scale = 10 ** max([0] + [-w.as_tuple().exponent for w in decimal_weights])
    weights = [int(w * scale) for w in decimal_weights]
    denominator = sum(weights)
    if not denominator:
        return [0] * len(weights)
    shares = [total * w // denominator for w in weights]
    order = sorted(range(len(weights)), key=lambda i: (-(total * weights[i] % denominator), i))
    for i in order[:total - sum(shares)]:
        shares[i] += 1
    return shares


CONVERSION_COLUMNS = ('labor_cost_eur', 'energy_cost_eur', 'manufacturing_overhead_eur')
SUBPOOL_COLUMNS = ('production_labor_cost_eur', 'support_labor_cost_eur',
                   'activity_energy_cost_eur', 'standby_energy_cost_eur')
IDLE_COLUMNS = ('idle_labor_cost_eur', 'idle_energy_cost_eur', 'idle_overhead_cost_eur')


def allocate_conversion(batch, line):
    """Return line pools, product shares and idle amounts, all in integer cents.

    Input batch must be in production_id order. Weights use exact decimal
    attempted-unit x standard-activity products, not rounded line totals.
    Aggregate labor/energy totals remain authoritative; support/standby receive
    the residual after rounding production/activity subpools.
    """
    require(batch.production_id.tolist() == sorted(batch.production_id)
            and not batch.production_id.duplicated().any(), 'Allocation batch must have unique sorted production IDs')
    attempts = [Decimal(str(v)) for v in batch.attempted_units]
    require(all(v.is_finite() and v >= 0 and v == int(v) for v in attempts),
            'Invalid attempted units')
    hours = [n * Decimal(str(v)) for n, v in zip(attempts, batch.standard_labor_hours_per_attempt)]
    kwh = [n * Decimal(str(v)) for n, v in zip(attempts, batch.standard_energy_kwh_per_attempt)]
    require(all(v.is_finite() and v >= 0 for v in hours + kwh), 'Invalid activity weights')
    labor, energy, overhead = [cents(getattr(line, col)) for col in CONVERSION_COLUMNS]
    production = cents(Decimal(str(line.production_labor_hours)) * Decimal(str(line.hourly_rate_eur)))
    activity = cents(Decimal(str(line.activity_energy_kwh)) * Decimal(str(line.energy_tariff_eur)))
    require(0 <= production <= labor and 0 <= activity <= energy, 'Invalid conversion subpool')
    pools = dict(zip(SUBPOOL_COLUMNS, (production, labor - production, activity, energy - activity)))
    pools['manufacturing_overhead_eur'] = overhead
    hour_fixed = hours if sum(hours) else attempts
    energy_fixed = kwh if sum(kwh) else attempts
    drivers = (hours, hour_fixed, kwh, energy_fixed, hour_fixed)
    shares = {col: split_cents(pools[col], weights) for col, weights in zip(pools, drivers)}
    shares['labor_cost_eur'] = [a + b for a, b in zip(shares[SUBPOOL_COLUMNS[0]], shares[SUBPOOL_COLUMNS[1]])]
    shares['energy_cost_eur'] = [a + b for a, b in zip(shares[SUBPOOL_COLUMNS[2]], shares[SUBPOOL_COLUMNS[3]])]
    idle = {name: pool - sum(shares[col]) for name, pool, col in
            zip(IDLE_COLUMNS, (labor, energy, overhead), CONVERSION_COLUMNS)}
    return pools, shares, idle


def validate_conversion_costs(inputs, line, alloc):
    """Reconcile activity allocations and each line pool including idle/loss costs."""
    validate_economic_assumptions()
    validate_activity_masters(inputs['products'], inputs['production_lines'])
    source = inputs['production'].merge(
        inputs['products'][['product_id', 'line_id', *PRODUCT_DRIVERS]],
        on='product_id', validate='many_to_one')
    fixed_lines = inputs['production_lines'].set_index('line_id')
    require(not line.duplicated(['month_id', 'line_id']).any(), 'Duplicate conversion pool')
    actual_keys = set(map(tuple, line[['month_id', 'line_id']].to_numpy()))
    expected_keys = set(map(tuple, inputs['line_month_capacity'][['month_id', 'line_id']].to_numpy()))
    require(actual_keys == expected_keys, 'Conversion pool coverage')
    require(not alloc.production_id.duplicated().any(), 'Duplicate production allocation')
    require(set(alloc.production_id) == set(source.production_id), 'Conversion production coverage')
    conversion = list(CONVERSION_COLUMNS)
    for row in line.itertuples(index=False):
        batch = source[(source.month_id == row.month_id) & (source.line_id == row.line_id)].sort_values('production_id')
        group = alloc[(alloc.month_id == row.month_id) & (alloc.line_id == row.line_id)].sort_values('production_id')
        require(group.production_id.tolist() == batch.production_id.tolist(), 'Conversion assignment keys')
        require(row.attempted_units == batch.attempted_units.sum(), 'Line attempts')
        for col in ('attempted_units', 'good_units'):
            close(group[col], batch[col], f'Conversion source {col}')
        for name, value in line_activity(batch, fixed_lines.loc[row.line_id]).items():
            close(getattr(row, name), value, f'Activity driver: {name}')
        close(row.labor_cost_eur, cents(row.labor_hours * row.hourly_rate_eur) / 100, 'Labor formula')
        close(row.energy_cost_eur, cents(row.energy_kwh * row.energy_tariff_eur) / 100, 'Energy formula')
        pools, shares, idle = allocate_conversion(batch, row)
        for col in SUBPOOL_COLUMNS:
            close(getattr(row, col), pools[col] / 100, f'Line subpool: {col}')
        for col, amounts in shares.items():
            require(list(map(cents, group[col])) == amounts, f'Activity-based allocation: {col}')
        for col, amount in idle.items():
            close(getattr(row, col), amount / 100, f'Idle component: {col}')
        require(cents(row.idle_cost_eur) == sum(idle.values()), 'Idle total')
        require(cents(row.total_conversion_cost_eur) == sum(cents(getattr(row, col)) for col in conversion), 'Conversion total')
        for cost_col, idle_col in zip(conversion, IDLE_COLUMNS):
            require(cents(getattr(row, cost_col)) == sum(map(cents, group[cost_col])) + idle[idle_col],
                    f'Conversion pool conservation: {cost_col}')
        for item in group.itertuples(index=False):
            total = cents(item.material_cost_eur) + sum(cents(getattr(item, col)) for col in conversion)
            require(cents(item.total_manufacturing_cost_eur) == total, 'Manufacturing cents')
            require(cents(item.capitalized_production_cost_eur) == (total if item.good_units else 0), 'Capitalized cents')
            require(cents(item.production_loss_expense_eur) == (0 if item.good_units else total), 'Loss cents')
        # Loss expenses already contain their conversion share: never add them to
        # the allocated pool again. This identity includes materials exactly once.
        source_total = sum(cents(getattr(row, col)) for col in conversion) + sum(map(cents, group.material_cost_eur))
        recognized = sum(map(cents, group.capitalized_production_cost_eur)) + sum(map(cents, group.production_loss_expense_eur)) + sum(idle.values())
        require(source_total == recognized, 'Capitalization/loss/idle conservation')


def material_issue_components(consumption):
    """Use Phase 4 lineage; fully legacy purchase-only issues remain supported."""
    columns = ('issued_purchase_material_value_eur', 'issued_inbound_freight_eur')
    present = set(columns) & set(consumption.columns)
    require(not present or set(columns).issubset(consumption.columns), 'Incomplete material issue component schema')
    result = consumption.copy()
    if not present:
        result[columns[0]] = result.issued_material_value_eur
        result[columns[1]] = 0.
    for row in result.itertuples(index=False):
        require(booked_cents(row.issued_material_value_eur) ==
                booked_cents(getattr(row, columns[0])) + booked_cents(getattr(row, columns[1])),
                'Landed material issues do not equal purchase plus freight')
    return result.groupby('production_id')[[*columns, 'issued_material_value_eur']].sum()


def validate_production_components(inputs, alloc):
    require(set(PRODUCTION_COLUMNS).issubset(alloc.columns), 'Incomplete production component schema')
    issues = material_issue_components(inputs['material_consumption'])
    for row in alloc.itertuples(index=False):
        source = issues.loc[row.production_id] if row.production_id in issues.index else None
        purchase = booked_cents(source.issued_purchase_material_value_eur) if source is not None else 0
        freight = booked_cents(source.issued_inbound_freight_eur) if source is not None else 0
        require(booked_cents(row.purchase_material_cost_eur) == purchase, 'Purchase-material source')
        require(booked_cents(row.inbound_freight_cost_eur) == freight, 'Inbound-freight source')
        require(booked_cents(row.material_cost_eur) == purchase + freight, 'Landed material aggregate')
        values = {c: booked_cents(getattr(row, col)) for c, col in COMPONENT_COSTS.items()}
        require(booked_cents(row.total_manufacturing_cost_eur) == sum(values.values()), 'Five-component manufacturing total')
        for c, value in values.items():
            require(booked_cents(getattr(row, f'capitalized_{c}_cost_eur')) == (value if row.good_units else 0),
                    f'Capitalized component: {c}')
            require(booked_cents(getattr(row, f'{c}_production_loss_expense_eur')) == (0 if row.good_units else value),
                    f'Production loss component: {c}')
        require(booked_cents(row.capitalized_production_cost_eur) == sum(booked_cents(getattr(row, col)) for col in CAPITALIZED_COLUMNS), 'Capitalized component total')
        require(booked_cents(row.production_loss_expense_eur) == sum(booked_cents(getattr(row, col)) for col in LOSS_COLUMNS), 'Production loss component total')


def has_finished_goods_schema(alloc, sales, inventory):
    schemas = ((alloc, PRODUCTION_COLUMNS), (sales, COGS_COLUMNS), (inventory, INVENTORY_COLUMNS))
    if not any(set(columns) & set(frame.columns) for frame, columns in schemas):
        return False
    for frame, columns in schemas:
        require(set(columns).issubset(frame.columns), 'Incomplete finished-goods component schema')
    return True


def validate_finished_goods_components(inputs, alloc, sales, inventory):
    """Exact component source, valuation, sales allocation and carry-forward checks."""
    require(has_finished_goods_schema(alloc, sales, inventory), 'Missing finished-goods component schema')
    validate_production_components(inputs, alloc)
    require(not alloc.duplicated(['month_id', 'product_id']).any(), 'Duplicate component production grain')
    require(not inventory.duplicated(['month_id', 'product_id']).any(), 'Duplicate component inventory grain')
    require(not sales.sales_line_id.duplicated().any(), 'Duplicate component sales ID')
    source = alloc.set_index(['month_id', 'product_id'])
    keys = set(map(tuple, inventory[['month_id', 'product_id']].to_numpy()))
    require(keys == set(source.index), 'Component inventory/production coverage')
    require(set(map(tuple, sales[['month_id', 'product_id']].to_numpy())).issubset(keys), 'Component sale outside inventory')
    for _, group in inventory.sort_values('month_id').groupby('product_id'):
        opening_units = 0
        opening = {c: 0. for c in COMPONENTS}
        for row in group.itertuples(index=False):
            production = source.loc[(row.month_id, row.product_id)]
            require(row.opening_units == opening_units and row.good_production_units == production.good_units,
                    'Component inventory source units')
            expected = value_finished_goods_month(opening_units, opening, production.good_units,
                {c: production[f'capitalized_{c}_cost_eur'] for c in COMPONENTS}, row.shipped_units)
            for col, value in expected.items():
                if col.endswith('_units'):
                    require(getattr(row, col) == value, f'Component inventory units: {col}')
                elif col == 'weighted_average_unit_cost_eur':
                    close(getattr(row, col), value, 'Component weighted average', .0000000051)
                else:
                    require(booked_cents(getattr(row, col)) == booked_cents(value), f'Finished-goods component: {col}')
            product_sales = sales[(sales.month_id == row.month_id) & (sales.product_id == row.product_id)].sort_values('sales_line_id')
            expected_sales = allocate_sales_cogs(expected, product_sales.units_shipped.tolist())
            for actual, values in zip(product_sales.itertuples(index=False), expected_sales):
                for col, value in values.items():
                    require(booked_cents(getattr(actual, col)) == booked_cents(value), f'Sales component allocation: {col}')
            opening_units = expected['closing_units']
            opening = {c: expected[f'closing_{c}_value_eur'] for c in COMPONENTS}


def load_inputs(input_dir=OUT):
    """Read all master/operational CSVs and reuse Phase 1's read-only checks."""
    spec = importlib.util.spec_from_file_location('phase1', ROOT / 'scripts/03_generate_operations.py')
    phase1 = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(phase1)
    masters = phase1.load_masters(input_dir)
    names = ('months', 'line_month_capacity', 'production', 'material_consumption',
             'purchase_order_lines', 'material_receipts', 'raw_material_inventory')
    operations = {n: pd.read_csv(Path(input_dir) / f'{n}.csv') for n in names}
    phase1.validate(masters, operations)
    return {**masters, **operations}


def generate_costs(inputs, rng):
    """Create line costs and assign them to products without duplicating materials."""
    validate_economic_assumptions()
    validate_activity_masters(inputs['products'], inputs['production_lines'])
    fixed_lines = inputs['production_lines'].set_index('line_id')
    production = inputs['production'].merge(
        inputs['products'][['product_id', 'line_id', *PRODUCT_DRIVERS]], on='product_id', validate='many_to_one')
    material_components = material_issue_components(inputs['material_consumption'])
    material = material_components.issued_material_value_eur
    lines, allocations = [], []
    for cap in inputs['line_month_capacity'].sort_values(['month_id', 'line_id']).itertuples(index=False):
        batch = production[(production.month_id == cap.month_id) & (production.line_id == cap.line_id)].sort_values('production_id')
        attempted = int(batch.attempted_units.sum())
        elapsed = (pd.Timestamp(cap.month_id).year - 2024) * 12 + pd.Timestamp(cap.month_id).month - 1
        activity = line_activity(batch, fixed_lines.loc[cap.line_id])
        hours, kwh = activity['labor_hours'], activity['energy_kwh']
        rate = round(rng.uniform(*LABOR_RATE_RANGE_EUR) * (1 + elapsed * MONTHLY_ESCALATION), 2)
        tariff = round(rng.uniform(*ENERGY_TARIFF_RANGE_EUR), 4)
        costs = [cents(hours * rate), cents(kwh * tariff),
                 cents(rng.uniform(*OVERHEAD_RANGE_EUR) * (1 + elapsed * MONTHLY_ESCALATION))]
        names = ('labor_cost_eur', 'energy_cost_eur', 'manufacturing_overhead_eur')
        line_record = dict(month_id=cap.month_id, line_id=cap.line_id, attempted_units=attempted,
                          labor_hours=hours, hourly_rate_eur=rate, energy_kwh=kwh, energy_tariff_eur=tariff,
                          **{n: v / 100 for n, v in zip(names, costs)},
                          total_conversion_cost_eur=sum(costs) / 100,
                          idle_cost_eur=sum(costs) / 100 if attempted == 0 else 0.0,
                          **{key: value for key, value in activity.items()
                             if key not in ('labor_hours', 'energy_kwh')})
        pools, assigned, idle = allocate_conversion(batch, SimpleNamespace(**line_record))
        line_record.update({col: pools[col] / 100 for col in SUBPOOL_COLUMNS})
        line_record.update({col: value / 100 for col, value in idle.items()})
        line_record['idle_cost_eur'] = sum(idle.values()) / 100
        lines.append(line_record)
        shares = [assigned[col] for col in names]
        for i, p in enumerate(batch.itertuples(index=False)):
            mat = cents(material.get(p.production_id, 0))
            purchase = cents(material_components.loc[p.production_id, 'issued_purchase_material_value_eur']) if p.production_id in material_components.index else 0
            freight = cents(material_components.loc[p.production_id, 'issued_inbound_freight_eur']) if p.production_id in material_components.index else 0
            component_values = dict(material=purchase, inbound_freight=freight,
                                    labor=shares[0][i], energy=shares[1][i], overhead=shares[2][i])
            total = sum(component_values.values())
            allocations.append(dict(production_id=p.production_id, month_id=p.month_id,
                                    product_id=p.product_id, line_id=p.line_id,
                                    attempted_units=p.attempted_units, good_units=p.good_units,
                                    material_cost_eur=mat / 100,
                                    **{n: s[i] / 100 for n, s in zip(names, shares)},
                                    total_manufacturing_cost_eur=total / 100,
                                    capitalized_production_cost_eur=total / 100 if p.good_units else 0.0,
                                    production_loss_expense_eur=0.0 if p.good_units else total / 100,
                                    good_unit_manufacturing_cost_eur=round(total / 100 / p.good_units, 8) if p.good_units else 0.0,
                                    **{col: assigned[col][i] / 100 for col in SUBPOOL_COLUMNS},
                                    purchase_material_cost_eur=purchase/100, inbound_freight_cost_eur=freight/100,
                                    **{f'capitalized_{c}_cost_eur': (value/100 if p.good_units else 0.) for c, value in component_values.items()},
                                    **{f'{c}_production_loss_expense_eur': (0. if p.good_units else value/100) for c, value in component_values.items()}))
    allocation_columns = [
        'production_id', 'month_id', 'product_id', 'line_id', 'attempted_units', 'good_units',
        'material_cost_eur', *CONVERSION_COLUMNS, 'total_manufacturing_cost_eur',
        'capitalized_production_cost_eur', 'production_loss_expense_eur',
        'good_unit_manufacturing_cost_eur', *SUBPOOL_COLUMNS, *PRODUCTION_COLUMNS]
    allocation_frame = pd.DataFrame(allocations, columns=allocation_columns)
    validate_production_components(inputs, allocation_frame)
    return pd.DataFrame(lines), allocation_frame


OUTBOUND_COLUMNS = ('outbound_freight_rate_eur_per_unit', 'outbound_freight_eur')


def has_outbound_schema(sales):
    present = set(OUTBOUND_COLUMNS) & set(sales.columns)
    require(not present or set(OUTBOUND_COLUMNS).issubset(sales.columns), 'Incomplete outbound freight schema')
    return bool(present)


def outbound_freight_amount(shipped_units, rate):
    """Commercial rounding on actual shipment units; no minimum shipment charge."""
    quantity, tariff = Decimal(str(shipped_units)), Decimal(str(rate))
    require(quantity.is_finite() and quantity >= 0 and quantity == quantity.to_integral_value(),
            'Invalid outbound shipped units')
    require(tariff.is_finite() and tariff >= 0, 'Invalid outbound freight rate')
    return cents(quantity * tariff) / 100


def validate_operating_financials(inputs, frames):
    """Enforce freight ownership, explicit opex components and company P&L."""
    sales, expenses = frames['sales'], frames['operating_expenses']
    freight_schema = has_outbound_schema(sales)
    if freight_schema:
        validate_outbound_freight_assumptions()
        customers = inputs['customers'].set_index('customer_id')
        for row in sales.itertuples(index=False):
            expected_rate = outbound_freight_rate(customers.at[row.customer_id, 'segment'], row.customer_id, row.month_id)
            close(row.outbound_freight_rate_eur_per_unit, expected_rate, 'Outbound freight segment rate', .000000001)
            require(booked_cents(row.outbound_freight_eur) ==
                    cents(outbound_freight_amount(row.units_shipped, expected_rate)), 'Outbound freight shipment amount')
    for name, frame in frames.items():
        if name != 'sales':
            require(not set(OUTBOUND_COLUMNS) & set(frame.columns), f'Outbound freight belongs only in sales: {name}')
    require(set(expenses.expense_category).issubset({'selling', 'administration'}),
            'Operating expense category must be selling or administration; freight is sales-owned')
    expected = generate_opex(inputs, sales).set_index(['month_id', 'expense_category']).sort_index()
    actual = expenses.set_index(['month_id', 'expense_category']).sort_index()
    require(actual.index.equals(expected.index), 'Operating expense classification/coverage')
    for col in ('amount_eur', 'fixed_amount_eur', 'variable_rate_pct', 'variable_driver_amount_eur'):
        close(actual[col], expected[col], f'Operating expense formula: {col}')
    if 'variable_amount_eur' in actual:
        close(actual.variable_amount_eur, expected.variable_amount_eur, 'Explicit variable operating expense')
        for row in expenses.itertuples(index=False):
            require(booked_cents(row.amount_eur) == booked_cents(row.fixed_amount_eur) + booked_cents(row.variable_amount_eur),
                    'Fixed plus variable operating expense')
    totals = profit_totals(frames)
    monthly = [profit_totals({name: frame[frame.month_id == month] for name, frame in frames.items()})
               for month in inputs['months'].month_id]
    for key, value in totals.items():
        require(value == sum(row[key] for row in monthly), f'Company/month P&L: {key}')


def generate_sales_inventory(inputs, allocation, rng):
    """Fulfill demand from stock and carry unsold units and their costs forward."""
    validate_production_components(inputs, allocation)
    validate_outbound_freight_assumptions()
    sales, inventory = [], []
    customers = inputs['customers'].sort_values('customer_id').set_index('customer_id')
    average_output = inputs['production'].groupby('product_id').good_units.mean()
    for product in inputs['products'].sort_values('product_id').itertuples(index=False):
        opening_units = 0
        opening_components = {c: 0. for c in COMPONENTS}
        demand_effect = rng.uniform(.94, 1.08)
        batches = allocation[allocation.product_id == product.product_id].sort_values('month_id')
        for elapsed, p in enumerate(batches.itertuples(index=False)):
            date = pd.Timestamp(p.month_id)
            season = .80 if date.month in (8, 12) else 1.02
            demand = max(1, int(average_output[product.product_id] * demand_effect * season
                                * (1 + .002 * elapsed) * rng.uniform(.85, 1.15)))
            available_units = opening_units + int(p.good_units)
            fulfilled = min(demand, available_units)
            ledger = value_finished_goods_month(opening_units, opening_components, p.good_units,
                {c: getattr(p, f'capitalized_{c}_cost_eur') for c in COMPONENTS}, fulfilled)
            count = int(rng.integers(4, 8))
            chosen = rng.choice(customers.index.to_numpy(), count, replace=False)
            requests = rng.multinomial(demand, np.ones(count) / count)
            shipped, remaining = [], fulfilled
            for request in requests:
                quantity = min(int(request), remaining)
                shipped.append(quantity)
                remaining -= quantity
            component_cogs = allocate_sales_cogs(ledger, shipped)
            average_cost = ledger['weighted_average_unit_cost_eur']
            for customer, request, quantity, costs in zip(chosen, requests, shipped, component_cogs):
                if quantity == 0:
                    continue
                segment = customers.at[customer, 'segment']
                low, high = {'OEM': (5, 10), 'Tier 1': (3, 7), 'Aftermarket': (0, 3)}[segment]
                discount = round(float(rng.uniform(low, high)), 2)
                price = round(product.base_selling_price_eur * (1 + MONTHLY_ESCALATION * elapsed) * rng.uniform(.98, 1.02), 2)
                gross = quantity * cents(price)
                reduction = int((Decimal(gross) * Decimal(str(discount)) / 100).quantize(Decimal('1'), rounding=ROUND_HALF_UP))
                freight_rate = outbound_freight_rate(segment, customer, p.month_id)
                sales.append(dict(sales_line_id=f'SL{len(sales) + 1:07d}', month_id=p.month_id,
                                  shipment_date=date.date().replace(day=int(inputs['months'].set_index('month_id').at[p.month_id, 'days_in_month'])).isoformat(),
                                  product_id=product.product_id, customer_id=customer,
                                  requested_units=int(request), unfulfilled_units=int(request) - quantity,
                                  units_shipped=quantity, list_unit_price_eur=price, discount_pct=discount,
                                  gross_revenue_eur=gross / 100, discount_amount_eur=reduction / 100,
                                  net_revenue_eur=(gross - reduction) / 100,
                                  weighted_average_unit_cost_eur=round(average_cost, 8), **costs,
                                  outbound_freight_rate_eur_per_unit=freight_rate,
                                  outbound_freight_eur=outbound_freight_amount(quantity, freight_rate)))
            inventory.append(dict(month_id=p.month_id, product_id=product.product_id,
                opening_units=ledger['opening_units'], good_production_units=p.good_units,
                demand_units=demand, shipped_units=fulfilled, unfulfilled_units=demand-fulfilled,
                closing_units=ledger['closing_units'], opening_value_eur=ledger['opening_value_eur'],
                production_value_eur=ledger['production_value_eur'], cogs_eur=ledger['cogs_eur'],
                closing_value_eur=ledger['closing_value_eur'], weighted_average_unit_cost_eur=average_cost,
                **{col: ledger[col] for col in INVENTORY_COLUMNS}))
            opening_units = ledger['closing_units']
            opening_components = {c: ledger[f'closing_{c}_value_eur'] for c in COMPONENTS}
    sales_columns = ['sales_line_id', 'month_id', 'shipment_date', 'product_id', 'customer_id',
        'requested_units', 'unfulfilled_units', 'units_shipped', 'list_unit_price_eur', 'discount_pct',
        'gross_revenue_eur', 'discount_amount_eur', 'net_revenue_eur', 'weighted_average_unit_cost_eur',
        'cogs_eur', *COGS_COLUMNS, *OUTBOUND_COLUMNS]
    sales_frame = pd.DataFrame(sales, columns=sales_columns)
    if sales_frame.empty:
        for col in sales_columns:
            if col.endswith('_units') or col == 'units_shipped':
                sales_frame[col] = sales_frame[col].astype('int64')
            elif col.endswith('_eur') or col == 'discount_pct' or col in OUTBOUND_COLUMNS:
                sales_frame[col] = sales_frame[col].astype('float64')
    return sales_frame, pd.DataFrame(inventory)


def generate_opex(inputs, sales):
    """Calculate selling/admin costs using a fixed base and revenue driver."""
    validate_economic_assumptions()
    revenue = sales.groupby('month_id').net_revenue_eur.sum()
    rows = []
    for i, month in enumerate(sorted(inputs['months'].month_id)):
        escalation = 1 + MONTHLY_ESCALATION * i
        for category, fixed, variable_rate in [('selling', SELLING_FIXED_EUR, SELLING_VARIABLE_RATE),
                                                ('administration', ADMIN_FIXED_EUR, 0.0)]:
            fixed_amount = cents(fixed * escalation) / 100
            driver = float(revenue.get(month, 0)) if variable_rate else 0.0
            variable_amount = cents(driver * variable_rate) / 100
            rows.append(dict(month_id=month, expense_category=category,
                             amount_eur=(cents(fixed_amount) + cents(variable_amount)) / 100,
                             fixed_amount_eur=fixed_amount, variable_rate_pct=variable_rate * 100,
                             variable_driver_amount_eur=driver, variable_amount_eur=variable_amount))
    return pd.DataFrame(rows)


def close(actual, expected, message, tolerance=.00001):
    require(np.allclose(actual, expected, atol=tolerance, rtol=0), message)


def validate(inputs, frames):
    """Recompute financial identities from source records and exported facts."""
    line, alloc, sales, inv, expenses = (frames[n] for n in OUTPUTS)
    component_schema = has_finished_goods_schema(alloc, sales, inv)
    keys = (['month_id', 'line_id'], ['production_id'], ['sales_line_id'],
            ['month_id', 'product_id'], ['month_id', 'expense_category'])
    for name, frame, key in zip(OUTPUTS, frames.values(), keys):
        require(not frame.isna().any().any() and not frame.duplicated(key).any(), f'{name}: null/duplicate')
        numeric = frame.select_dtypes(include='number')
        require(np.isfinite(numeric.to_numpy()).all() and (numeric >= 0).all().all(), f'{name}: negative/nonfinite')
        require(frame.month_id.isin(inputs['months'].month_id).all(), f'{name}: month FK')
        for col, parent in [('product_id', 'products'), ('customer_id', 'customers'), ('line_id', 'production_lines'), ('production_id', 'production')]:
            if col in frame:
                require(frame[col].isin(inputs[parent][col]).all(), f'{name}: {col} FK')
        for col in frame:
            if col.endswith('_units'):
                close(frame[col], np.floor(frame[col]), f'{name}: noninteger units')
    require(len(line) == len(inputs['line_month_capacity']) and len(alloc) == len(inputs['production']), 'Cost coverage')
    require(len(inv) == len(inputs['months']) * len(inputs['products']), 'FG coverage')
    source = inputs['production'].merge(inputs['products'][['product_id', 'line_id']], on='product_id').set_index('production_id').sort_index()
    actual = alloc.set_index('production_id').sort_index()
    require(actual.index.equals(source.index), 'Allocation production coverage')
    for col in ['month_id', 'product_id', 'line_id', 'attempted_units', 'good_units']:
        require((actual[col] == source[col]).all(), f'Allocation source {col}')
    material = inputs['material_consumption'].groupby('production_id').issued_material_value_eur.sum()
    close(actual.material_cost_eur, material.reindex(actual.index, fill_value=0), 'Material source cost')
    validate_conversion_costs(inputs, line, alloc)
    if component_schema:
        validate_finished_goods_components(inputs, alloc, sales, inv)
    conversion = list(CONVERSION_COLUMNS)
    close(alloc.total_manufacturing_cost_eur, alloc.material_cost_eur + alloc[conversion].sum(axis=1), 'Manufacturing total')
    close(alloc.total_manufacturing_cost_eur, alloc.capitalized_production_cost_eur + alloc.production_loss_expense_eur, 'Capitalization')
    close(alloc.good_unit_manufacturing_cost_eur, (alloc.total_manufacturing_cost_eur / alloc.good_units.replace(0, np.nan)).fillna(0), 'Good unit cost')
    require((alloc.loc[alloc.good_units == 0, 'capitalized_production_cost_eur'] == 0).all(), 'Zero output capitalization')
    require((alloc.loc[alloc.good_units > 0, 'production_loss_expense_eur'] == 0).all(), 'Unexpected production loss')
    stock = inv.set_index(['month_id', 'product_id']).sort_index()
    ac = alloc.set_index(['month_id', 'product_id']).sort_index()
    require(stock.index.equals(ac.index), 'Inventory production coverage')
    close(stock.good_production_units, ac.good_units, 'FG source quantity')
    close(stock.production_value_eur, ac.capitalized_production_cost_eur, 'FG source value')
    close(inv.closing_units, inv.opening_units + inv.good_production_units - inv.shipped_units, 'FG quantity reconciliation')
    close(inv.closing_value_eur, inv.opening_value_eur + inv.production_value_eur - inv.cogs_eur, 'FG value reconciliation')
    close(inv.shipped_units, np.minimum(inv.demand_units, inv.opening_units + inv.good_production_units), 'Demand fulfillment')
    close(inv.unfulfilled_units, inv.demand_units - inv.shipped_units, 'Unfulfilled demand')
    available = inv.opening_units + inv.good_production_units
    average = ((inv.opening_value_eur + inv.production_value_eur) / available.replace(0, np.nan)).fillna(0)
    close(inv.weighted_average_unit_cost_eur, average, 'FG weighted average', .00000001)
    if not component_schema:
        for row, avg in zip(inv.itertuples(index=False), average):
            close(row.cogs_eur, cents(avg * row.shipped_units) / 100, 'Monthly weighted average COGS')
    for _, group in inv.sort_values('month_id').groupby('product_id'):
        require(group.iloc[0].opening_units == 0 and group.iloc[0].opening_value_eur == 0, 'Opening FG')
        close(group.opening_units.iloc[1:], group.closing_units.iloc[:-1], 'FG quantity carry')
        close(group.opening_value_eur.iloc[1:], group.closing_value_eur.iloc[:-1], 'FG value carry')
    totals = sales.groupby(['month_id', 'product_id'])[['units_shipped', 'cogs_eur']].sum()
    require(totals.index.isin(stock.index).all(), 'Sales period/product FK')
    close(stock.shipped_units, totals.units_shipped.reindex(stock.index, fill_value=0), 'Sales quantity ledger')
    close(stock.cogs_eur, totals.cogs_eur.reindex(stock.index, fill_value=0), 'Sales COGS ledger')
    require((sales.units_shipped > 0).all() and (sales.discount_pct <= 100).all(), 'Invalid sale')
    close(sales.requested_units, sales.units_shipped + sales.unfulfilled_units, 'Request quantity')
    dates = pd.to_datetime(sales.shipment_date)
    require((dates.dt.strftime('%Y-%m-01') == sales.month_id).all() and dates.dt.is_month_end.all(), 'Shipment dates')
    close(sales.gross_revenue_eur, sales.units_shipped * sales.list_unit_price_eur, 'Gross revenue')
    expected_discount = [cents(Decimal(str(g)) * Decimal(str(d)) / 100) / 100 for g, d in zip(sales.gross_revenue_eur, sales.discount_pct)]
    close(sales.discount_amount_eur, expected_discount, 'Discount calculation')
    close(sales.net_revenue_eur, sales.gross_revenue_eur - sales.discount_amount_eur, 'Net revenue')
    customer_segments = inputs['customers'].set_index('customer_id').segment
    base_prices = inputs['products'].set_index('product_id').base_selling_price_eur
    for sale in sales.itertuples(index=False):
        low, high = {'OEM': (5, 10), 'Tier 1': (3, 7), 'Aftermarket': (0, 3)}[customer_segments[sale.customer_id]]
        require(low <= sale.discount_pct <= high, 'Segment discount policy')
        date = pd.Timestamp(sale.month_id)
        elapsed = (date.year - 2024) * 12 + date.month - 1
        base = base_prices[sale.product_id] * (1 + MONTHLY_ESCALATION * elapsed)
        require(base * .98 - .005001 <= sale.list_unit_price_eur <= base * 1.02 + .005001, 'Pricing policy')
    for key, group in sales.groupby(['month_id', 'product_id'], sort=False):
        average = stock.loc[key, 'weighted_average_unit_cost_eur']
        close(group.weighted_average_unit_cost_eur, average, 'Sales unit cost')
        if not component_schema:
            close(group.cogs_eur, np.array(split_cents(cents(stock.loc[key, 'cogs_eur']), group.units_shipped)) / 100, 'Sales COGS allocation')
    validate_operating_financials(inputs, frames)
    print('PASS: keys/FKs, source quantities/material costs, activity-based allocations, idle costs')
    print('PASS: demand/shipments, prices/revenue/discounts, weighted-average COGS')
    print('PASS: FG quantity/value/carry-forward, nonnegative balances, operating expenses')


def profit_totals(frames):
    """Company P&L in integer cents; aggregate aliases are informational only.

    Fully pre-Phase-6 sales have no freight fields and retain legacy zero freight.
    Reject partial schemas, duplicate facts and freight recorded outside sales.
    """
    sales, expenses = frames['sales'], frames['operating_expenses']
    require(not sales.sales_line_id.duplicated().any(), 'Duplicate sale in company P&L')
    require(not expenses.duplicated(['month_id', 'expense_category']).any(), 'Duplicate operating expense in P&L')
    require(set(expenses.expense_category).issubset({'selling', 'administration'}),
            'Operating expense category must be selling or administration; freight is sales-owned')
    for name, frame in frames.items():
        if name != 'sales':
            require(not set(OUTBOUND_COLUMNS) & set(frame.columns), f'Outbound freight belongs only in sales: {name}')
    revenue = sum(map(cents, sales.net_revenue_eur))
    cogs = sum(map(booked_cents, sales.cogs_eur))
    outbound = sum(map(booked_cents, sales.outbound_freight_eur)) if has_outbound_schema(sales) else 0
    selling = sum(map(booked_cents, expenses.loc[expenses.expense_category == 'selling', 'amount_eur']))
    administration = sum(map(booked_cents, expenses.loc[expenses.expense_category == 'administration', 'amount_eur']))
    idle = sum(map(booked_cents, frames['manufacturing_costs'].idle_cost_eur))
    loss = sum(map(booked_cents, frames['production_cost_allocation'].production_loss_expense_eur))
    return dict(revenue=revenue, cogs=cogs, gross_profit=revenue - cogs,
                outbound_freight=outbound, selling_expenses=selling, administrative_expenses=administration,
                selling_admin_expenses=selling + administration, idle_cost=idle, production_loss=loss,
                separately_expensed_production_costs=idle + loss,
                operating_profit=revenue - cogs - outbound - selling - administration - idle - loss)


def run_validation_tests(inputs, frames):
    """Exercise failure detection and zero-output accounting without file writes."""
    from contextlib import redirect_stdout
    from io import StringIO
    mutations = [('sales', 'customer_id', 'INVALID'),
                 ('sales', 'net_revenue_eur', 0),
                 ('production_cost_allocation', 'labor_cost_eur', 0),
                 ('finished_goods_inventory', 'closing_units', -1),
                 ('finished_goods_inventory', 'closing_value_eur', 1)]
    for table, column, value in mutations:
        changed = {n: f.copy(deep=True) for n, f in frames.items()}
        changed[table].loc[0, column] = value
        try:
            with redirect_stdout(StringIO()):
                validate(inputs, changed)
        except ValueError:
            pass
        else:
            raise ValueError(f'Negative test accepted: {table}.{column}')
    require(split_cents(2, [1, 1, 1]) == [1, 1, 0], 'Cent residual test')
    edge = {n: f.copy(deep=True) for n, f in inputs.items()}
    edge['production'][['attempted_units', 'defective_units', 'good_units']] = 0
    for col in ('issued_material_value_eur', 'issued_purchase_material_value_eur', 'issued_inbound_freight_eur'):
        if col in edge['material_consumption']:
            edge['material_consumption'][col] = 0
    idle_lines, idle_alloc = generate_costs(edge, np.random.default_rng(SEED))
    close(idle_lines.idle_cost_eur, idle_lines.total_conversion_cost_eur, 'Idle line expense test')
    close(idle_alloc.capitalized_production_cost_eur, 0, 'Idle capitalization test')
    edge = {n: f.copy(deep=True) for n, f in inputs.items()}
    edge['production']['good_units'] = 0
    edge['production']['defective_units'] = edge['production'].attempted_units
    _, lost = generate_costs(edge, np.random.default_rng(SEED))
    close(lost.production_loss_expense_eur, lost.total_manufacturing_cost_eur, 'Zero good output expense test')
    close(lost.capitalized_production_cost_eur, 0, 'Zero good output capitalization test')
    print('PASS: five deliberate invalid-data tests; cent residual, idle-line and zero-good-output tests')


def main(output_dir):
    """Read staging inputs, validate, exclusively export, then validate readback."""
    target = output_directory(output_dir)
    protected = [p for p in target.glob('*.csv') if p.stem not in OUTPUTS] + list((ROOT / 'scripts').glob('*.py'))
    hashes = {p: hashlib.sha256(p.read_bytes()).hexdigest() for p in protected}
    inputs = load_inputs(target)
    rng = np.random.default_rng(SEED)
    line, allocation = generate_costs(inputs, rng)
    sales, stock = generate_sales_inventory(inputs, allocation, rng)
    frames = dict(zip(OUTPUTS, (line, allocation, sales, stock, generate_opex(inputs, sales))))
    validate(inputs, frames)
    for name, frame in frames.items():
        write_csv(frame, name, target)
        print(f'{name}.csv: {len(frame):,} rows')
    exported = {n: pd.read_csv(target / f'{n}.csv') for n in OUTPUTS}
    validate(inputs, exported)
    run_validation_tests(inputs, exported)
    require(all(hashlib.sha256(p.read_bytes()).hexdigest() == h for p, h in hashes.items()), 'Existing input file changed')
    print('PASS: existing master, operational, raw data and scripts unchanged')
    pnl = profit_totals(exported)
    for name in ('revenue', 'cogs', 'gross_profit', 'outbound_freight', 'selling_expenses',
                 'administrative_expenses', 'idle_cost', 'production_loss', 'operating_profit'):
        print(f'{name}: EUR {pnl[name] / 100:,.2f}')


if __name__ == '__main__':
    main(parse_output_directory())
