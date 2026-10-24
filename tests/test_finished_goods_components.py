"""Phase 5: five-component valuation, integration and mutation regressions.

Only small in-memory fixtures are used; no generator main() is called.
"""
import hashlib
from pathlib import Path
import unittest
from unittest.mock import patch

import numpy as np
import pandas as pd
import test_financial_assumptions as baseline
import finished_goods_valuation as fg


class FinishedGoodsComponentTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.before = cls.hashes()
        cls.export_guard = patch.object(pd.DataFrame, 'to_csv', side_effect=AssertionError('CSV export forbidden'))
        cls.mkdir_guard = patch.object(Path, 'mkdir', side_effect=AssertionError('mkdir forbidden'))
        cls.export_guard.start()
        cls.mkdir_guard.start()
        cls.financials = baseline.load_script('04_generate_financials')

    @classmethod
    def hashes(cls):
        return {p: hashlib.sha256(p.read_bytes()).hexdigest()
            for folder in ('data', 'sql', 'powerbi')
            for p in (baseline.ROOT / folder).rglob('*') if p.is_file()}

    @classmethod
    def tearDownClass(cls):
        cls.export_guard.stop()
        cls.mkdir_guard.stop()
        if cls.hashes() != cls.before:
            raise AssertionError('Protected files changed')

    def values(self, *amounts):
        return dict(zip(fg.COMPONENTS, amounts or (0.,)*5))

    def fixture(self, months=2, zero=False):
        inputs = baseline.FinancialAssumptionsTests.fixture(self)
        consumption = inputs['material_consumption']
        consumption['issued_inbound_freight_eur'] = [5., 10.]
        consumption['issued_purchase_material_value_eur'] = consumption.issued_material_value_eur - consumption.issued_inbound_freight_eur
        inputs['customers'] = pd.DataFrame([dict(customer_id=f'C{i:03d}', segment='OEM') for i in range(1, 9)])
        if months == 2:
            second = inputs['production'].copy()
            second['month_id'] = '2024-02-01'
            second['production_id'] = ['PR000003', 'PR000004']
            inputs['production'] = pd.concat([inputs['production'], second], ignore_index=True)
            issues = consumption.copy()
            issues['production_id'] = ['PR000003', 'PR000004']
            issues[['issued_material_value_eur', 'issued_purchase_material_value_eur', 'issued_inbound_freight_eur']] *= 1.5
            inputs['material_consumption'] = pd.concat([consumption, issues], ignore_index=True)
            inputs['months'] = pd.DataFrame([dict(month_id='2024-01-01', days_in_month=31), dict(month_id='2024-02-01', days_in_month=29)])
            inputs['line_month_capacity'] = pd.DataFrame([dict(month_id=month, line_id='L01') for month in inputs['months'].month_id])
        if zero:
            inputs['production'][['attempted_units', 'good_units', 'defective_units']] = 0
            inputs['material_consumption'][['issued_material_value_eur', 'issued_purchase_material_value_eur', 'issued_inbound_freight_eur']] = 0.
        return inputs

    def mini_financials(self, inputs):
        rng = np.random.default_rng(362)
        line, allocation = self.financials.generate_costs(inputs, rng)
        sales, inventory = self.financials.generate_sales_inventory(inputs, allocation, rng)
        return dict(zip(self.financials.OUTPUTS, (line, allocation, sales, inventory,
                    self.financials.generate_opex(inputs, sales))))

    def test_hand_calculated_five_component_month_and_carry(self):
        row = fg.value_finished_goods_month(10, self.values(20, 2, 10, 2, 6),
                                            10, self.values(40, 4, 30, 6, 10), 5)
        self.assertEqual([row[col] for col in fg.COGS_COLUMNS], [15., 1.5, 10., 2., 4.])
        self.assertEqual(row['cogs_eur'], 32.5)
        self.assertEqual(row['closing_value_eur'], 97.5)
        self.assertEqual(row['weighted_average_unit_cost_eur'], 6.5)
        next_row = fg.value_finished_goods_month(15,
            {c: row[f'closing_{c}_value_eur'] for c in fg.COMPONENTS}, 0, self.values(), 15)
        self.assertEqual(next_row['cogs_eur'], 97.5)
        self.assertEqual(next_row['closing_value_eur'], 0)
        self.assertTrue(all(next_row[f'closing_{c}_value_eur'] == 0 for c in fg.COMPONENTS))

    def test_component_rounding_is_authoritative_not_aggregate_rounding(self):
        row = fg.value_finished_goods_month(0, self.values(), 2, self.values(*([.01]*5)), 1)
        self.assertEqual(row['cogs_eur'], .05)  # aggregate-only half-up would be .03
        self.assertEqual(row['closing_value_eur'], 0.)
        self.assertEqual(row['closing_units'], 1)
        for c in fg.COMPONENTS:
            self.assertEqual(row[f'{c}_cogs_eur'], .01)

    def test_customer_cogs_largest_remainder_and_zero_shipment_rows(self):
        row = fg.value_finished_goods_month(0, self.values(), 3, self.values(.01, .02, .03, .04, .05), 3)
        rows = fg.allocate_sales_cogs(row, [1, 0, 1, 1])
        self.assertEqual([r['material_cogs_eur'] for r in rows], [.01, 0, 0, 0])
        self.assertEqual(rows[1]['cogs_eur'], 0)
        for col in fg.COGS_COLUMNS:
            self.assertEqual(sum(map(fg.booked_cents, [r[col] for r in rows])), fg.booked_cents(row[col]))
        self.assertTrue(all(fg.booked_cents(r['cogs_eur']) == sum(fg.booked_cents(r[col]) for col in fg.COGS_COLUMNS) for r in rows))

    def test_zero_stock_zero_shipments_and_invalid_inputs(self):
        row = fg.value_finished_goods_month(0, self.values(), 0, self.values(), 0)
        self.assertEqual(row['weighted_average_unit_cost_eur'], 0)
        self.assertEqual(fg.allocate_sales_cogs(row, []), [])
        row = fg.value_finished_goods_month(10, self.values(20, 2, 10, 2, 6), 0, self.values(), 0)
        self.assertEqual(row['closing_value_eur'], 40)
        self.assertEqual(row['cogs_eur'], 0)
        for units in (-1, .5, float('inf'), float('nan')):
            with self.assertRaises(ValueError):
                fg.value_finished_goods_month(units, self.values(), 0, self.values(), 0)
        with self.assertRaises(ValueError):
            fg.value_finished_goods_month(0, self.values(1, 0, 0, 0, 0), 0, self.values(), 0)
        with self.assertRaises(ValueError):
            fg.value_finished_goods_month(1, self.values(), 0, self.values(), 2)
        with self.assertRaises(ValueError):
            fg.value_finished_goods_month(0, self.values(), 0, self.values(1, 0, 0, 0, 0), 0)
        with self.assertRaises(ValueError):
            fg.value_finished_goods_month(1, self.values(.005, 0, 0, 0, 0), 0, self.values(), 0)
        with self.assertRaises(ValueError):
            fg.allocate_sales_cogs(row, [1])

    def test_end_to_end_small_fixture_five_component_reconciliations(self):
        inputs = self.fixture()
        frames = self.mini_financials(inputs)
        self.financials.validate(inputs, frames)
        allocation, sales, inventory = (frames[k] for k in ('production_cost_allocation', 'sales', 'finished_goods_inventory'))
        for row in allocation.itertuples(index=False):
            self.assertEqual(fg.booked_cents(row.material_cost_eur), fg.booked_cents(row.purchase_material_cost_eur) + fg.booked_cents(row.inbound_freight_cost_eur))
            self.assertEqual(fg.booked_cents(row.total_manufacturing_cost_eur), sum(fg.booked_cents(getattr(row, col)) for col in fg.COMPONENT_COSTS.values()))
        for c in fg.COMPONENTS:
            self.assertEqual(sum(map(fg.booked_cents, inventory[f'{c}_cogs_eur'])), sum(map(fg.booked_cents, sales[f'{c}_cogs_eur'])))
            self.assertEqual(sum(map(fg.booked_cents, allocation[f'capitalized_{c}_cost_eur'])),
                sum(map(fg.booked_cents, sales[f'{c}_cogs_eur'])) +
                sum(map(fg.booked_cents, inventory.query('month_id == "2024-02-01"')[f'closing_{c}_value_eur'])))
        self.assertGreater(sales.inbound_freight_cogs_eur.sum(), 0)

    def test_all_zero_production_has_no_sales_and_only_idle_expenses(self):
        inputs = self.fixture(zero=True)
        frames = self.mini_financials(inputs)
        self.financials.validate(inputs, frames)
        self.assertTrue(frames['sales'].empty)
        self.assertEqual(frames['finished_goods_inventory'].closing_value_eur.sum(), 0)
        self.assertGreater(frames['manufacturing_costs'].idle_cost_eur.sum(), 0)

    def test_fully_defective_batches_expense_each_component(self):
        inputs = self.fixture()
        inputs['production']['good_units'] = 0
        inputs['production']['defective_units'] = inputs['production'].attempted_units
        frames = self.mini_financials(inputs)
        self.financials.validate(inputs, frames)
        allocation = frames['production_cost_allocation']
        for c, col in fg.COMPONENT_COSTS.items():
            self.assertEqual(allocation[f'capitalized_{c}_cost_eur'].sum(), 0)
            pd.testing.assert_series_equal(allocation[f'{c}_production_loss_expense_eur'], allocation[col], check_names=False)
        self.assertTrue(frames['sales'].empty)
        self.assertGreater(allocation.production_loss_expense_eur.sum(), 0)
        self.assertEqual(frames['manufacturing_costs'].idle_cost_eur.sum(), 0)

    def test_defective_new_batch_can_ship_opening_stock_without_capitalizing_loss(self):
        inputs = self.fixture()
        second = inputs['production'].month_id == '2024-02-01'
        inputs['production'].loc[second, 'good_units'] = 0
        inputs['production'].loc[second, 'defective_units'] = inputs['production'].loc[second, 'attempted_units']
        line, allocation = self.financials.generate_costs(inputs, np.random.default_rng(362))
        # Deterministic hand-selected shipments deliberately leave opening stock.
        inventory, sales, opening = [], [], {}
        for row in allocation.itertuples(index=False):
            units, values = opening.get(row.product_id, (0, self.values()))
            ship = row.good_units // 2 if row.month_id == '2024-01-01' else units
            ledger = fg.value_finished_goods_month(units, values, row.good_units,
                {c: getattr(row, f'capitalized_{c}_cost_eur') for c in fg.COMPONENTS}, ship)
            inventory.append(dict(month_id=row.month_id, product_id=row.product_id, **ledger))
            if ship:
                sales.append(dict(sales_line_id=f'SL{len(sales):07d}', month_id=row.month_id,
                    product_id=row.product_id, units_shipped=ship, **fg.allocate_sales_cogs(ledger, [ship])[0]))
            opening[row.product_id] = ledger['closing_units'], {c: ledger[f'closing_{c}_value_eur'] for c in fg.COMPONENTS}
        inventory, sales = pd.DataFrame(inventory), pd.DataFrame(sales)
        self.financials.validate_finished_goods_components(inputs, allocation, sales, inventory)
        self.assertEqual(inventory.query('month_id == "2024-02-01"').production_value_eur.sum(), 0)
        self.assertGreater(inventory.query('month_id == "2024-02-01"').cogs_eur.sum(), 0)
        self.assertGreater(allocation.query('month_id == "2024-02-01"').production_loss_expense_eur.sum(), 0)

    def test_reproducibility_under_input_and_sales_row_reordering(self):
        inputs = self.fixture()
        frames = self.mini_financials(inputs)
        shuffled = {name: frame.iloc[::-1].reset_index(drop=True) for name, frame in inputs.items()}
        repeated = self.mini_financials(shuffled)
        for name in frames:
            pd.testing.assert_frame_equal(frames[name], repeated[name])
        frames['sales'] = frames['sales'].iloc[::-1]
        self.financials.validate(inputs, frames)

    def test_reject_partial_schemas_and_material_double_counting(self):
        inputs = self.fixture()
        frames = self.mini_financials(inputs)
        changed = {name: frame.copy() for name, frame in frames.items()}
        changed['sales'] = changed['sales'].drop(columns=['inbound_freight_cogs_eur'])
        with self.assertRaisesRegex(ValueError, 'Incomplete finished-goods'):
            self.financials.validate(inputs, changed)
        inputs['material_consumption'] = inputs['material_consumption'].drop(columns=['issued_inbound_freight_eur'])
        with self.assertRaisesRegex(ValueError, 'Incomplete material issue'):
            self.financials.generate_costs(inputs, np.random.default_rng(362))
        inputs = self.fixture()
        inputs['material_consumption'].loc[0, 'issued_material_value_eur'] += 5.
        with self.assertRaisesRegex(ValueError, 'Landed material issues'):
            self.financials.generate_costs(inputs, np.random.default_rng(362))

    def test_detect_component_corruption_even_when_aggregate_is_unchanged(self):
        inputs = self.fixture()
        frames = self.mini_financials(inputs)
        mutations = [('production_cost_allocation', 'purchase_material_cost_eur'),
            ('production_cost_allocation', 'capitalized_inbound_freight_cost_eur'),
            ('production_cost_allocation', 'labor_production_loss_expense_eur'),
            ('finished_goods_inventory', 'opening_energy_value_eur'),
            ('finished_goods_inventory', 'production_material_value_eur'),
            ('finished_goods_inventory', 'closing_overhead_value_eur'),
            ('sales', 'material_cogs_eur'), ('sales', 'cogs_eur')]
        for table, column in mutations:
            with self.subTest(table=table, column=column):
                changed = {name: frame.copy(deep=True) for name, frame in frames.items()}
                changed[table].loc[0, column] += .01
                with self.assertRaises(ValueError):
                    self.financials.validate(inputs, changed)


if __name__ == '__main__':
    unittest.main()
