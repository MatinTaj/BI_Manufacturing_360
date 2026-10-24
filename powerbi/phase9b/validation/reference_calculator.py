"""Independent Decimal/integer-cent scenario reference; PostgreSQL access is read-only.
Does not execute DAX/M, change source data, or create database objects.
"""
import csv,hashlib,json,re,subprocess
from collections import defaultdict
from decimal import Decimal,ROUND_HALF_UP,localcontext
from pathlib import Path
D=Decimal
HERE=Path(__file__).resolve().parent
PACKAGE=HERE.parent
ROOT=PACKAGE.parents[1]
DRIVERS=('price','material','inbound','outbound','labor','energy')

def cents(value):
    value=D(str(value))*100
    if value!=value.to_integral_value():raise ValueError('Source is not exact cents')
    return int(value)

def split_cents(total,weights,keys):
    if total<0 or any(w<0 for w in weights):raise ValueError('Negative costs/weights')
    denominator=sum(weights)
    if denominator==0:
        if total:raise ValueError('Nonzero total with no weights')
        return [0]*len(weights)
    base=[total*w//denominator for w in weights]
    residual=total-sum(base)
    ranked=sorted(range(len(weights)),key=lambda i:(-(total*weights[i]%denominator),keys[i]))
    for i in ranked[:residual]:base[i]+=1
    assert sum(base)==total
    return base

def reconstruct_exposure(finished,allocations,sales):
    alloc={(r['month_id'],r['product_id']):r for r in allocations}
    assert len(alloc)==len(allocations)
    grouped=defaultdict(list)
    for r in sales:grouped[(r['month_id'],r['product_id'])].append(r)
    state={};result={};ledger=[]
    for f in sorted(finished,key=lambda x:(x['product_id'],x['month_id'])):
        key=(f['month_id'],f['product_id']);a=alloc[key]
        op=cents(f['opening_labor_value_eur']);addition=cents(f['production_labor_value_eur']);issued=cents(f['labor_cogs_eur']);close=cents(f['closing_labor_value_eur'])
        if f['product_id'] not in state:
            assert op==0,'Unknown initial direct/support split; cannot invent opening allocation'
            opening_direct=0
        else:
            opening_direct,previous_total,previous_month=state[f['product_id']]
            assert op==previous_total
            y,m=map(int,previous_month[:7].split('-'));next_month=f'{y+int(m==12):04}-{1 if m==12 else m+1:02}-01'
            assert f['month_id']==next_month,'Nonconsecutive inventory months'
        assert addition==cents(a['capitalized_labor_cost_eur'])
        direct_add=cents(a['production_labor_cost_eur']) if a['good_units']>0 else 0
        support_add=addition-direct_add
        assert support_add>=0 and direct_add>=0
        if a['good_units']>0:assert support_add==cents(a['support_labor_cost_eur'])
        direct_available=opening_direct+direct_add
        total_available=op+addition;support_available=total_available-direct_available
        assert 0<=issued<=total_available and support_available>=0
        # Existing total monthly labor COGS is authoritative. Allocate analytical parts only.
        direct_cogs,support_cogs=split_cents(issued,[direct_available,support_available],['direct','support'])
        closing_direct=direct_available-direct_cogs;closing_support=support_available-support_cogs
        assert op+addition-issued==close and closing_direct+closing_support==close
        assert closing_direct>=0 and closing_support>=0
        state[f['product_id']]=(closing_direct,close,f['month_id'])
        lines=sorted(grouped[key],key=lambda x:x['sales_line_id'])
        line_labor=[cents(x['labor_cogs_eur']) for x in lines]
        assert sum(line_labor)==issued
        assigned=split_cents(direct_cogs,line_labor,[x['sales_line_id'] for x in lines])
        for row,value,total in zip(lines,assigned,line_labor):
            assert 0<=value<=total and row['sales_line_id'] not in result
            result[row['sales_line_id']]={'direct':D(value)/100,'support':D(total-value)/100}
        assert sum(assigned)==direct_cogs
        ledger.append(dict(month_id=f['month_id'],product_id=f['product_id'],direct_opening_cents=opening_direct,direct_addition_cents=direct_add,direct_cogs_cents=direct_cogs,direct_closing_cents=closing_direct,support_cogs_cents=support_cogs))
    assert len(result)==len(sales)
    return result,ledger

def calculate(base,parameters):
    if set(parameters)-set(DRIVERS):raise ValueError('Unknown scenario driver')
    p={name:D(str(parameters.get(name,0))) for name in DRIVERS}
    if any(not x.is_finite() or x<D('-0.50') or x>D('1.00') for x in p.values()):raise ValueError('Parameter outside prepared range')
    revenue=base['revenue']*(1+p['price'])
    material=base['material']*(1+p['material']);inbound=base['inbound']*(1+p['inbound'])
    direct=base['direct_labor']*(1+p['labor']);support=base['support_labor']
    energy=base['energy']*(1+p['energy']);overhead=base['overhead']
    cogs=material+inbound+direct+support+energy+overhead
    gp=revenue-cogs;outbound=base['outbound']*(1+p['outbound'])
    fixed=base['fixed_selling'];variable=base['variable_selling']*(1+p['price'])
    selling=fixed+variable;admin=base['administration'];opex=selling+admin
    idle=base['idle'];loss=base['loss'];op=gp-outbound-opex-idle-loss
    base_cogs=sum(base[k] for k in ('material','inbound','direct_labor','support_labor','energy','overhead'))
    base_gp=base['revenue']-base_cogs;base_op=base_gp-base['outbound']-base['fixed_selling']-base['variable_selling']-admin-idle-loss
    ratio=lambda n,d:100*n/d if d else None
    return dict(revenue=revenue,material_cogs=material,inbound_cogs=inbound,direct_labor_cogs=direct,support_labor_cogs=support,labor_cogs=direct+support,energy_cogs=energy,overhead_cogs=overhead,cogs=cogs,gross_profit=gp,gross_margin_pct=ratio(gp,revenue),outbound_freight=outbound,fixed_selling=fixed,variable_selling=variable,selling_expenses=selling,administrative_expenses=admin,operating_expenses=opex,idle_cost=idle,production_loss=loss,operating_profit=op,operating_margin_pct=ratio(op,revenue),gp_change=gp-base_gp,gp_change_pct=ratio(gp-base_gp,base_gp),op_change=op-base_op,op_change_pct=ratio(op-base_op,base_op))

def baseline_for(period,data,exposure):
    select=lambda name:[r for r in data[name] if period=='combined' or r['month_id'].startswith(period)]
    sales=select('sales');opex=select('operating_expenses')
    amount=lambda col:sum((D(str(r[col])) for r in sales),D(0))
    b={key:amount(col) for key,col in [('revenue','net_revenue_eur'),('material','material_cogs_eur'),('inbound','inbound_freight_cogs_eur'),('energy','energy_cogs_eur'),('overhead','overhead_cogs_eur'),('outbound','outbound_freight_eur')]}
    b['direct_labor']=sum((exposure[r['sales_line_id']]['direct'] for r in sales),D(0));b['support_labor']=sum((exposure[r['sales_line_id']]['support'] for r in sales),D(0))
    assert b['direct_labor']+b['support_labor']==amount('labor_cogs_eur')
    b['fixed_selling']=sum((D(str(r['fixed_amount_eur'])) for r in opex if r['expense_category']=='selling'),D(0));b['variable_selling']=sum((D(str(r['variable_amount_eur'])) for r in opex if r['expense_category']=='selling'),D(0))
    b['administration']=sum((D(str(r['amount_eur'])) for r in opex if r['expense_category']=='administration'),D(0))
    assert all(D(str(r['variable_amount_eur']))==0 for r in opex if r['expense_category']=='administration')
    assert b['fixed_selling']+b['variable_selling']==sum(D(str(r['amount_eur'])) for r in opex if r['expense_category']=='selling')
    b['idle']=sum((D(str(r['idle_cost_eur'])) for r in select('manufacturing_costs')),D(0));b['loss']=sum((D(str(r['production_loss_expense_eur'])) for r in select('production_cost_allocation')),D(0))
    assert sum(b[k] for k in ('material','inbound','direct_labor','support_labor','energy','overhead'))==amount('cogs_eur')
    return b

def main():
    report=Path((PACKAGE/'report_path.txt').read_text())
    args=['C:/Program Files/PostgreSQL/18/bin/psql.exe','-X','-w','-h','localhost','-p','5432','-U','postgres','-d','manufacturing_360','-v','ON_ERROR_STOP=1','-At','-f','-']
    def query(sql):
        r=subprocess.run(args,input='BEGIN ISOLATION LEVEL REPEATABLE READ READ ONLY;\n'+sql+';\nCOMMIT;',capture_output=True,text=True,encoding='utf-8')
        if r.returncode:raise RuntimeError(r.stderr)
        return [json.loads(l,parse_float=D) for l in r.stdout.splitlines() if l.startswith(('{','['))]
    def save(name,value): (report/name).write_text(json.dumps(value,indent=2,default=str)+'\n',encoding='utf-8')
    def snapshot():
        rels=query("SELECT jsonb_agg(q) FROM (SELECT schemaname,tablename FROM pg_tables WHERE schemaname IN ('public','manufacturing_v2') ORDER BY 1,2) q")[0]
        out={}
        for t in rels:
            name='.'.join('"'+t[k].replace('"','""')+'"' for k in ('schemaname','tablename'))
            out[name]=query("SELECT jsonb_build_object('rows',count(*),'hash',md5(coalesce(string_agg(h,'' ORDER BY h),''))) FROM (SELECT md5(row_to_json(t)::text) h FROM "+name+' t) q')[0]
        r=subprocess.run(['C:/Program Files/PostgreSQL/18/bin/pg_dump.exe','-w','-h','localhost','-p','5432','-U','postgres','-d','manufacturing_360','-n','public','-n','manufacturing_v2','--schema-only','--no-owner','--no-privileges'],capture_output=True,text=True)
        if r.returncode:raise RuntimeError('Definition capture failed')
        normalized=re.sub(r'(?m)^\\(un)?restrict .*$', '-- normalized restrict token',r.stdout)
        return dict(tables=out,definition_sha256=hashlib.sha256(normalized.encode()).hexdigest())
    before=snapshot();save('database_before.json',before)
    sql=';\n'.join("SELECT jsonb_build_object('dataset','"+name+"','rows',coalesce(jsonb_agg(q),'[]'::jsonb)) FROM manufacturing_v2."+name+' q' for name in ('sales','finished_goods_inventory','production_cost_allocation','operating_expenses','manufacturing_costs'))
    data={r['dataset']:r['rows'] for r in query(sql)}
    checks=query('SELECT jsonb_agg(q) FROM manufacturing_v2.audit_validation_results q')[0];assert len(checks)==36 and all(r['failed_rows']==0 for r in checks)
    comparisons=query('SELECT jsonb_agg(q) FROM manufacturing_v2.audit_pnl_reconciliation q')[0];assert len(comparisons)==33 and all(r['passed'] for r in comparisons)
    exposure,ledger=reconstruct_exposure(data['finished_goods_inventory'],data['production_cost_allocation'],data['sales'])
    sql_exposure=(HERE/'direct_labor_exposure.sql').read_text().strip().rstrip(';')
    actual=query('SELECT jsonb_agg(q) FROM ('+sql_exposure+') q')[0]
    assert len(actual)==len(exposure)
    for r in actual:
        expected=exposure[r['sales_line_id']]
        assert r['direct_labor_exposure_valid'] is True
        assert r['direct_labor_cogs_exposure_eur']==expected['direct'] and r['support_labor_cogs_exposure_eur']==expected['support']
    projection=(HERE/'fact_sales_scenario_projection.sql').read_text().strip().rstrip(';')
    projected=query('SELECT jsonb_agg(q) FROM ('+projection+') q')[0]
    original={r['sales_line_id']:r for r in query('SELECT jsonb_agg(q) FROM manufacturing_v2.bi_sales_detail q')[0]}
    for row in projected:
        assert all(row[col]==value for col,value in original[row['sales_line_id']].items())
        assert row['direct_labor_exposure_valid'] is True
    assert len(projected)==len(original)==2596
    cases={'all_zero':{},'material_plus_10':{'material':D('.10')},'direct_labor_plus_10':{'labor':D('.10')},'energy_plus_10':{'energy':D('.10')},'inbound_plus_10':{'inbound':D('.10')},'outbound_plus_10':{'outbound':D('.10')},'selling_price_plus_5':{'price':D('.05')},'material_plus_10_price_plus_5':{'material':D('.10'),'price':D('.05')}}
    for driver in DRIVERS:
        cases[driver+'_minimum']={driver:D('-.50')};cases[driver+'_maximum']={driver:D('1.00')}
    cases['all_maximum']={driver:D(1) for driver in DRIVERS};cases['all_minimum']={driver:D('-.5') for driver in DRIVERS}
    manifest=json.loads((ROOT/'sql/v2/input_manifest.json').read_text());path=ROOT/manifest['phase7_report']/'financial_comparison.csv'
    assert hashlib.sha256(path.read_bytes()).hexdigest()==manifest['phase7_financial_sha256']
    with path.open(newline='',encoding='utf-8') as f: approved={r['period']:r for r in csv.DictReader(f) if r['dataset']=='candidate'}
    results=[];bases={};zero_comparisons=0
    for period in ('2024','2025','combined'):
        b=baseline_for(period,data,exposure);bases[period]=b;base=calculate(b,{})
        for metric in ('revenue','cogs','gross_profit','outbound_freight','selling_expenses','administrative_expenses','idle_cost','production_loss','operating_profit','gross_margin_pct','operating_margin_pct'):
            tol=D('0.00000001') if metric.endswith('_pct') else D(0)
            assert abs(base[metric]-D(approved[period][metric]))<=tol,(period,metric)
            zero_comparisons+=1
        for name,changes in cases.items():
            out=calculate(b,changes)
            d={k:D(str(changes.get(k,0))) for k in DRIVERS}
            # Independent closed-form delta equation, not reuse of the P&L calculation path.
            expected_gp=b['revenue']*d['price']-b['material']*d['material']-b['inbound']*d['inbound']-b['direct_labor']*d['labor']-b['energy']*d['energy']
            expected_op=expected_gp-b['outbound']*d['outbound']-b['variable_selling']*d['price']
            assert out['gp_change']==expected_gp and out['op_change']==expected_op
            assert out['support_labor_cogs']==b['support_labor'] and out['overhead_cogs']==b['overhead']
            assert out['fixed_selling']==b['fixed_selling'] and out['administrative_expenses']==b['administration']
            assert out['operating_profit']==out['gross_profit']-out['outbound_freight']-out['operating_expenses']-out['idle_cost']-out['production_loss']
            assert out['cogs']==out['material_cogs']+out['inbound_cogs']+out['labor_cogs']+out['energy_cogs']+out['overhead_cogs']
            assert all(out[k]>=0 for k in ('material_cogs','inbound_cogs','direct_labor_cogs','support_labor_cogs','energy_cogs','overhead_cogs'))
            results.append(dict(period=period,scenario=name,parameters=d,**out))
        combined=calculate(b,{'material':D('.10'),'price':D('.05')})
        assert combined['op_change']==calculate(b,{'material':D('.10')})['op_change']+calculate(b,{'price':D('.05')})['op_change']
    save('baseline_inputs.json',bases);save('scenario_results_full_precision.json',results)
    # Report only, not regenerated source datasets. Decimal precision is preserved in JSON.
    with (report/'scenario_results.csv').open('w',newline='',encoding='utf-8') as stream:
        flat=[{k:v for k,v in row.items() if k!='parameters'} for row in results]
        writer=csv.DictWriter(stream,fieldnames=list(flat[0]));writer.writeheader();writer.writerows(flat)
    save('scenario_definitions.json',cases);save('source_sql_checks.json',checks);save('source_baseline_comparisons.json',comparisons)
    save('exposure_validation.json',dict(monthly_ledgers=len(ledger),sales_rows=len(exposure),python_sql_agreement=True,original_sales_columns_preserved=True,direct_cogs=sum(v['direct'] for v in exposure.values()),support_cogs=sum(v['support'] for v in exposure.values()),allocation='Two-level deterministic largest remainder; monthly direct/support first, then sale-line labor COGS weights.'))
    after=snapshot();save('database_after.json',after);assert before==after
    protected=json.loads((report/'protected_files_before.json').read_text());assert all(hashlib.sha256((ROOT/n).read_bytes()).hexdigest()==v for n,v in protected.items())
    status=dict(status='PASS',read_only=True,dax_executed=False,m_executed=False,csharp_executed=False,scenario_cases=len(cases),periods=3,scenario_period_results=len(results),required_scenario_period_results=24,boundary_and_combination_results=len(results)-24,zero_baseline_comparisons=zero_comparisons,closed_form_delta_comparisons=2*len(results),cost_conservation_checks=len(results),monthly_labor_ledgers=len(ledger),sales_labor_decompositions=len(exposure),sql_python_exposure_agreement=True,original_sales_fields_preserved=True,source_sql_checks=36,source_baseline_comparisons=33,database_tables_unchanged=len(before['tables']),protected_existing_files_unchanged=len(protected),github_finalization_started=False)
    save('reference_validation_summary.json',status);print(json.dumps({'report':str(report),**status},indent=2))
if __name__=='__main__':
    with localcontext() as ctx:
        ctx.prec=48
        main()
