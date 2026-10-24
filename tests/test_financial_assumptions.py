"""Non-destructive Phase 1/2/3 tests. Never call generator main() entry points."""
import copy
import hashlib
import importlib.util
from pathlib import Path
import sys
import unittest
from unittest.mock import patch

import numpy as np
import pandas as pd

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / 'scripts'))
import economic_assumptions as economics


def load_script(name):
    spec = importlib.util.spec_from_file_location(name, ROOT / 'scripts' / f'{name}.py')
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def add_manual_component_ledgers(allocation, sales, inventory):
    """Upgrade old hand-built test quantities to the authoritative component schema."""
    from finished_goods_valuation import COMPONENTS, value_finished_goods_month, allocate_sales_cogs
    sales, inventory = sales.copy(), inventory.copy()
    source = allocation.set_index(['month_id', 'product_id'])
    for _, rows in inventory.sort_values('month_id').groupby('product_id'):
        opening_units, opening = 0, {c: 0. for c in COMPONENTS}
        for index, row in rows.iterrows():
            production = source.loc[(row.month_id, row.product_id)]
            ledger = value_finished_goods_month(opening_units, opening, production.good_units,
                {c: production[f'capitalized_{c}_cost_eur'] for c in COMPONENTS}, row.shipped_units)
            for col, value in ledger.items():
                inventory.loc[index, col] = value
            group = sales[(sales.month_id == row.month_id) & (sales.product_id == row.product_id)].sort_values('sales_line_id')
            for sale_index, values in zip(group.index, allocate_sales_cogs(ledger, group.units_shipped.tolist())):
                for col, value in values.items():
                    sales.loc[sale_index, col] = value
                sales.loc[sale_index, 'weighted_average_unit_cost_eur'] = ledger['weighted_average_unit_cost_eur']
            opening_units = ledger['closing_units']
            opening = {c: ledger[f'closing_{c}_value_eur'] for c in COMPONENTS}
    return sales, inventory


class FinancialAssumptionsTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.protected = {p: hashlib.sha256(p.read_bytes()).hexdigest()
                         for folder in ('data', 'sql', 'powerbi')
                         for p in (ROOT / folder).rglob('*') if p.is_file()}
        # CSV and filesystem output is forbidden even if a regression calls it.
        cls.export_guard = patch.object(pd.DataFrame, 'to_csv', side_effect=AssertionError('CSV write forbidden'))
        cls.mkdir_guard = patch.object(Path, 'mkdir', side_effect=AssertionError('Directory creation forbidden'))
        cls.export_guard.start()
        cls.mkdir_guard.start()
        cls.master = load_script('02_generate_master_data')
        cls.operations = load_script('03_generate_operations')
        cls.financials = load_script('04_generate_financials')

    @classmethod
    def tearDownClass(cls):
        cls.export_guard.stop()
        cls.mkdir_guard.stop()
        after = {p: hashlib.sha256(p.read_bytes()).hexdigest()
                 for folder in ('data', 'sql', 'powerbi')
                 for p in (ROOT / folder).rglob('*') if p.is_file()}
        if after != cls.protected:
            raise AssertionError('Protected data/SQL/Power BI files changed')

    def fixture(self):
        return dict(
            products=pd.DataFrame([
                dict(product_id='P001', line_id='L01', base_selling_price_eur=50.,
                     standard_labor_hours_per_attempt=.5, standard_energy_kwh_per_attempt=2.),
                dict(product_id='P002', line_id='L01', base_selling_price_eur=80.,
                     standard_labor_hours_per_attempt=1., standard_energy_kwh_per_attempt=4.)]),
            production_lines=pd.DataFrame([dict(line_id='L01', support_labor_hours_per_month=120.,
                                               base_energy_kwh_per_month=2400.)]),
            production=pd.DataFrame([
                dict(production_id='PR000001', month_id='2024-01-01', product_id='P001',
                     attempted_units=10, defective_units=1, good_units=9),
                dict(production_id='PR000002', month_id='2024-01-01', product_id='P002',
                     attempted_units=20, defective_units=2, good_units=18)]),
            line_month_capacity=pd.DataFrame([dict(month_id='2024-01-01', line_id='L01')]),
            material_consumption=pd.DataFrame([
                dict(production_id='PR000001', issued_material_value_eur=100.),
                dict(production_id='PR000002', issued_material_value_eur=200.)]),
            months=pd.DataFrame([dict(month_id='2024-01-01', days_in_month=31)]),
            customers=pd.DataFrame([dict(customer_id='C001', segment='OEM')]))

    def cost_fixture(self, inputs=None):
        inputs = self.fixture() if inputs is None else inputs
        return self.financials.generate_costs(inputs, np.random.default_rng(362))

    def test_master_import_and_build_are_write_free_and_repeatable(self):
        first, second = self.master.build_masters(), self.master.build_masters()
        for name in first:
            pd.testing.assert_frame_equal(first[name], second[name])
        self.assertEqual(first['products'].product_id.tolist(), [f'P{i:03d}' for i in range(1, 21)])
        self.assertEqual(first['products'].line_id.tolist(), [f'L{(i-1)%3+1:02d}' for i in range(1, 21)])
        for table, key in [('materials', 'material_id'), ('suppliers', 'supplier_id'),
                           ('customers', 'customer_id'), ('production_lines', 'line_id')]:
            old = pd.read_csv(ROOT / 'data/processed' / f'{table}.csv')
            self.assertEqual(first[table][key].tolist(), old[key].tolist())
        alternate = self.master.build_masters(seed=999)
        self.assertFalse(first['suppliers'].equals(alternate['suppliers']))

    def test_engineering_boms_and_prices_are_independent(self):
        original = self.master.build_masters()
        families = copy.deepcopy(economics.FAMILIES)
        families['Brake Assembly']['price'] *= 2
        with patch.dict(economics.FAMILIES, families):
            repriced = self.master.build_masters()
        pd.testing.assert_frame_equal(original['bom'], repriced['bom'])
        for col in economics.PRODUCT_DRIVERS:
            pd.testing.assert_series_equal(original['products'][col], repriced['products'][col])
        self.assertEqual(repriced['products'].iloc[0].base_selling_price_eur,
                         2 * original['products'].iloc[0].base_selling_price_eur)
        # A steel/cast-iron brake carrier, not a random mixture of all materials.
        brake = original['bom'].query('product_id == "P001"').set_index('material_id')
        self.assertEqual(set(brake.index), {'M001', 'M004', 'M005', 'M006'})
        self.assertAlmostEqual(brake.loc['M001', 'quantity_kg_per_unit'], 3.4)

    def test_reject_invalid_master_values_and_legacy_driver_schema(self):
        masters = self.master.build_masters()
        for table, column, invalid in [('products', 'base_selling_price_eur', -1),
                                       ('products', economics.PRODUCT_DRIVERS[0], float('inf')),
                                       ('production_lines', economics.LINE_DRIVERS[1], float('nan')),
                                       ('bom', 'quantity_kg_per_unit', 0)]:
            with self.subTest(table=table, column=column):
                changed = {name: frame.copy(deep=True) for name, frame in masters.items()}
                changed[table].loc[0, column] = invalid
                with self.assertRaises(ValueError):
                    self.master.validate_masters(changed)
        legacy = masters['products'].drop(columns=list(economics.PRODUCT_DRIVERS))
        with self.assertRaisesRegex(ValueError, 'coordinated regeneration'):
            economics.validate_activity_masters(legacy, masters['production_lines'])

    def test_reject_invalid_configuration(self):
        for name, value in [('LABOR_RATE_RANGE_EUR', (36, 32)),
                            ('ENERGY_TARIFF_RANGE_EUR', (0.1, float('inf'))),
                            ('SELLING_VARIABLE_RATE', 2.), ('VARIANT_SIZE', (1, 2))]:
            with self.subTest(name=name), patch.object(economics, name, value):
                with self.assertRaises(ValueError):
                    economics.validate_economic_assumptions()

    def test_hand_calculated_activity_and_cost_conservation(self):
        line, allocation = self.cost_fixture()
        row = line.iloc[0]
        # 10*.5 + 20*1 = 25 person-hours; 10*2 + 20*4 = 100 kWh.
        self.assertEqual(row.production_labor_hours, 25.)
        self.assertEqual(row.labor_hours, 145.)
        self.assertEqual(row.activity_energy_kwh, 100.)
        self.assertEqual(row.energy_kwh, 2500.)
        self.assertEqual(row.labor_cost_eur, round(145 * row.hourly_rate_eur, 2))
        self.assertEqual(row.energy_cost_eur, round(2500 * row.energy_tariff_eur, 2))
        for col in ('labor_cost_eur', 'energy_cost_eur', 'manufacturing_overhead_eur'):
            self.assertEqual(sum(map(self.financials.cents, allocation[col])), self.financials.cents(row[col]))
        self.assertAlmostEqual(allocation.total_manufacturing_cost_eur.sum(),
                               300 + row.total_conversion_cost_eur)
        self.assertAlmostEqual(allocation.capitalized_production_cost_eur.sum(),
                               allocation.total_manufacturing_cost_eur.sum())

    def test_mix_changes_activity_without_price_dependency(self):
        inputs = self.fixture()
        original, _ = self.cost_fixture(inputs)
        # Same total units, greater share of the labor/energy-intensive product.
        inputs['production']['attempted_units'] = [0, 30]
        changed, _ = self.cost_fixture(inputs)
        self.assertEqual(changed.iloc[0].production_labor_hours, 30.)
        self.assertEqual(changed.iloc[0].activity_energy_kwh, 120.)
        inputs = self.fixture()
        inputs['products']['base_selling_price_eur'] *= 10
        repriced, _ = self.cost_fixture(inputs)
        pd.testing.assert_frame_equal(original, repriced)

    def test_idle_and_zero_good_output_accounting(self):
        inputs = self.fixture()
        inputs['production'][['attempted_units', 'good_units', 'defective_units']] = 0
        inputs['material_consumption']['issued_material_value_eur'] = 0.
        lines, allocation = self.cost_fixture(inputs)
        self.assertEqual(lines.iloc[0].labor_hours, 120.)
        self.assertEqual(lines.iloc[0].energy_kwh, 2400.)
        self.assertEqual(lines.iloc[0].idle_cost_eur, lines.iloc[0].total_conversion_cost_eur)
        self.assertEqual(allocation.capitalized_production_cost_eur.sum(), 0.)
        inputs = self.fixture()
        inputs['production']['good_units'] = 0
        inputs['production']['defective_units'] = inputs['production'].attempted_units
        _, allocation = self.cost_fixture(inputs)
        pd.testing.assert_series_equal(allocation.production_loss_expense_eur,
                                       allocation.total_manufacturing_cost_eur, check_names=False)
        self.assertEqual(allocation.capitalized_production_cost_eur.sum(), 0.)

    def test_seeded_costs_are_repeatable(self):
        for first, second in zip(self.cost_fixture(), self.cost_fixture()):
            pd.testing.assert_frame_equal(first, second)

    def test_opex_resource_base_variable_response_and_zero_revenue(self):
        inputs = self.fixture()
        sales = pd.DataFrame([dict(month_id='2024-01-01', net_revenue_eur=100000.)])
        expenses = self.financials.generate_opex(inputs, sales).set_index('expense_category')
        self.assertEqual(expenses.loc['selling', 'amount_eur'], 28000.)
        self.assertEqual(expenses.loc['administration', 'amount_eur'], 38000.)
        self.assertEqual(expenses.loc['selling', 'variable_rate_pct'], 2.)
        sales.net_revenue_eur *= 2
        changed = self.financials.generate_opex(inputs, sales).set_index('expense_category')
        self.assertEqual(changed.loc['selling', 'amount_eur'] - expenses.loc['selling', 'amount_eur'], 2000.)
        self.assertEqual(changed.loc['administration', 'amount_eur'], 38000.)
        empty = self.financials.generate_opex(inputs, sales.iloc[:0]).set_index('expense_category')
        self.assertEqual(empty.loc['selling', 'amount_eur'], 26000.)

    def test_existing_reconciliation_validator_with_small_manual_ledgers(self):
        inputs = self.fixture()
        lines, allocation = self.cost_fixture(inputs)
        sales_rows, stock_rows = [], []
        for i, row in enumerate(allocation.itertuples(index=False)):
            price = [50., 80.][i]
            gross = row.good_units * price
            discount = round(gross * .05, 2)
            value = row.capitalized_production_cost_eur
            unit_cost = round(value / row.good_units, 8)
            sales_rows.append(dict(sales_line_id=f'SL{i:07d}', month_id=row.month_id,
                shipment_date='2024-01-31', product_id=row.product_id, customer_id='C001',
                requested_units=row.good_units, unfulfilled_units=0, units_shipped=row.good_units,
                list_unit_price_eur=price, discount_pct=5., gross_revenue_eur=gross,
                discount_amount_eur=discount, net_revenue_eur=gross-discount,
                weighted_average_unit_cost_eur=unit_cost, cogs_eur=value))
            stock_rows.append(dict(month_id=row.month_id, product_id=row.product_id,
                opening_units=0, good_production_units=row.good_units, demand_units=row.good_units,
                shipped_units=row.good_units, unfulfilled_units=0, closing_units=0,
                opening_value_eur=0., production_value_eur=value, cogs_eur=value,
                closing_value_eur=0., weighted_average_unit_cost_eur=unit_cost))
        sales = pd.DataFrame(sales_rows)
        sales, stock = add_manual_component_ledgers(allocation, sales, pd.DataFrame(stock_rows))
        frames = dict(zip(self.financials.OUTPUTS, (lines, allocation, sales, stock,
                      self.financials.generate_opex(inputs, sales))))
        self.financials.validate(inputs, frames)
        self.financials.run_validation_tests(inputs, frames)
        broken = {name: frame.copy(deep=True) for name, frame in frames.items()}
        broken['manufacturing_costs'].loc[0, 'production_labor_hours'] += 1
        with self.assertRaisesRegex(ValueError, 'Activity driver'):
            self.financials.validate(inputs, broken)
        self.assertLess(self.financials.profit_totals(frames)['operating_profit'], 0)

    def test_independent_labor_energy_and_fixed_pool_allocations(self):
        inputs = self.fixture()
        # Labor shares 5:20 = 1:4; energy shares 50:20 = 5:2, NOT unit shares 1:2.
        inputs['products']['standard_energy_kwh_per_attempt'] = [5., 1.]
        lines, allocation = self.cost_fixture(inputs)
        self.financials.validate_conversion_costs(inputs, lines, allocation)
        row, first = lines.iloc[0], allocation.iloc[0]
        # Independent two-way largest remainder oracle for a first share.
        def expected(pool, numerator, denominator):
            q1, r1 = divmod(pool * numerator, denominator)
            q2, r2 = divmod(pool * (denominator - numerator), denominator)
            return q1 + int(pool - q1 - q2 > 0 and r1 >= r2)
        for col in ('production_labor_cost_eur', 'support_labor_cost_eur', 'manufacturing_overhead_eur'):
            self.assertEqual(self.financials.cents(first[col]), expected(self.financials.cents(row[col]), 1, 5))
        for col in ('activity_energy_cost_eur', 'standby_energy_cost_eur'):
            self.assertEqual(self.financials.cents(first[col]), expected(self.financials.cents(row[col]), 5, 7))
        for frame in (lines, allocation):
            for row in frame.itertuples(index=False):
                self.assertEqual(self.financials.cents(row.labor_cost_eur),
                    self.financials.cents(row.production_labor_cost_eur) + self.financials.cents(row.support_labor_cost_eur))
                self.assertEqual(self.financials.cents(row.energy_cost_eur),
                    self.financials.cents(row.activity_energy_cost_eur) + self.financials.cents(row.standby_energy_cost_eur))

    def test_fractional_weights_and_cent_ties(self):
        split = self.financials.split_cents
        self.assertEqual(split(7, [.01, .02, .04]), [1, 2, 4])
        self.assertEqual(split(2, [.0001, .0001, .0001]), [1, 1, 0])
        self.assertEqual(split(1, [0, .5, .5]), [0, 1, 0])
        self.assertEqual(split(0, [.2, .8]), [0, 0])
        self.assertEqual(split(100, [0, 0]), [0, 0])
        for invalid in ([1, -1], [float('nan'), 1], [float('inf'), 1]):
            with self.assertRaises(ValueError):
                split(1, invalid)
        with self.assertRaises(ValueError):
            split(-1, [1, 2])

    def test_subhour_drivers_are_not_truncated(self):
        inputs = self.fixture()
        inputs['production'][['attempted_units', 'good_units']] = 1
        inputs['production']['defective_units'] = 0
        inputs['products']['standard_labor_hours_per_attempt'] = [.01, .04]
        lines, allocation = self.cost_fixture(inputs)
        self.financials.validate_conversion_costs(inputs, lines, allocation)
        # Both weights used to be truncated to zero by the old integer-only split.
        self.assertGreater(allocation.iloc[0].production_labor_cost_eur, 0)
        self.assertGreater(allocation.iloc[1].production_labor_cost_eur,
                           allocation.iloc[0].production_labor_cost_eur)

    def test_subpool_residual_cents_and_stable_production_id_ties(self):
        from types import SimpleNamespace
        batch = self.fixture()['production'].copy()
        batch['attempted_units'] = 1
        batch['standard_labor_hours_per_attempt'] = .005
        batch['standard_energy_kwh_per_attempt'] = .005
        line = SimpleNamespace(labor_cost_eur=.01, energy_cost_eur=.01, manufacturing_overhead_eur=.01,
                               production_labor_hours=.01, hourly_rate_eur=.5,
                               activity_energy_kwh=.01, energy_tariff_eur=.5)
        pools, shares, idle = self.financials.allocate_conversion(batch, line)
        # Rounding each variable/fixed half independently would create 2 cents.
        self.assertEqual(pools['production_labor_cost_eur'], 1)
        self.assertEqual(pools['support_labor_cost_eur'], 0)
        self.assertEqual(pools['activity_energy_cost_eur'], 1)
        self.assertEqual(pools['standby_energy_cost_eur'], 0)
        self.assertEqual(shares['labor_cost_eur'], [1, 0])
        self.assertEqual(shares['energy_cost_eur'], [1, 0])
        self.assertEqual(sum(idle.values()), 0)
        # Generate equal-activity batches in opposite input orders. Stable IDs
        # decide penny ties even when input CSV order changes.
        inputs = self.fixture()
        inputs['production'][['attempted_units', 'good_units']] = 1
        inputs['production']['defective_units'] = 0
        inputs['products']['standard_labor_hours_per_attempt'] = .5
        inputs['products']['standard_energy_kwh_per_attempt'] = 2.
        baseline = self.cost_fixture(inputs)
        inputs['production'] = inputs['production'].iloc[::-1]
        inputs['products'] = inputs['products'].iloc[::-1]
        for first, second in zip(baseline, self.cost_fixture(inputs)):
            pd.testing.assert_frame_equal(first, second)

    def test_fixed_pool_zero_driver_fallback_and_unassigned_variable_cost(self):
        from types import SimpleNamespace
        batch = self.fixture()['production'].copy()
        batch['standard_labor_hours_per_attempt'] = 0.
        batch['standard_energy_kwh_per_attempt'] = 0.
        # Defensive allocator case: zero standards remain invalid in master input.
        line = SimpleNamespace(labor_cost_eur=1., energy_cost_eur=1., manufacturing_overhead_eur=1.,
                               production_labor_hours=0., hourly_rate_eur=1.,
                               activity_energy_kwh=0., energy_tariff_eur=1.)
        pools, shares, idle = self.financials.allocate_conversion(batch, line)
        self.assertEqual(shares['support_labor_cost_eur'], [33, 67])
        self.assertEqual(shares['standby_energy_cost_eur'], [33, 67])
        self.assertEqual(shares['manufacturing_overhead_eur'], [33, 67])
        self.assertEqual(sum(idle.values()), 0)
        batch.attempted_units = 0
        _, shares, idle = self.financials.allocate_conversion(batch, line)
        self.assertEqual(sum(idle.values()), 300)
        self.assertTrue(all(sum(amounts) == 0 for amounts in shares.values()))
        # If an inconsistent external pool has variable cost but no activity,
        # that cost must be expensed, never lost or allocated using fixed fallback.
        line.production_labor_hours = .25
        _, shares, idle = self.financials.allocate_conversion(batch, line)
        self.assertEqual(idle['idle_labor_cost_eur'], 100)

    def test_row_permutation_is_reproducible_across_months_and_lines(self):
        inputs = self.fixture()
        second = inputs['production'].copy()
        second['month_id'] = '2024-02-01'
        second['production_id'] = ['PR000003', 'PR000004']
        inputs['production'] = pd.concat([inputs['production'], second], ignore_index=True)
        second_material = inputs['material_consumption'].copy()
        second_material['production_id'] = ['PR000003', 'PR000004']
        inputs['material_consumption'] = pd.concat([inputs['material_consumption'], second_material], ignore_index=True)
        fixed = inputs['production_lines'].copy()
        fixed['line_id'] = 'L02'
        inputs['production_lines'] = pd.concat([inputs['production_lines'], fixed], ignore_index=True)
        inputs['products'].loc[1, 'line_id'] = 'L02'
        inputs['line_month_capacity'] = pd.DataFrame([
            dict(month_id=month, line_id=line) for month in ('2024-01-01', '2024-02-01')
            for line in ('L01', 'L02')])
        baseline = self.cost_fixture(inputs)
        self.financials.validate_conversion_costs(inputs, *baseline)
        shuffled = {name: frame.sample(frac=1, random_state=7).reset_index(drop=True)
                    for name, frame in inputs.items()}
        for first, second in zip(baseline, self.cost_fixture(shuffled)):
            pd.testing.assert_frame_equal(first, second)

    def test_mixed_defects_expense_assigned_cost_without_charging_good_product(self):
        inputs = self.fixture()
        inputs['production'].loc[0, 'good_units'] = 0
        inputs['production'].loc[0, 'defective_units'] = 10
        lines, allocation = self.cost_fixture(inputs)
        self.financials.validate_conversion_costs(inputs, lines, allocation)
        lost, good = allocation.iloc[0], allocation.iloc[1]
        self.assertEqual(lost.capitalized_production_cost_eur, 0)
        self.assertEqual(lost.production_loss_expense_eur, lost.total_manufacturing_cost_eur)
        self.assertEqual(good.production_loss_expense_eur, 0)
        self.assertEqual(good.capitalized_production_cost_eur, good.total_manufacturing_cost_eur)
        self.assertEqual(lines.iloc[0].idle_cost_eur, 0)

    def test_zero_attempt_product_receives_no_conversion_cost(self):
        inputs = self.fixture()
        inputs['production'].loc[0, ['attempted_units', 'good_units', 'defective_units']] = 0
        inputs['material_consumption'].loc[0, 'issued_material_value_eur'] = 0.
        lines, allocation = self.cost_fixture(inputs)
        self.financials.validate_conversion_costs(inputs, lines, allocation)
        for col in self.financials.CONVERSION_COLUMNS + self.financials.SUBPOOL_COLUMNS:
            self.assertEqual(allocation.iloc[0][col], 0)
        self.assertEqual(allocation.iloc[1].labor_cost_eur, lines.iloc[0].labor_cost_eur)

    def test_line_with_no_production_records_expenses_all_conversion(self):
        inputs = self.fixture()
        inputs['production'] = inputs['production'].iloc[:0]
        inputs['material_consumption'] = inputs['material_consumption'].iloc[:0]
        lines, allocation = self.cost_fixture(inputs)
        self.assertTrue(allocation.empty)
        self.financials.validate_conversion_costs(inputs, lines, allocation)
        self.assertEqual(lines.iloc[0].idle_cost_eur, lines.iloc[0].total_conversion_cost_eur)

    def test_conversion_validator_rejects_misallocation_and_unbalanced_pools(self):
        inputs = self.fixture()
        lines, allocation = self.cost_fixture(inputs)
        # Total is conserved but the product split is wrong.
        wrong = allocation.copy()
        wrong.loc[0, 'support_labor_cost_eur'] += .01
        wrong.loc[1, 'support_labor_cost_eur'] -= .01
        with self.assertRaisesRegex(ValueError, 'Activity-based allocation'):
            self.financials.validate_conversion_costs(inputs, lines, wrong)
        for col in ('idle_cost_eur', 'production_labor_cost_eur', 'total_conversion_cost_eur'):
            with self.subTest(col=col):
                wrong_line = lines.copy()
                wrong_line.loc[0, col] += .01
                with self.assertRaises(ValueError):
                    self.financials.validate_conversion_costs(inputs, wrong_line, allocation)

    def test_monthly_weighted_average_inventory_carry_is_preserved(self):
        from decimal import Decimal, ROUND_HALF_UP
        inputs = self.fixture()
        production2 = inputs['production'].copy()
        production2['month_id'] = '2024-02-01'
        production2['production_id'] = ['PR000003', 'PR000004']
        inputs['production'] = pd.concat([inputs['production'], production2], ignore_index=True)
        issues2 = inputs['material_consumption'].copy()
        issues2['production_id'] = ['PR000003', 'PR000004']
        issues2['issued_material_value_eur'] *= 2  # changed new-production unit cost
        inputs['material_consumption'] = pd.concat([inputs['material_consumption'], issues2], ignore_index=True)
        inputs['months'] = pd.DataFrame([dict(month_id='2024-01-01', days_in_month=31),
                                        dict(month_id='2024-02-01', days_in_month=29)])
        inputs['line_month_capacity'] = pd.DataFrame([dict(month_id=month, line_id='L01')
                                                     for month in inputs['months'].month_id])
        lines, allocation = self.cost_fixture(inputs)
        sales_rows, inventory_rows = [], []
        opening = {}
        for row in allocation.itertuples(index=False):
            units, value = opening.get(row.product_id, (0, 0))
            new_value = self.financials.cents(row.capitalized_production_cost_eur)
            available_units, available_cents = units + row.good_units, value + new_value
            shipped = row.good_units // 2 if row.month_id == '2024-01-01' else row.good_units
            # Independent manual monthly weighted-average valuation.
            cogs = int((Decimal(available_cents) * shipped / available_units).quantize(Decimal('1'), rounding=ROUND_HALF_UP))
            closing_units, closing_cents = available_units-shipped, available_cents-cogs
            unit_cost = round(available_cents / 100 / available_units, 8)
            price = 50. if row.product_id == 'P001' else 80.
            gross = shipped * price
            discount = round(gross * .05, 2)
            sales_rows.append(dict(sales_line_id=f'SL{len(sales_rows):07d}', month_id=row.month_id,
                shipment_date='2024-01-31' if row.month_id == '2024-01-01' else '2024-02-29',
                product_id=row.product_id, customer_id='C001', requested_units=shipped,
                unfulfilled_units=0, units_shipped=shipped, list_unit_price_eur=price,
                discount_pct=5., gross_revenue_eur=gross, discount_amount_eur=discount,
                net_revenue_eur=gross-discount, weighted_average_unit_cost_eur=unit_cost, cogs_eur=cogs/100))
            inventory_rows.append(dict(month_id=row.month_id, product_id=row.product_id,
                opening_units=units, good_production_units=row.good_units, demand_units=shipped,
                shipped_units=shipped, unfulfilled_units=0, closing_units=closing_units,
                opening_value_eur=value/100, production_value_eur=new_value/100,
                cogs_eur=cogs/100, closing_value_eur=closing_cents/100, weighted_average_unit_cost_eur=unit_cost))
            opening[row.product_id] = closing_units, closing_cents
        sales, inventory = add_manual_component_ledgers(allocation, pd.DataFrame(sales_rows), pd.DataFrame(inventory_rows))
        frames = dict(zip(self.financials.OUTPUTS, (lines, allocation, sales, inventory,
                      self.financials.generate_opex(inputs, sales))))
        self.financials.validate(inputs, frames)
        self.assertGreater(inventory.query('month_id == "2024-02-01"').opening_value_eur.sum(), 0)
        self.assertEqual(sum(map(self.financials.cents, allocation.capitalized_production_cost_eur)),
                         sum(map(self.financials.cents, sales.cogs_eur)) +
                         sum(map(self.financials.cents, inventory.query('month_id == "2024-02-01"').closing_value_eur)))

    def test_legacy_operational_data_still_passes_read_only_checks(self):
        masters = self.operations.load_masters()
        names = ('months', 'line_month_capacity', 'production', 'material_consumption',
                 'purchase_order_lines', 'material_receipts', 'raw_material_inventory')
        operations = {name: pd.read_csv(ROOT / 'data/processed' / f'{name}.csv') for name in names}
        self.operations.validate(masters, operations)


if __name__ == '__main__':
    unittest.main()
