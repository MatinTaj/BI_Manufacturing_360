"""Limited static audit, extracted native SQL execution and in-memory tests.
Not a DAX, M or C# compiler. No Power BI model is opened.
"""
import argparse,hashlib,json,re,subprocess,sys
from decimal import Decimal
from pathlib import Path
PACKAGE=Path(__file__).resolve().parent.parent
ROOT=PACKAGE.parents[1]

def balanced(text,name):
    stack=[];quote=None;i=0
    while i<len(text):
        c=text[i]
        if quote:
            if c==quote:
                if i+1<len(text) and text[i+1]==quote:i+=2;continue
                quote=None
        elif c in ('"',"'"):quote=c
        elif c in '([{':stack.append(c)
        elif c in ')]}':
            assert stack and '([{'.index(stack.pop())==')]}'.index(c),name
        i+=1
    assert not stack and quote is None,name

def main():
    cli=argparse.ArgumentParser();cli.add_argument('--parser-path');args=cli.parse_args()
    if args.parser_path:sys.path.insert(0,args.parser_path)
    from pglast import parser
    assert parser.get_postgresql_version()[0]==18
    report=Path((PACKAGE/'report_path.txt').read_text())
    source_model=json.loads((ROOT/'powerbi/phase9a/model_spec.json').read_text());tables={t['name']:set(t['columns']) for t in source_model['tables']};tables['FactSales'].update(['direct_labor_cogs_exposure_eur','support_labor_cogs_exposure_eur'])
    params=json.loads((PACKAGE/'dax/parameters.json').read_text());oldparams=json.loads((ROOT/'powerbi/phase9a/dax/optional_parameters.json').read_text())
    assert {x['name'] for x in params}=={x['name'] for x in oldparams} and len(params)==6
    for x in params:
        assert x['columns']==['Value'] and x['formula']=='GENERATESERIES(CURRENCY(-0.50), CURRENCY(1.00), CURRENCY(0.01))'
        grid=[Decimal('-.50')+Decimal('.01')*i for i in range(151)]
        assert grid[-1]==1 and 0 in grid and Decimal('.10') in grid and Decimal('.05') in grid
        tables[x['name']]={'Value'}
    old=json.loads((ROOT/'powerbi/phase9a/dax/measures.json').read_text());old_names={m['name'] for m in old if m['optional']};known={m['name'] for m in old if not m['optional']};new=json.loads((PACKAGE/'dax/scenario_measures.json').read_text());assert len(new)==22 and old_names<={m['name'] for m in new}
    refs=0
    for m in new:
        balanced(m['formula'],m['name']);assert set(m['dependencies'])<=known,m['name']
        for t,c in re.findall(r"'([^']+)'\[([^\]]+)\]",m['formula']):assert t in tables and c in tables[t],(m['name'],t,c);refs+=1
        known.add(m['name'])
    by={m['name']:m['formula'] for m in new}
    assert by['Scenario Manufacturing COGS'].count('[Labor COGS]')==1 and by['Scenario Manufacturing COGS'].count('[Direct Labor COGS Exposure]')==1
    assert '[Support Labor COGS Exposure] *' not in by['Scenario Manufacturing COGS']
    assert '[Scenario Outbound Freight]' not in by['Scenario Manufacturing COGS']
    assert by['Scenario Operating Profit'].count('[Scenario Outbound Freight]')==1
    assert by['Scenario Operating Profit'].count('[Scenario Operating Expenses]')==1
    assert '[Scenario Selling Expenses]' not in by['Scenario Operating Profit']
    assert '[Scenario Outbound Freight]' not in by['Scenario Operating Expenses']
    for f in (PACKAGE/'validation').glob('*.sql'):
        tree=json.loads(parser.parse_sql_json(f.read_text()))
        assert all('SelectStmt' in w['stmt'] for w in tree['stmts'])
    for file in (PACKAGE/'validation').glob('*.dax'):
        balanced(re.sub(r'(?m)^//.*$', '', file.read_text()),file.name)
    mtext=(PACKAGE/'power_query/FactSales.m').read_text();balanced(mtext,'FactSales.m')
    match=re.search(r'Source = fxRead\("((?:[^"]|"")*)"\)',mtext);assert match
    native=match.group(1).replace('""','"');sql=(PACKAGE/'validation/fact_sales_scenario_projection.sql').read_text().strip().rstrip(';')
    def normalize(x):
        if isinstance(x,dict):return {k:normalize(v) for k,v in x.items() if k not in ('location','stmt_location','stmt_len')}
        if isinstance(x,list):return [normalize(v) for v in x]
        return x
    assert normalize(json.loads(parser.parse_sql_json(native)))==normalize(json.loads(parser.parse_sql_json(sql)))
    cmd=['C:/Program Files/PostgreSQL/18/bin/psql.exe','-X','-w','-h','localhost','-p','5432','-U','postgres','-d','manufacturing_360','-v','ON_ERROR_STOP=1','-At','-f','-']
    run=subprocess.run(cmd,input="BEGIN READ ONLY; SELECT jsonb_build_object('rows',count(*),'unique_sales_ids',count(DISTINCT sales_line_id),'valid_rows',count(*) FILTER(WHERE direct_labor_exposure_valid),'labor_difference',sum(labor_cogs_eur-direct_labor_cogs_exposure_eur-support_labor_cogs_exposure_eur)) FROM ("+native+") q; COMMIT;",capture_output=True,text=True)
    if run.returncode:raise RuntimeError(run.stderr)
    native_result=next(json.loads(l) for l in run.stdout.splitlines() if l.startswith('{'));assert native_result['rows']==native_result['unique_sales_ids']==native_result['valid_rows']==2596 and native_result['labor_difference']==0
    test=subprocess.run([sys.executable,'-B','-m','unittest','discover','-s',str(PACKAGE/'validation'),'-p','test_reference.py','-v'],capture_output=True,text=True)
    (report/'unit_test_results.txt').write_text(test.stdout+test.stderr,encoding='utf-8');assert test.returncode==0
    result=dict(status='PASS',kind='Static reference/structure checks plus read-only native SQL and Python tests',dax_engine_executed=False,m_engine_executed=False,csharp_compiled=False,parameter_tables_reused=6,new_parameter_tables=0,parameter_grid_values=151,existing_scenario_measures_reused=14,new_measures=8,scenario_measure_count=22,direct_dax_column_references_checked=refs,native_sql_matches_prepared_projection=True,native_sql_result=native_result,in_memory_tests_passed=15)
    (report/'static_audit_results.json').write_text(json.dumps(result,indent=2)+'\n',encoding='utf-8');print(json.dumps(result,indent=2))
if __name__=='__main__':main()
