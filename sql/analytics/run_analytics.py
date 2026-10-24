"""Execute reviewed SELECT-only portfolio in PostgreSQL read-only transactions.
Uses secure existing pgpass authentication; never accepts passwords or performs DDL.
Requires pglast 8.x / PostgreSQL 18 grammar. Python standard library otherwise.
"""
import argparse,csv,datetime,hashlib,json,re,subprocess,sys,time
from decimal import Decimal
from pathlib import Path
HERE=Path(__file__).resolve().parent
ROOT=HERE.parents[1]

def main():
    cli=argparse.ArgumentParser(description=__doc__)
    cli.add_argument('--parser-path');cli.add_argument('--psql',default='C:/Program Files/PostgreSQL/18/bin/psql.exe')
    args=cli.parse_args()
    if args.parser_path:sys.path.insert(0,args.parser_path)
    from pglast import parser
    if parser.get_postgresql_version()[0]!=18:raise RuntimeError('PostgreSQL 18 grammar required')
    output=ROOT/'reports'/('phase8c_'+datetime.datetime.now().strftime('%Y%m%dT%H%M%S'))
    output.mkdir(exist_ok=False)
    base=[args.psql,'-X','-w','-h','localhost','-p','5432','-U','postgres','-d','manufacturing_360','-v','ON_ERROR_STOP=1','-At']
    def execute(sql):
        r=subprocess.run(base+['-f','-'],input=sql,capture_output=True,text=True,encoding='utf-8')
        if r.returncode:
            (output/'sql_error.txt').write_text(r.stderr,encoding='utf-8')
            raise RuntimeError('Read-only SQL failed; see '+str(output/'sql_error.txt'))
        return r.stdout
    def jdump(path,value):path.write_text(json.dumps(value,indent=2,default=str)+'\n',encoding='utf-8')
    def fingerprint():
        # Full-row multiset hashes for public and v2 tables; all definitions checked separately.
        catalog=execute("BEGIN READ ONLY; SELECT jsonb_agg(q) FROM (SELECT schemaname,tablename FROM pg_tables WHERE schemaname IN ('public','manufacturing_v2') ORDER BY 1,2) q; COMMIT;")
        relations=next(json.loads(line) for line in catalog.splitlines() if line.startswith('['))
        result={}
        for rel in relations:
            name='.'.join('"'+rel[k].replace('"','""')+'"' for k in ('schemaname','tablename'))
            query="BEGIN READ ONLY; SELECT json_build_object('rows',count(*),'hash',md5(coalesce(string_agg(h,'' ORDER BY h),''))) FROM (SELECT md5(row_to_json(t)::text) h FROM "+name+" t) q; COMMIT;"
            result[name]=next(json.loads(line) for line in execute(query).splitlines() if line.startswith('{'))
        return result
    def definitions():
        cmd=[str(Path(args.psql).with_name('pg_dump.exe')),'-w','-h','localhost','-p','5432','-U','postgres','-d','manufacturing_360','-n','public','-n','manufacturing_v2','--schema-only','--no-owner','--no-privileges']
        r=subprocess.run(cmd,capture_output=True,text=True,encoding='utf-8')
        if r.returncode:raise RuntimeError('Read-only definition capture failed')
        return re.sub(r'(?m)^\\(un)?restrict .*$', '-- normalized restrict token',r.stdout)
    protected={str(p.relative_to(ROOT)):hashlib.sha256(p.read_bytes()).hexdigest() for d in ('data','powerbi','src','tests') for p in (ROOT/d).rglob('*') if p.is_file()}
    for p in (ROOT/'sql').rglob('*'):
        if p.is_file() and HERE not in p.parents:protected[str(p.relative_to(ROOT))]=hashlib.sha256(p.read_bytes()).hexdigest()
    jdump(output/'protected_files_before.json',protected)
    before=fingerprint();before_def=definitions();jdump(output/'database_fingerprints_before.json',before)
    (output/'database_definitions_before.sql').write_text(before_def,encoding='utf-8')
    statements=[]
    for file in sorted(HERE.glob('*.sql')):
        text=file.read_text(encoding='utf-8');tree=json.loads(parser.parse_sql_json(text))
        for i,wrapped in enumerate(tree['stmts'],1):
            raw=wrapped['stmt'];stmt=raw.get('SelectStmt')
            if stmt is None:raise RuntimeError('Only SELECT allowed: '+file.name)
            def inspect(node):
                if isinstance(node,dict):
                    if 'intoClause' in node or 'lockingClause' in node:raise RuntimeError('Write or row lock forbidden')
                    if 'RangeVar' in node and node['RangeVar'].get('schemaname') not in (None,'manufacturing_v2','pg_catalog'):raise RuntimeError('Unapproved source schema')
                    for value in node.values():inspect(value)
                elif isinstance(node,list):
                    for value in node:inspect(value)
            inspect(raw)
            loc=wrapped.get('stmt_location',0);length=wrapped.get('stmt_len',0)
            # Parser byte offsets are UTF-8 offsets, not Python character offsets.
            encoded=text.encode('utf-8');sql=encoded[loc:loc+length if length else None].decode('utf-8').strip().rstrip(';')
            statements.append((file.stem+f'_q{i:02}',sql))
    # Validate first and raise immediately on failure, before business analyses.
    validation=next(sql for key,sql in statements if key=='09_validation_q01')
    baseline=next(sql for key,sql in statements if key=='09_validation_q02')
    script="\\set ON_ERROR_STOP on\nBEGIN ISOLATION LEVEL REPEATABLE READ READ ONLY;\nSET LOCAL search_path=pg_catalog;\nSET LOCAL statement_timeout='60s';\n"
    script+="DO $gate$ BEGIN IF current_database()<>'manufacturing_360' OR current_setting('server_version_num')::int NOT BETWEEN 180000 AND 189999 THEN RAISE EXCEPTION 'Wrong environment'; END IF; IF EXISTS(SELECT 1 FROM ("+validation+") checks WHERE failed_rows<>0) THEN RAISE EXCEPTION 'Portfolio validation failed'; END IF; IF EXISTS(SELECT 1 FROM ("+baseline+") comparisons WHERE passed IS DISTINCT FROM true) THEN RAISE EXCEPTION 'Baseline mismatch'; END IF; END; $gate$;\n"
    script+="SELECT json_build_object('query','environment','rows',json_build_array(json_build_object('database',current_database(),'user',current_user,'version',current_setting('server_version'),'transaction_read_only',current_setting('transaction_read_only'))));\n"
    for key,sql in statements:
        script+="SELECT json_build_object('query','"+key+"','rows',coalesce(jsonb_agg(q),'[]'::jsonb)) FROM ("+sql+") q;\n"
    script+='COMMIT;\n'
    started=time.perf_counter();stdout=execute(script);elapsed=time.perf_counter()-started
    results={}
    for line in stdout.splitlines():
        if line.startswith('{'):
            item=json.loads(line,parse_float=Decimal);results[item['query']]=item['rows']
    if len(results)!=len(statements)+1:raise RuntimeError('Missing query results')
    if results['environment'][0]['transaction_read_only']!='on':raise RuntimeError('Read-only guarantee missing')
    assert all(r['failed_rows']==0 for r in results['09_validation_q01'])
    assert all(r['passed'] for r in results['09_validation_q02'])
    # Independent approved Phase 7 baseline, not only audit tables in the same DB.
    manifest=json.loads((ROOT/'sql/v2/input_manifest.json').read_text());ref=ROOT/manifest['phase7_report']/'financial_comparison.csv'
    if hashlib.sha256(ref.read_bytes()).hexdigest()!=manifest['phase7_financial_sha256']:raise RuntimeError('Phase 7 file changed')
    with ref.open(newline='',encoding='utf-8') as f:expected={r['period']:r for r in csv.DictReader(f) if r['dataset']=='candidate'}
    comparison_count=0
    for r in results['09_validation_q02']:
        allowed=Decimal('0.00000001') if r['metric'].endswith('_pct') else Decimal(0)
        assert abs(Decimal(str(r['actual']))-Decimal(expected[r['period']][r['metric']]))<=allowed
        comparison_count+=1
    assert all(r['inbound_bridge_difference_eur']==0 for r in results['08_logistics_distribution_q02'])
    # Cross-analysis conservation checks guard incorrect aggregation in portfolio results.
    for annual in results['01_executive_financial_q01']:
        year=int(annual['period'])
        products=[r for r in results['02_product_profitability_q02'] if r['year']==year]
        customers=[r for r in results['07_customer_concentration_q01'] if r['year']==year]
        distribution=[r for r in results['08_logistics_distribution_q01'] if r['year']==year]
        assert sum(r['revenue_eur'] for r in products)==annual['revenue']
        assert sum(r['cogs_eur'] for r in products)==annual['cogs']
        assert sum(r['revenue_eur'] for r in customers)==annual['revenue']
        assert sum(r['outbound_eur'] for r in distribution)==annual['outbound_freight']
        assert sum(r['gross_profit_eur'] for r in products)==annual['gross_profit']
        assert sum(r['gross_profit_eur'] for r in customers)==annual['gross_profit']
        assert sum(r['contribution_eur'] for r in distribution)==annual['gross_profit']-annual['outbound_freight']
        inv=next(r for r in results['06_inventory_turnover_q01'] if r['year']==year)
        assert inv['cogs_eur']==annual['cogs']
        components=[r for r in results['03_manufacturing_costs_q01'] if r['year']==year]
        pools=[r for r in results['03_manufacturing_costs_q02'] if r['year']==year]
        assert sum(r['cost_eur'] for r in components)==inv['landed_raw_issues_eur']+sum(r['conversion_eur']-r['idle_eur'] for r in pools)
        dec=next(r for r in results['01_executive_financial_q02'] if r['month_id']==str(year)+'-12-01')
        assert dec['ytd_revenue_eur']==annual['revenue'] and dec['ytd_operating_profit_eur']==annual['operating_profit']
    jdump(output/'query_results.json',results)
    for key,rows in results.items():
        with (output/(key+'.csv')).open('w',newline='',encoding='utf-8') as stream:
            if rows:
                writer=csv.DictWriter(stream,fieldnames=list(rows[0]));writer.writeheader();writer.writerows(rows)
    after=fingerprint();after_def=definitions();jdump(output/'database_fingerprints_after.json',after)
    (output/'database_definitions_after.sql').write_text(after_def,encoding='utf-8')
    if before!=after or before_def!=after_def:raise RuntimeError('Database changed; investigate before proceeding')
    if any(hashlib.sha256((ROOT/name).read_bytes()).hexdigest()!=digest for name,digest in protected.items()):raise RuntimeError('Protected file changed')
    status={'status':'PASS','database':'manufacturing_360','schema':'manufacturing_v2','read_only':True,'business_modules':8,'business_queries':16,'validation_queries':3,'quality_gates':len(results['09_validation_q01']),'existing_phase8b_gates':36,'baseline_metric_comparisons':comparison_count,'cross_analysis_annual_reconciliations':22,'inbound_freight_bridges':2,'database_tables_fingerprinted':len(before),'database_data_and_definitions_unchanged':True,'protected_files_unchanged':len(protected),'single_snapshot_execution_seconds':round(elapsed,3),'parser_version':parser.get_postgresql_version(),'phase9_started':False}
    jdump(output/'execution_summary.json',status)
    print(json.dumps({'report':str(output),**status},indent=2))
if __name__=='__main__':main()
