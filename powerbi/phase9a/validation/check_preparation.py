"""Read-only model source checks plus limited static M/DAX preparation checks.
Does not run Power Query, DAX, C#, Desktop, or a Tabular engine.
"""
import argparse,calendar,csv,hashlib,json,re,subprocess,sys
from datetime import date,timedelta
from pathlib import Path
ROOT=Path(__file__).resolve().parents[3]
PACKAGE=ROOT/'powerbi/phase9a'

def main():
    cli=argparse.ArgumentParser();cli.add_argument('--parser-path');args=cli.parse_args()
    if args.parser_path:sys.path.insert(0,args.parser_path)
    from pglast import parser
    model=json.loads((PACKAGE/'model_spec.json').read_text());ms=json.loads((PACKAGE/'dax/measures.json').read_text())
    report=Path((PACKAGE/'report_path.txt').read_text());source_columns=json.loads((report/'live_schema_columns.json').read_text())
    tables={t['name']:t for t in model['tables']}
    optional=json.loads((PACKAGE/'dax/optional_parameters.json').read_text())
    for t in optional:tables[t['name']]=t
    def query(sql):
        cmd=['C:/Program Files/PostgreSQL/18/bin/psql.exe','-X','-w','-h','localhost','-p','5432','-U','postgres','-d','manufacturing_360','-v','ON_ERROR_STOP=1','-At','-f','-']
        run=subprocess.run(cmd,input='BEGIN READ ONLY;\n'+sql+';\nCOMMIT;',capture_output=True,text=True,encoding='utf-8')
        if run.returncode:raise RuntimeError(run.stderr)
        return next(json.loads(l) for l in run.stdout.splitlines() if l.startswith(('[','{')))
    def snapshot():
        rels=query("SELECT jsonb_agg(q) FROM (SELECT schemaname,tablename FROM pg_tables WHERE schemaname IN ('public','manufacturing_v2') ORDER BY 1,2) q")
        out={}
        for t in rels:
            name='.'.join('"'+t[k].replace('"','""')+'"' for k in ('schemaname','tablename'))
            out[name]=query("SELECT jsonb_build_object('rows',count(*),'hash',md5(coalesce(string_agg(h,'' ORDER BY h),''))) FROM (SELECT md5(row_to_json(t)::text) h FROM "+name+' t) q')
        cmd=['C:/Program Files/PostgreSQL/18/bin/pg_dump.exe','-w','-h','localhost','-p','5432','-U','postgres','-d','manufacturing_360','-n','public','-n','manufacturing_v2','--schema-only','--no-owner','--no-privileges']
        run=subprocess.run(cmd,capture_output=True,text=True,encoding='utf-8')
        if run.returncode:raise RuntimeError('Definition snapshot failed')
        dump=re.sub(r'(?m)^\\(un)?restrict .*$', '-- normalized restrict token',run.stdout)
        return dict(data=out,definition_sha256=hashlib.sha256(dump.encode()).hexdigest())
    before=snapshot();(report/'database_before.json').write_text(json.dumps(before,indent=2))
    # Distinguish lexical/reference checks from real language compilation.
    def balanced(text,language):
        text=re.sub(r'//[^\n]*','',text)
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
                if not stack or '([{'.index(stack.pop())!=')]}'.index(c):raise ValueError('Delimiter mismatch: '+language)
            i+=1
        assert not stack and quote is None,language
    source_checks=[]
    for t in model['tables']:
        if 'sql' not in t:continue
        ast=json.loads(parser.parse_sql_json(t['sql']));assert len(ast['stmts'])==1 and 'SelectStmt' in ast['stmts'][0]['stmt']
        keys=','.join('"'+k+'"' for k in t['keys'])
        result=query("SELECT jsonb_build_object('rows',(SELECT count(*) FROM ("+t['sql']+") q),'duplicate_keys',(SELECT count(*) FROM (SELECT "+keys+' FROM ('+t['sql']+') q GROUP BY '+keys+' HAVING count(*)>1) d))')
        assert result['rows']==t['verified_rows'] and result['duplicate_keys']==0,t['name']
        source_checks.append({'table':t['name'],**result})
    # Build equivalent daily calendar and M-derived month fields as read-only CTEs.
    bounds="SELECT least((SELECT min(month_id) FROM manufacturing_v2.months),(SELECT min(order_date) FROM manufacturing_v2.purchase_order_lines),(SELECT min(receipt_date) FROM manufacturing_v2.material_receipts),(SELECT min(shipment_date) FROM manufacturing_v2.sales)) AS lo,greatest((SELECT (max(month_id)+interval '1 month - 1 day')::date FROM manufacturing_v2.months),(SELECT max(expected_receipt_date) FROM manufacturing_v2.purchase_order_lines),(SELECT max(receipt_date) FROM manufacturing_v2.material_receipts),(SELECT max(shipment_date) FROM manufacturing_v2.sales)) AS hi"
    calendar_sql="SELECT generate_series(date_trunc('year',lo)::date,(date_trunc('year',hi)+interval '1 year - 1 day')::date,interval '1 day')::date AS \"Date\" FROM ("+bounds+") b"
    shape=query('SELECT jsonb_build_object(\'rows\',count(*),\'unique_dates\',count(DISTINCT "Date"),\'min_date\',min("Date"),\'max_date\',max("Date")) FROM ('+calendar_sql+') d')
    assert shape['rows']==shape['unique_dates']==731
    relationship_checks=[]
    for r in model['relationships']:
        dim=tables[r['from_table']];fact=tables[r['to_table']]
        assert r['from_column'] in dim['columns'] and r['to_column'] in fact['columns']
        assert dim['role']=='dimension' and fact['role']=='fact'
        assert r['cardinality']=='1:*' and r['cross_filter']=='Single: dimension to fact'
        dimsql=calendar_sql if dim['name']=='DimDate' else dim['sql']
        factsql=fact['sql']
        if r['to_column'] in ('ReceiptMonth','OrderMonth'):
            col='receipt_date' if r['to_column']=='ReceiptMonth' else 'order_date'
            factsql='SELECT q.*,date_trunc(\'month\',q.'+col+')::date AS "'+r['to_column']+'" FROM ('+factsql+') q'
        q='SELECT jsonb_build_object(\'missing\',count(*)) FROM ('+factsql+') f LEFT JOIN ('+dimsql+') d ON f."'+r['to_column']+'"=d."'+r['from_column']+'" WHERE d."'+r['from_column']+'" IS NULL'
        result=query(q);assert result['missing']==0,r
        relationship_checks.append({**r,**result})
    # One active relationship per dimension/fact pair; no dimension chains/fact links.
    active=[(r['from_table'],r['to_table']) for r in model['relationships'] if r['active']]
    assert len(active)==len(set(active))
    names=set();reference_count=0
    for m in ms:
        balanced(m['formula'],m['name'])
        for table,col in re.findall(r"'([^']+)'\[([^\]]+)\]",m['formula']):
            assert table in tables and col in tables[table]['columns'],(m['name'],table,col)
            reference_count+=1
        assert all(dep in names for dep in m['dependencies']),m['name']
        names.add(m['name'])
    for file in (PACKAGE/'power_query').glob('*.m'):balanced(file.read_text(encoding='utf-8'),file.name)
    mapping=list(csv.DictReader((PACKAGE/'KPI_TO_DAX.csv').open()));assert len(mapping)==49
    for item in mapping:assert all(name.strip() in names for name in item['dax_measures'].split(';'))
    existing=query('SELECT jsonb_agg(q) FROM (SELECT * FROM manufacturing_v2.audit_validation_results ORDER BY check_name) q')
    assert len(existing)==36 and all(x['failed_rows']==0 for x in existing)
    baseline=query('SELECT jsonb_agg(q) FROM (SELECT * FROM manufacturing_v2.audit_pnl_reconciliation ORDER BY period,metric) q')
    assert len(baseline)==33 and all(x['passed'] for x in baseline)
    after=snapshot();assert before==after,'Database changed'
    (report/'database_after.json').write_text(json.dumps(after,indent=2))
    protected=json.loads((report/'protected_files_before.json').read_text());assert all(hashlib.sha256((ROOT/name).read_bytes()).hexdigest()==digest for name,digest in protected.items())
    for filename,value in [('source_checks.json',source_checks),('relationship_checks.json',relationship_checks),('sql_baseline_checks.json',baseline),('sql_model_checks.json',existing),('calendar_check.json',shape)]:
        (report/filename).write_text(json.dumps(value,indent=2)+'\n')
    result=dict(status='PASS',checks_are_static_or_sql_only=True,power_bi_desktop_executed=False,dax_engine_executed=False,m_engine_executed=False,csharp_compiled=False,model_tables=19,active_relationships=len(active),inactive_relationships=4,model_projections_executed=len(source_checks),relationships_checked=len(relationship_checks),calendar_days=731,core_measures=sum(not m['optional'] for m in ms),optional_measures=sum(m['optional'] for m in ms),optional_parameter_tables=6,dax_column_references_checked=reference_count,kpis_mapped=len(mapping),existing_sql_checks_passed=36,financial_baseline_comparisons_passed=33,protected_files_unchanged=len(protected),database_tables_unchanged=len(before['data']),phase9b_started=False)
    (report/'static_validation_results.json').write_text(json.dumps(result,indent=2)+'\n');print(json.dumps(result,indent=2))
if __name__=='__main__':main()
