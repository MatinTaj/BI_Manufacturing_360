"""Non-destructive in-memory edge-case tests; no database or file generation."""
import unittest
from decimal import Decimal as D
from reference_calculator import split_cents,reconstruct_exposure,calculate

def base():
    return {k:D(v) for k,v in dict(revenue='100',material='20',inbound='2',direct_labor='20',support_labor='5',energy='3',overhead='10',outbound='5',fixed_selling='3',variable_selling='2',administration='5',idle='0',loss='0').items()}
class ReferenceTests(unittest.TestCase):
    def test_exact_half_cent_tie_direct_first(self):self.assertEqual(split_cents(1,[1,1],['direct','support']),[1,0])
    def test_sales_tie_uses_stable_key(self):self.assertEqual(split_cents(1,[1,1],['B','A']),[0,1])
    def test_zero_pool(self):self.assertEqual(split_cents(0,[0,0],['A','B']),[0,0])
    def test_invalid_pool(self):
        with self.assertRaises(ValueError):split_cents(1,[0],['A'])
        with self.assertRaises(ValueError):split_cents(1,[-1],['A'])
    def test_full_issue_conserves_parts(self):self.assertEqual(split_cents(100,[61,39],['direct','support']),[61,39])
    def test_no_shipments_preserve_direct_inventory(self):
        f=[dict(month_id='2024-01-01',product_id='P',opening_labor_value_eur=0,production_labor_value_eur=100,labor_cogs_eur=0,closing_labor_value_eur=100),dict(month_id='2024-02-01',product_id='P',opening_labor_value_eur=100,production_labor_value_eur=0,labor_cogs_eur=100,closing_labor_value_eur=0)]
        a=[dict(month_id=x['month_id'],product_id='P',good_units=1 if i==0 else 0,capitalized_labor_cost_eur=100 if i==0 else 0,production_labor_cost_eur=60 if i==0 else 99,support_labor_cost_eur=40 if i==0 else 1) for i,x in enumerate(f)]
        sales=[dict(month_id='2024-02-01',product_id='P',sales_line_id='A',labor_cogs_eur=100)]
        result,ledger=reconstruct_exposure(f,a,sales)
        self.assertEqual(result['A'],dict(direct=D(60),support=D(40)))
        self.assertEqual(ledger[0]['direct_closing_cents'],6000)
    def test_unknown_initial_inventory_rejected(self):
        f=[dict(month_id='2024-01-01',product_id='P',opening_labor_value_eur=1,production_labor_value_eur=0,labor_cogs_eur=0,closing_labor_value_eur=1)]
        a=[dict(month_id='2024-01-01',product_id='P',good_units=0,capitalized_labor_cost_eur=0,production_labor_cost_eur=0,support_labor_cost_eur=0)]
        with self.assertRaises(AssertionError):reconstruct_exposure(f,a,[])
    def test_zero_setting(self):
        x=calculate(base(),{});self.assertEqual(x['op_change'],0);self.assertEqual(x['gp_change'],0)
    def test_direct_labor_only(self):
        b=base();x=calculate(b,{'labor':'.10'});self.assertEqual(x['op_change'],D('-2'));self.assertEqual(x['support_labor_cogs'],D(5))
    def test_outbound_does_not_change_gp(self):
        x=calculate(base(),{'outbound':'.10'});self.assertEqual(x['gp_change'],0);self.assertEqual(x['op_change'],D('-.5'))
    def test_price_variable_selling_response(self):
        x=calculate(base(),{'price':'.05'});self.assertEqual(x['gp_change'],D(5));self.assertEqual(x['op_change'],D('4.9'));self.assertEqual(x['variable_selling'],D('2.10'))
    def test_combined_linear(self):
        b=base();x=calculate(b,{'material':'.10','price':'.05'});self.assertEqual(x['op_change'],calculate(b,{'material':'.10'})['op_change']+calculate(b,{'price':'.05'})['op_change'])
    def test_zero_revenue_profit_ratios_are_none(self):
        b={k:D(0) for k in base()};x=calculate(b,{});self.assertIsNone(x['gross_margin_pct']);self.assertIsNone(x['op_change_pct'])
    def test_invalid_parameters(self):
        for p in ({'labor':D('NaN')},{'material':D('1.01')},{'price':D('-.51')},{'unknown':0}):
            with self.assertRaises(ValueError):calculate(base(),p)
    def test_negative_base_profit_percentage_is_defined(self):
        b=base();b['administration']=D(100);x=calculate(b,{'material':'.10'});self.assertLess(x['op_change'],0);self.assertGreater(x['op_change_pct'],0)
if __name__=='__main__':unittest.main()
