"""Phase 4 tests: pure valuation and tiny in-memory material-flow fixtures only."""
import hashlib
from pathlib import Path
import unittest
from unittest.mock import patch

import numpy as np
import pandas as pd
from test_financial_assumptions import load_script, ROOT
import economic_assumptions as economics
import material_valuation as valuation


class InboundMaterialValuationTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.before = cls.hashes()
        cls.exports = patch.object(pd.DataFrame, 'to_csv', side_effect=AssertionError('CSV export forbidden'))
        cls.mkdirs = patch.object(Path, 'mkdir', side_effect=AssertionError('mkdir forbidden'))
        cls.exports.start()
        cls.mkdirs.start()
        cls.operations = load_script('03_generate_operations')
        cls.financials = load_script('04_generate_financials')

    @classmethod
    def hashes(cls):
        return {p: hashlib.sha256(p.read_bytes()).hexdigest()
                for folder in ('data', 'sql', 'powerbi')
                for p in (ROOT / folder).rglob('*') if p.is_file()}

    @classmethod
    def tearDownClass(cls):
        cls.exports.stop()
        cls.mkdirs.stop()
        if cls.hashes() != cls.before:
            raise AssertionError('Protected files changed')

    def fixture(self, count=2, zero=False):
        months = pd.DataFrame([dict(month_id=d.strftime('%Y-%m-01'), days_in_month=d.days_in_month)
                               for d in pd.date_range('2024-01-01', periods=count, freq='MS')])
        masters = dict(
            materials=pd.DataFrame([dict(material_id='M001', material_name='Steel', unit='kg', base_unit_cost_eur=2.8)]),
            suppliers=pd.DataFrame([dict(supplier_id='S001', lead_time_days=5)]),
            material_suppliers=pd.DataFrame([dict(material_id='M001', supplier_id='S001')]),
            products=pd.DataFrame([dict(product_id='P001', line_id='L01', base_selling_price_eur=50.,
                standard_labor_hours_per_attempt=.5, standard_energy_kwh_per_attempt=2.)]),
            production_lines=pd.DataFrame([dict(line_id='L01', monthly_capacity_units=100,
                support_labor_hours_per_month=120., base_energy_kwh_per_month=2400.)]),
            bom=pd.DataFrame([dict(product_id='P001', material_id='M001', quantity_kg_per_unit=1.)]))
        production = pd.DataFrame([dict(production_id=f'PR{i+1:06d}', month_id=month,
            product_id='P001', attempted_units=0 if zero else 4, defective_units=0,
            good_units=0 if zero else 4) for i, month in enumerate(months.month_id)])
        consumption = pd.DataFrame([dict(production_id=pid, material_id='M001',
            required_kg=0. if zero else 4., extra_waste_kg=0. if zero else .02,
            consumed_kg=0. if zero else 4.02) for pid in production.production_id])
        return masters, months, production, consumption

    def flow(self, fixture):
        return self.operations.generate_material_flow(*fixture, np.random.default_rng(361))

    def validate_flow(self, fixture, flow):
        _, _, production, _ = fixture
        consumption, orders, receipts, inventory = flow
        self.operations.validate_material_components(production, consumption, orders, receipts, inventory)

    def test_receipt_purchase_freight_and_landed_unit_hand_calculation(self):
        row = valuation.value_receipt(10, 2.8, .12)
        self.assertEqual(row['receipt_value_eur'], 28.)
        self.assertEqual(row['purchase_value_eur'], 28.)
        self.assertEqual(row['inbound_freight_eur'], 1.2)
        self.assertEqual(row['landed_receipt_value_eur'], 29.2)
        self.assertEqual(row['landed_unit_cost_eur'], 2.92)

    def test_component_weighted_average_and_carry_hand_calculation(self):
        ledger, issues = valuation.value_material_month(10, 20, 1, 10, 40, 3, [5, 10])
        self.assertEqual(ledger['weighted_average_unit_cost_eur'], 3.2)
        self.assertEqual(ledger['issued_purchase_material_value_eur'], 45)
        self.assertEqual(ledger['issued_inbound_freight_value_eur'], 3)
        self.assertEqual([row['issued_material_value_eur'] for row in issues], [16, 32])
        self.assertEqual(ledger['closing_purchase_material_value_eur'], 15)
        self.assertEqual(ledger['closing_inbound_freight_value_eur'], 1)
        next_month, issues = valuation.value_material_month(5, 15, 1, 0, 0, 0, [5])
        self.assertEqual(next_month['issued_material_value_eur'], 16)
        self.assertEqual(next_month['closing_value_eur'], 0)
        self.assertEqual(next_month['closing_kg'], 0)

    def test_component_rounding_and_tie_allocation(self):
        ledger, issues = valuation.value_material_month(0, 0, 0, .003, .01, .01, [.001, .001, .001])
        self.assertEqual([row['issued_material_value_eur'] for row in issues], [.02, 0, 0])
        self.assertEqual(ledger['closing_value_eur'], 0)
        ledger, issues = valuation.value_material_month(1, .01, .01, 0, 0, 0, [.5])
        # Each component rounds half-up. Total can differ by one cent from
        # independently rounding aggregate WAC x quantity.
        self.assertEqual(ledger['issued_material_value_eur'], .02)
        self.assertEqual(ledger['closing_value_eur'], 0)
        self.assertEqual(valuation.value_receipt(1, .005, .005)['landed_receipt_value_eur'], .02)
        ledger, issues = valuation.value_material_month(0, 0, 0, .002, .01, .01, [.001, 0, .001])
        self.assertEqual(issues[1]['issued_material_value_eur'], 0)

    def test_zero_quantities_and_invalid_values(self):
        receipt = valuation.value_receipt(0, 2.8, .12)
        self.assertEqual(receipt['landed_unit_cost_eur'], 0)
        self.assertEqual(receipt['landed_receipt_value_eur'], 0)
        ledger, issues = valuation.value_material_month(0, 0, 0, 0, 0, 0, [0])
        self.assertEqual(ledger['weighted_average_unit_cost_eur'], 0)
        self.assertEqual(issues[0]['issued_material_value_eur'], 0)
        for args in ((0, 1, 0, 0, 0, 0, []), (1, 2, .1, 0, 0, 0, [2])):
            with self.assertRaises(ValueError):
                valuation.value_material_month(*args)
        for invalid in (-1, float('nan'), float('inf'), .0001):
            with self.assertRaises(ValueError):
                valuation.value_receipt(invalid, 2.8, .12)

    def test_freight_rates_are_plausible_deterministic_and_rng_independent(self):
        rates = [economics.inbound_freight_rate('M001', supplier, month, i)
                 for supplier in ('S001', 'S002')
                 for i, month in enumerate(('2024-01-01', '2024-02-01'))]
        self.assertTrue(all(.10 <= rate <= .15 for rate in rates))
        self.assertGreater(len(set(rates)), 1)
        self.assertEqual(rates[0], economics.inbound_freight_rate('M001', 'S001', '2024-01-01', 0))
        rng = np.random.default_rng(361)
        expected = np.random.default_rng(361).random()
        economics.inbound_freight_rate('M001', 'S001', '2024-01-01', 0)
        self.assertEqual(rng.random(), expected)
        with patch.object(economics, 'INBOUND_FREIGHT_BASE_EUR_PER_KG', -1):
            with self.assertRaises(ValueError):
                economics.validate_freight_assumptions()

    def test_generated_component_rollforwards_and_opening_freight(self):
        fixture = self.fixture()
        flow = self.flow(fixture)
        self.validate_flow(fixture, flow)
        consumption, orders, receipts, inventory = flow
        self.assertEqual(inventory.iloc[0].opening_kg, 1.005)
        self.assertEqual(inventory.iloc[0].opening_purchase_material_value_eur, 2.81)
        self.assertEqual(inventory.iloc[0].opening_inbound_freight_value_eur, .12)
        for component in ('purchase_material', 'inbound_freight'):
            self.assertEqual(inventory.iloc[1][f'opening_{component}_value_eur'],
                             inventory.iloc[0][f'closing_{component}_value_eur'])
        for row in receipts.itertuples(index=False):
            self.assertEqual(valuation.cents(row.receipt_value_eur) + valuation.cents(row.inbound_freight_eur),
                             valuation.cents(row.landed_receipt_value_eur))
            self.assertAlmostEqual(row.landed_unit_cost_eur * row.received_kg,
                                   row.landed_receipt_value_eur, delta=row.received_kg*.0000000051)

    def test_no_consumption_and_no_receipts_keep_defined_schema(self):
        fixture = self.fixture(zero=True)
        flow = self.flow(fixture)
        self.validate_flow(fixture, flow)
        consumption, orders, receipts, inventory = flow
        self.assertTrue(orders.empty and receipts.empty)
        self.assertEqual(inventory.closing_value_eur.sum(), 0)
        self.assertEqual(consumption.issued_material_value_eur.sum(), 0)

    def test_zero_quantity_receipt_validation_and_no_issue_month(self):
        fixture = self.fixture(zero=True)
        consumption, orders, receipts, inventory = self.flow(fixture)
        orders = pd.DataFrame([dict(po_line_id='PO000001', material_id='M001', supplier_id='S001',
            order_date='2024-01-20', expected_receipt_date='2024-01-25', ordered_kg=0., agreed_unit_cost_eur=2.8)])
        values = valuation.value_receipt(0, 2.8, .12)
        receipts = pd.DataFrame([dict(receipt_id='RC000001', po_line_id='PO000001',
            receipt_date='2024-01-25', received_kg=0., **values)])
        self.validate_flow(fixture, (consumption, orders, receipts, inventory))
        ledger, issues = valuation.value_material_month(10, 28, 1.2, 0, 0, 0, [])
        self.assertEqual(issues, [])
        self.assertEqual(ledger['closing_purchase_material_value_eur'], 28)
        self.assertEqual(ledger['closing_inbound_freight_value_eur'], 1.2)

    def test_row_permutation_reproducibility_and_stable_keys(self):
        fixture = self.fixture()
        first = self.flow(fixture)
        masters, months, production, consumption = fixture
        shuffled = ({name: frame.iloc[::-1].reset_index(drop=True) for name, frame in masters.items()},
                    months.iloc[::-1], production.iloc[::-1], consumption.iloc[::-1])
        for baseline, changed in zip(first, self.flow(shuffled)):
            pd.testing.assert_frame_equal(baseline, changed)
        self.assertEqual(first[1].po_line_id.tolist(), ['PO000001', 'PO000002'])
        self.assertEqual(first[2].receipt_id.tolist(), ['RC000001', 'RC000002'])

    def test_validation_rejects_component_corruption_and_partial_schema(self):
        fixture = self.fixture()
        flow = self.flow(fixture)
        for index, column in ((2, 'purchase_value_eur'), (2, 'inbound_freight_eur'),
                              (2, 'landed_receipt_value_eur'), (2, 'landed_unit_cost_eur'),
                              (3, 'opening_inbound_freight_value_eur'),
                              (3, 'closing_purchase_material_value_eur'),
                              (0, 'issued_inbound_freight_eur'), (0, 'issued_material_value_eur')):
            with self.subTest(column=column):
                changed = [frame.copy(deep=True) for frame in flow]
                changed[index].loc[0, column] += .01
                with self.assertRaises(ValueError):
                    self.validate_flow(fixture, changed)
        changed = [frame.copy(deep=True) for frame in flow]
        changed[0] = changed[0].drop(columns=['issued_inbound_freight_eur'])
        with self.assertRaisesRegex(ValueError, 'Incomplete inbound component schema'):
            self.validate_flow(fixture, changed)

    def test_existing_full_production_validation_on_small_component_fixture(self):
        # 24 tiny monthly records meet the pre-existing coverage contract.
        fixture = self.fixture(count=24)
        masters, months, production, _ = fixture
        consumption, orders, receipts, inventory = self.flow(fixture)
        capacity = pd.DataFrame([dict(month_id=month, line_id='L01', nominal_capacity_units=100,
            downtime_pct=0., effective_capacity_units=100) for month in months.month_id])
        frames = dict(months=months, line_month_capacity=capacity, production=production,
            material_consumption=consumption, purchase_order_lines=orders, material_receipts=receipts,
            raw_material_inventory=inventory)
        self.operations.validate(masters, frames)

    def test_freight_enters_manufacturing_materials_once_without_changing_conversion(self):
        fixture = self.fixture()
        flow = self.flow(fixture)
        with patch.object(self.operations, 'inbound_freight_rate', return_value=.24), \
             patch.object(self.operations, 'INBOUND_FREIGHT_BASE_EUR_PER_KG', .24):
            higher = self.flow(fixture)
        pd.testing.assert_frame_equal(flow[1], higher[1])  # Same purchasing RNG/terms.
        pd.testing.assert_series_equal(flow[2].receipt_value_eur, higher[2].receipt_value_eur)
        masters, months, production, _ = fixture
        base_inputs = dict(**masters, months=months, production=production,
            line_month_capacity=pd.DataFrame([dict(month_id=month, line_id='L01') for month in months.month_id]),
            material_consumption=flow[0])
        base_line, base_alloc = self.financials.generate_costs(base_inputs, np.random.default_rng(362))
        high_inputs = dict(base_inputs, material_consumption=higher[0])
        high_line, high_alloc = self.financials.generate_costs(high_inputs, np.random.default_rng(362))
        pd.testing.assert_frame_equal(base_line, high_line)
        self.financials.validate_conversion_costs(base_inputs, base_line, base_alloc)
        self.financials.validate_conversion_costs(high_inputs, high_line, high_alloc)
        self.assertGreater(high_alloc.material_cost_eur.sum(), base_alloc.material_cost_eur.sum())
        self.assertEqual(sum(map(valuation.cents, high_alloc.material_cost_eur)) - sum(map(valuation.cents, base_alloc.material_cost_eur)),
            sum(map(valuation.cents, higher[0].issued_inbound_freight_eur)) - sum(map(valuation.cents, flow[0].issued_inbound_freight_eur)))
        sales = pd.DataFrame([dict(month_id=month, net_revenue_eur=1000.) for month in months.month_id])
        pd.testing.assert_frame_equal(self.financials.generate_opex(base_inputs, sales),
                                      self.financials.generate_opex(high_inputs, sales))


if __name__ == '__main__':
    unittest.main()
