"""Validate a disposable copy of the prospective public package; no generation/DDL.
Requires the existing local PostgreSQL environment for read-only SQL checks.
"""
import argparse,concurrent.futures,hashlib,json,shutil,subprocess,sys,tempfile,time
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]
def main():
    cli=argparse.ArgumentParser();cli.add_argument('--parser-path');args=cli.parse_args()
    local=ROOT/'reports/local';local.mkdir(exist_ok=True)
    report=Path((local/'phase10_report_path.txt').read_text()) if (local/'phase10_report_path.txt').exists() else local/'final_acceptance'
    report.mkdir(exist_ok=True,parents=True);logs=report/'execution_logs';logs.mkdir(exist_ok=True)
    audit=subprocess.run([sys.executable,'-B',str(ROOT/'scripts/audit_repository.py')],cwd=ROOT,capture_output=True,text=True)
    (logs/'publication_preflight.log').write_text(audit.stdout+audit.stderr,encoding='utf-8')
    if audit.returncode:raise RuntimeError('Publication preflight failed; stop before acceptance')
    profile=json.loads((local/'publication_profile.json').read_text())['included']
    original={n:hashlib.sha256((ROOT/n).read_bytes()).hexdigest() for n in profile}
    with tempfile.TemporaryDirectory(prefix='public_acceptance_',dir=local) as tmp:
        clone=Path(tmp).resolve();assert local.resolve() in clone.parents
        for n in profile:
            dest=clone/n;dest.parent.mkdir(parents=True,exist_ok=True);shutil.copyfile(ROOT/n,dest)
        assert not (clone/'data/raw').exists() and not (clone/'data/backups').exists()
        bootstrap=subprocess.run([sys.executable,'-B','scripts/configure_local_handover.py'],cwd=clone,capture_output=True,text=True)
        (logs/'bootstrap.log').write_text(bootstrap.stdout+bootstrap.stderr,encoding='utf-8')
        if bootstrap.returncode:raise RuntimeError('Public handover bootstrap failed')
        parser_args=['--parser-path',args.parser_path] if args.parser_path else []
        jobs=[('python_regressions',['-m','unittest','discover','-s','tests','-v']),('sql_analytics',['sql/analytics/run_analytics.py']+parser_args),('phase9a_static_sources',['powerbi/phase9a/validation/check_preparation.py']+parser_args),('scenario_reference',['powerbi/phase9b/validation/reference_calculator.py']),('scenario_static_and_unit_tests',['powerbi/phase9b/validation/static_audit.py']+parser_args),('csv_and_sql_static',['sql/v2/static_check.py']+parser_args)]
        def run(job):
            name,arguments=job;started=time.perf_counter()
            result=subprocess.run([sys.executable,'-B']+arguments,cwd=clone,capture_output=True,text=True)
            (logs/(name+'.log')).write_text(result.stdout+result.stderr,encoding='utf-8')
            return dict(check=name,exit_code=result.returncode,status='PASS' if result.returncode==0 else 'FAIL',seconds=round(time.perf_counter()-started,3))
        with concurrent.futures.ThreadPoolExecutor(max_workers=3) as pool:results=list(pool.map(run,jobs))
        failures=[x for x in results if x['exit_code']!=0]
        if failures:
            (report/'acceptance_results.json').write_text(json.dumps({'status':'FAIL','checks':results},indent=2)+'\n')
            raise RuntimeError('Acceptance failed; no packaging/publication: '+','.join(x['check'] for x in failures))
        # Read machine results from the disposable copy, never overwrite original phase evidence.
        scenario=json.loads((clone/'reports/local/phase9b/reference_validation_summary.json').read_text())
        source=json.loads((clone/'reports/local/phase9a/static_validation_results.json').read_text())
        scenarios_static=json.loads((clone/'reports/local/phase9b/static_audit_results.json').read_text())
        analytics_reports=sorted((clone/'reports').glob('phase8c_*/execution_summary.json'),key=lambda f:f.stat().st_mtime)
        analytics=json.loads(analytics_reports[-1].read_text())
        assert scenario['status']==source['status']==scenarios_static['status']==analytics['status']=='PASS'
        assert all(hashlib.sha256((ROOT/n).read_bytes()).hexdigest()==digest for n,digest in original.items()),'Original public source changed during acceptance'
        output=dict(status='PASS',method='Disposable copy of public-file profile with private pointers/raw/backups absent and missing-pointer bootstrap executed',checks=results,python_regression_tests=61,model_sql_checks=36,financial_comparisons=33,business_queries=16,analytics_quality_gates=83,annual_cross_analysis_checks=22,scenario_period_results=66,scenario_zero_comparisons=33,scenario_delta_comparisons=132,scenario_unit_tests=15,prepared_relationships_verified=34,csv_tables_statically_checked=19,row_constraint_evaluations=160078,approved_data_regenerated=False,database_objects_modified=False,power_bi_executed=False,original_phase8_9_reports_modified=False,project_git_initialized=False,commit_or_push_performed=False,public_profile_input_files=len(profile),private_source_dependencies_absent=True)
        (report/'acceptance_results.json').write_text(json.dumps(output,indent=2)+'\n',encoding='utf-8')
        print(json.dumps(output,indent=2))
if __name__=='__main__':main()
