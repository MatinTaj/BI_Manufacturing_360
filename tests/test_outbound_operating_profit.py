"""Phase 6 shipment freight, expense ownership and company P&L regressions."""
import hashlib
from pathlib import Path
import unittest
from unittest.mock import patch

import numpy as np
import pandas as pd
import test_financial_assumptions as baseline
import test_finished_goods_components as fg_tests
import economic_assumptions as economics


class OutboundOperatingProfitTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.before = cls.hashes()
        cls.exports = patch.object(pd.DataFrame, 'to_csv', side_effect=AssertionError('CSV export forbidden'))
        cls.mkdirs = patch.object(Path, 'mkdir', side_effect=AssertionError('mkdir forbidden'))
        cls.exports.start()
        cls.mkdirs.start()
        cls.financials = baseline.load_script('04_generate_financials')

    @classmethod
    def hashes(cls):
        return {p: hashlib.sha256(p.read_bytes()).hexdigest()
                for folder in ('data', 'sql', 'powerbi')
                for p in (baseline.ROOT / folder).rglob('*') if p.is_file()}

    @classmethod
    def tearDownClass(cls):
        cls.exports.stop()
        cls.mkdirs.stop()
        if cls.before != cls.hashes():
            raise AssertionError('Protected files changed')

    def fixture(self, zero=False):
        inputs = fg_tests.FinishedGoodsComponentTests.fixture(self, zero=zero)
        inputs['customers']['segment'] = ['OEM', 'Tier 1', 'Aftermarket', 'OEM', 'Tier 1', 'Aftermarket', 'OEM', 'Tier 1']
        return inputs

    def frames(self, inputs):
        return fg_tests.FinishedGoodsComponentTests.mini_financials(self, inputs)

    def test_segment_rates_deterministic_variation_and_invalid_settings(self):
        for segment, base in economics.OUTBOUND_FREIGHT_RATES_EUR_PER_UNIT.items():
            values = [economics.outbound_freight_rate(segment, customer, month)
                      for customer in ('C001', 'C002') for month in ('2024-01-01', '2024-02-01')]
            self.assertTrue(all(base * .95 * .97 - .00005 <= value <= base * 1.05 * 1.03 + .00005 for value in values))
            self.assertGreater(len(set(values)), 1)
            self.assertEqual(values[0], economics.outbound_freight_rate(segment, 'C001', '2024-01-01'))
        with self.assertRaisesRegex(ValueError, 'Unknown outbound'):
            economics.outbound_freight_rate('UNKNOWN', 'C001', '2024-01-01')
        for rates in ({'OEM': 1.2}, {'OEM': -1, 'Tier 1': 1.5, 'Aftermarket': 2.2},
                      {'OEM': float('nan'), 'Tier 1': 1.5, 'Aftermarket': 2.2}):
            with patch.object(economics, 'OUTBOUND_FREIGHT_RATES_EUR_PER_UNIT', rates):
                with self.assertRaises(ValueError):
                    economics.validate_outbound_freight_assumptions()

    def test_freight_uses_shipped_units_with_half_up_rounding(self):
        amount = self.financials.outbound_freight_amount
        self.assertEqual(amount(3, 1.2345), 3.70)
        self.assertEqual(amount(1, 1.005), 1.01)
        self.assertEqual(amount(0, 2.2), 0.)
        self.assertEqual(amount(10, 0), 0.)
        for quantity, rate in ((-1, 1.2), (.5, 1.2), (1, -1), (float('inf'), 1.2), (1, float('nan'))):
            with self.assertRaises(ValueError):
                amount(quantity, rate)
        inputs = self.fixture()
        frames = self.frames(inputs)
        sale = frames['sales'].iloc[0]
        # Request/lost-demand quantities have no bearing on freight valuation.
        changed = {name: frame.copy(deep=True) for name, frame in frames.items()}
        changed['sales'].loc[0, 'requested_units'] += 100
        changed['sales'].loc[0, 'unfulfilled_units'] += 100
        self.financials.validate(inputs, changed)
        self.assertEqual(changed['sales'].iloc[0].outbound_freight_eur, sale.outbound_freight_eur)

    def test_generated_freight_reconciles_and_is_not_in_opex_or_cogs(self):
        inputs = self.fixture()
        frames = self.frames(inputs)
        self.financials.validate(inputs, frames)
        for sale in frames['sales'].itertuples(index=False):
            rate = economics.outbound_freight_rate(inputs['customers'].set_index('customer_id').at[sale.customer_id, 'segment'], sale.customer_id, sale.month_id)
            self.assertEqual(sale.outbound_freight_rate_eur_per_unit, rate)
            self.assertEqual(sale.outbound_freight_eur, self.financials.outbound_freight_amount(sale.units_shipped, rate))
        self.assertEqual(set(frames['operating_expenses'].expense_category), {'selling', 'administration'})
        for name, frame in frames.items():
            if name != 'sales':
                self.assertFalse(set(self.financials.OUTBOUND_COLUMNS) & set(frame.columns))

    def test_freight_rate_change_preserves_revenue_cogs_inventory_and_rng(self):
        inputs = self.fixture()
        original = self.frames(inputs)
        # In-memory sensitivity for isolation, not a new scenario implementation.
        with patch.object(self.financials, 'outbound_freight_rate', return_value=0.):
            no_freight = self.frames(inputs)
        for name in original:
            if name == 'sales':
                pd.testing.assert_frame_equal(original[name].drop(columns=list(self.financials.OUTBOUND_COLUMNS)),
                                              no_freight[name].drop(columns=list(self.financials.OUTBOUND_COLUMNS)))
            else:
                pd.testing.assert_frame_equal(original[name], no_freight[name])
        before = self.financials.profit_totals(no_freight)
        after = self.financials.profit_totals(original)
        self.assertEqual(before['gross_profit'], after['gross_profit'])
        self.assertEqual(before['operating_profit'] - after['operating_profit'], after['outbound_freight'])
        self.assertGreater(after['outbound_freight'], 0)

    def test_explicit_fixed_variable_expenses_and_price_driven_behavior(self):
        inputs = self.fixture()
        sales = pd.DataFrame([dict(month_id=month, net_revenue_eur=100000.) for month in inputs['months'].month_id])
        recorded = self.financials.generate_opex(inputs, sales)
        january = recorded.query('month_id == "2024-01-01"').set_index('expense_category')
        self.assertEqual(january.loc['selling', 'fixed_amount_eur'], 26000.)
        self.assertEqual(january.loc['selling', 'variable_amount_eur'], 2000.)
        self.assertEqual(january.loc['selling', 'amount_eur'], 28000.)
        self.assertEqual(january.loc['administration', 'variable_amount_eur'], 0.)
        self.assertEqual(january.loc['administration', 'amount_eur'], 38000.)
        sales.net_revenue_eur *= 2
        doubled = self.financials.generate_opex(inputs, sales)
        pd.testing.assert_series_equal(recorded.fixed_amount_eur, doubled.fixed_amount_eur)
        self.assertEqual(doubled.query('expense_category == "selling"').variable_amount_eur.sum(), 8000.)
        self.assertEqual(doubled.query('expense_category == "administration"').variable_amount_eur.sum(), 0.)
        february = recorded.query('month_id == "2024-02-01"').set_index('expense_category')
        self.assertEqual(february.loc['selling', 'fixed_amount_eur'], 26039.)
        self.assertEqual(february.loc['administration', 'fixed_amount_eur'], 38057.)
        for row in recorded.itertuples(index=False):
            self.assertEqual(self.financials.cents(row.amount_eur), self.financials.cents(row.fixed_amount_eur) + self.financials.cents(row.variable_amount_eur))

    def test_zero_shipments_zero_revenue_keep_fixed_expenses_and_idle_separate(self):
        inputs = self.fixture(zero=True)
        frames = self.frames(inputs)
        self.financials.validate(inputs, frames)
        self.assertTrue(frames['sales'].empty)
        self.assertTrue(set(self.financials.OUTBOUND_COLUMNS).issubset(frames['sales'].columns))
        self.assertEqual(frames['operating_expenses'].variable_amount_eur.sum(), 0)
        totals = self.financials.profit_totals(frames)
        self.assertEqual(totals['outbound_freight'], 0)
        self.assertGreater(totals['selling_expenses'], 0)
        self.assertGreater(totals['administrative_expenses'], 0)
        self.assertGreater(totals['idle_cost'], 0)
        self.assertEqual(totals['production_loss'], 0)
        self.assertEqual(totals['operating_profit'], -totals['selling_admin_expenses'] - totals['idle_cost'])

    def test_company_pnl_independent_hand_calculation(self):
        frames = dict(
            sales=pd.DataFrame([dict(sales_line_id='SL1', net_revenue_eur=1000., cogs_eur=400., outbound_freight_rate_eur_per_unit=1., outbound_freight_eur=10.),
                                dict(sales_line_id='SL2', net_revenue_eur=500., cogs_eur=200., outbound_freight_rate_eur_per_unit=2., outbound_freight_eur=20.)]),
            operating_expenses=pd.DataFrame([dict(month_id='2024-01-01', expense_category='selling', amount_eur=50.),
                                             dict(month_id='2024-01-01', expense_category='administration', amount_eur=70.)]),
            manufacturing_costs=pd.DataFrame([dict(idle_cost_eur=5.)]),
            production_cost_allocation=pd.DataFrame([dict(production_loss_expense_eur=15.)]))
        totals = self.financials.profit_totals(frames)
        self.assertEqual(totals['revenue'], 150000)
        self.assertEqual(totals['cogs'], 60000)
        self.assertEqual(totals['gross_profit'], 90000)
        self.assertEqual(totals['outbound_freight'], 3000)
        self.assertEqual(totals['selling_expenses'], 5000)
        self.assertEqual(totals['administrative_expenses'], 7000)
        self.assertEqual(totals['separately_expensed_production_costs'], 2000)
        self.assertEqual(totals['operating_profit'], 73000)

    def test_company_monthly_pnl_and_production_loss_reconciliation(self):
        inputs = self.fixture()
        inputs['production'].loc[0, 'good_units'] = 0
        inputs['production'].loc[0, 'defective_units'] = inputs['production'].loc[0, 'attempted_units']
        frames = self.frames(inputs)
        self.financials.validate(inputs, frames)
        total = self.financials.profit_totals(frames)
        monthly = [self.financials.profit_totals({name: frame[frame.month_id == month] for name, frame in frames.items()}) for month in inputs['months'].month_id]
        for key in total:
            self.assertEqual(total[key], sum(row[key] for row in monthly))
        self.assertGreater(total['production_loss'], 0)
        self.assertEqual(total['operating_profit'], total['gross_profit'] - total['outbound_freight'] - total['selling_expenses'] - total['administrative_expenses'] - total['idle_cost'] - total['production_loss'])

    def test_reject_corrupt_partial_and_duplicate_freight_recognition(self):
        inputs = self.fixture()
        original = self.frames(inputs)
        mutations = [('sales', 'outbound_freight_rate_eur_per_unit'), ('sales', 'outbound_freight_eur'),
                     ('operating_expenses', 'amount_eur'), ('operating_expenses', 'variable_amount_eur')]
        for table, column in mutations:
            with self.subTest(column=column):
                changed = {name: frame.copy(deep=True) for name, frame in original.items()}
                changed[table].loc[0, column] += .01
                with self.assertRaises(ValueError):
                    self.financials.validate(inputs, changed)
        changed = {name: frame.copy(deep=True) for name, frame in original.items()}
        changed['sales'] = changed['sales'].drop(columns=['outbound_freight_eur'])
        with self.assertRaisesRegex(ValueError, 'Incomplete outbound'):
            self.financials.validate(inputs, changed)
        changed = {name: frame.copy(deep=True) for name, frame in original.items()}
        changed['operating_expenses'].loc[0, 'expense_category'] = 'outbound_freight'
        with self.assertRaisesRegex(ValueError, 'freight is sales-owned'):
            self.financials.profit_totals(changed)
        changed = {name: frame.copy(deep=True) for name, frame in original.items()}
        changed['operating_expenses']['outbound_freight_eur'] = 0.
        with self.assertRaisesRegex(ValueError, 'belongs only in sales'):
            self.financials.profit_totals(changed)
        for table, label in [('sales', 'Duplicate sale'), ('operating_expenses', 'Duplicate operating expense')]:
            changed = {name: frame.copy(deep=True) for name, frame in original.items()}
            changed[table] = pd.concat([changed[table], changed[table].iloc[:1]], ignore_index=True)
            with self.assertRaisesRegex(ValueError, label):
                self.financials.profit_totals(changed)

    def test_legacy_no_freight_fields_remains_explicit_zero_freight(self):
        inputs = self.fixture()
        frames = self.frames(inputs)
        before = self.financials.profit_totals(frames)
        frames['sales'] = frames['sales'].drop(columns=list(self.financials.OUTBOUND_COLUMNS))
        frames['operating_expenses'] = frames['operating_expenses'].drop(columns=['variable_amount_eur'])
        self.financials.validate(inputs, frames)
        legacy = self.financials.profit_totals(frames)
        self.assertEqual(legacy['outbound_freight'], 0)
        self.assertEqual(legacy['operating_profit'] - before['operating_profit'], before['outbound_freight'])


if __name__ == '__main__':
    unittest.main()
