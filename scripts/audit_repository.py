"""Non-destructive publication audit and optional offline handover ZIP.
Never initializes the project Git repository, commits, pushes or touches PostgreSQL.
Secret findings report locations/categories only, never matched values.
"""
import argparse,hashlib,json,re,subprocess,tempfile,zipfile
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]

def main():
    cli=argparse.ArgumentParser();cli.add_argument('--build-handover',action='store_true');args=cli.parse_args()
    local=ROOT/'reports/local';local.mkdir(exist_ok=True)
    report=Path((local/'phase10_report_path.txt').read_text()) if (local/'phase10_report_path.txt').exists() else local/'publication_audit'
    report.mkdir(parents=True,exist_ok=True)
    files=[p for p in ROOT.rglob('*') if p.is_file() and not any(x in p.parts for x in ('.git','.venv','__pycache__')) and ROOT/'handover' not in p.parents and local not in p.parents]
    names=[p.relative_to(ROOT).as_posix() for p in files]
    # Only this disposable scratch repository is initialized to validate ignore semantics.
    with tempfile.TemporaryDirectory(prefix='gitignore_audit_',dir=local) as tmp:
        scratch=Path(tmp).resolve();assert local.resolve() in scratch.parents
        subprocess.run(['git','init','-q',str(scratch)],check=True,capture_output=True)
        (scratch/'.gitignore').write_bytes((ROOT/'.gitignore').read_bytes())
        probes=['.env','pgpass.conf','private.pem','data/backups/example.csv','powerbi/example.pbix','powerbi/phase9a/report_path.txt','reports/local/private.json','data/staging/sales.csv','data/processed/sales.csv','powerbi/phase9b/power_query/FactSales.m','reports/phase7_20261024T141247792082+0200/financial_comparison.csv']
        def ignored(paths):
            proc=subprocess.run(['git','-C',str(scratch),'check-ignore','--no-index','-z','--stdin'],input=('\0'.join(paths)+'\0').encode('utf-8'),capture_output=True)
            if proc.returncode not in (0,1):raise RuntimeError('Ignore-rule check failed')
            return set(proc.stdout.decode('utf-8').split('\0'))-{''}
        excluded=ignored(names);probe_ignored=ignored(probes)
        assert all(p in probe_ignored for p in probes[:7]) and all(p not in probe_ignored for p in probes[7:])
    public={n:p for n,p in zip(names,files) if n not in excluded}
    findings=[];binary_uninspected=[];local_paths=[]
    patterns={'private_key':r'-----BEGIN (?:RSA |EC |OPENSSH )?PRIVATE KEY-----','github_token':r'\b(?:ghp_[A-Za-z0-9]{30,}|github_pat_[A-Za-z0-9_]{40,})','aws_key':r'\bAKIA[0-9A-Z]{16}\b','credential_url':r'postgres(?:ql)?://[^\s/:]+:[^\s@]+@','literal_password':r'(?im)(?:password|passwd|PGPASSWORD)\s*[=:]\s*["\x27]([^"\x27\r\n]{4,})["\x27]'}
    for n,p in zip(names,files):
        try:text=p.read_text(encoding='utf-8-sig')
        except (UnicodeError,OSError):
            binary_uninspected.append(n);continue
        for kind,pattern in patterns.items():
            for match in re.finditer(pattern,text):
                value=match.group(1) if kind=='literal_password' else ''
                if value and any(marker in value.lower() for marker in ('your_password','your-password','placeholder','example','${','<')):continue
                findings.append(dict(file=n,kind=kind,line=text.count('\n',0,match.start())+1,public=n in public))
        # Normalize JSON escaping for path detection, never print path values.
        normalized=text.replace('\\\\','\\')
        if re.search(r'[A-Z]:[\\/](?:Users|GitHub|Program Files)',normalized):
            local_paths.append(dict(file=n,public=n in public,personal_home_path=bool(re.search(r'[A-Z]:[\\/]Users[\\/]',normalized))))
    if findings:
        (report/'security_STOP.json').write_text(json.dumps({'status':'STOP','candidate_locations_only':findings},indent=2))
        raise RuntimeError('Credential candidates found; stopped. Inspect the private location-only report; no values printed.')
    public_home=[x for x in local_paths if x['public'] and x['personal_home_path']]
    if public_home:raise RuntimeError('Personal home path in prospective publication; review exclusions')
    broken=[];excluded_links=[]
    for n,p in zip(names,files):
        if p.suffix!='.md' or p.name.startswith('original_'):continue
        for target in re.findall(r'\]\(([^)]+)\)',p.read_text(encoding='utf-8')):
            if target.startswith(('http:','https:','#','mailto:')):continue
            target=target.strip('<>').split('#')[0]
            if not target:continue
            dest=(p.parent/target).resolve()
            if not dest.exists():broken.append(dict(file=n,target=target))
            elif n in public and ROOT in dest.parents and dest.is_file() and dest.relative_to(ROOT).as_posix() not in public:excluded_links.append(dict(file=n,target=target))
    if broken or excluded_links:raise RuntimeError('Documentation/public-profile link check failed: '+json.dumps(broken+excluded_links))
    oversized=[dict(file=n,bytes=p.stat().st_size) for n,p in zip(names,files) if p.stat().st_size>=50*1024*1024]
    if any(x['bytes']>=100*1024*1024 and x['file'] in public for x in oversized):raise RuntimeError('GitHub oversized public artifact')
    git=subprocess.run(['git','-C',str(ROOT),'rev-parse','--is-inside-work-tree'],capture_output=True,text=True)
    git_state={'initialized':git.returncode==0,'branch':None,'remote':None,'tracked_file_count':None,'untracked_file_count':None}
    if git.returncode==0:
        git_state['branch']=subprocess.run(['git','-C',str(ROOT),'branch','--show-current'],capture_output=True,text=True,check=True).stdout.strip()
        tracked=subprocess.run(['git','-C',str(ROOT),'ls-files'],capture_output=True,text=True,check=True).stdout.splitlines();git_state['tracked_file_count']=len(tracked)
        untracked=subprocess.run(['git','-C',str(ROOT),'ls-files','--others','--exclude-standard'],capture_output=True,text=True,check=True).stdout.splitlines();git_state['untracked_file_count']=len(untracked)
        remote=subprocess.run(['git','-C',str(ROOT),'remote','get-url','origin'],capture_output=True,text=True)
        value=remote.stdout.strip()
        # Only report an ordinary credential-free GitHub repository URL.
        git_state['remote']=value if re.fullmatch(r'(?:https://github\.com/|git@github\.com:)[A-Za-z0-9_.-]+/[A-Za-z0-9_.-]+(?:\.git)?',value) else ('configured; inspect locally' if value else None)
        if set(tracked)&excluded:raise RuntimeError('Ignored private artifact is already tracked; stop and review index/history manually')
    result=dict(status='PASS',scope='Pattern-based text scan and prospective Git/public profile; not a forensic secret or binary/history certification',files_scanned=len(files),total_bytes=sum(p.stat().st_size for p in files),public_file_count=len(public),excluded_file_count=len(excluded),credential_candidates=0,personal_home_paths_in_public=0,broken_local_markdown_links=0,links_to_excluded_public_targets=0,large_files_50mib=oversized,binary_files_not_text_inspected=binary_uninspected,git=git_state,ignore_probe_count=len(probes),database_touched=False,project_git_initialized=False)
    (report/'audit_summary.json').write_text(json.dumps(result,indent=2)+'\n',encoding='utf-8')
    # Inventory contains relative filenames and hashes only, never matched secret values.
    inventory={'included':{n:hashlib.sha256(p.read_bytes()).hexdigest() for n,p in public.items()},'excluded':sorted(excluded)}
    (local/'publication_profile.json').write_text(json.dumps(inventory,indent=2)+'\n',encoding='utf-8')
    if args.build_handover:
        dest=ROOT/'handover';dest.mkdir(exist_ok=True);archive=dest/'Manufacturing_360_PowerBI_Handover.zip'
        if archive.exists():raise FileExistsError('Existing handover archive preserved; choose an explicit new name/version before rebuilding')
        with zipfile.ZipFile(archive,'x',compression=zipfile.ZIP_DEFLATED) as out:
            for n,p in sorted(public.items()):out.write(p,n)
            out.writestr('HANDOVER_MANIFEST.json',json.dumps(inventory['included'],indent=2)+'\n')
        with zipfile.ZipFile(archive) as packaged:
            manifest=json.loads(packaged.read('HANDOVER_MANIFEST.json'))
            assert all(hashlib.sha256(packaged.read(n)).hexdigest()==digest for n,digest in manifest.items())
            assert 'docs/POWER_BI_START_HERE.md' in manifest and len([n for n in manifest if n.startswith('data/staging/') and n.endswith('.csv')])==19
            assert not any(n.endswith('.pbix') or n.startswith(('data/raw/','data/backups/')) or n.endswith('/report_path.txt') for n in manifest)
            # Crosscheck every Markdown link inside the ZIP itself.
            for n in manifest:
                if not n.endswith('.md'):continue
                for link in re.findall(r'\]\(([^)]+)\)',packaged.read(n).decode('utf-8')):
                    if link.startswith(('http:','https:','#','mailto:')):continue
                    import posixpath
                    link=link.strip('<>').split('#')[0]
                    if link:assert posixpath.normpath(posixpath.join(posixpath.dirname(n),link)) in manifest,(n,link)
        checksum=hashlib.sha256(archive.read_bytes()).hexdigest()
        (dest/'SHA256.txt').write_text(checksum+'  '+archive.name+'\n',encoding='utf-8')
        (local/'handover_validation.json').write_text(json.dumps({'status':'PASS','archive':'handover/'+archive.name,'sha256':checksum,'entries':len(manifest),'bytes':archive.stat().st_size,'manifest_hashes_verified':True,'internal_markdown_links_verified':True,'third_party_installers_or_wheels_bundled':False},indent=2)+'\n',encoding='utf-8')
    print(json.dumps(result,indent=2))
if __name__=='__main__':main()
