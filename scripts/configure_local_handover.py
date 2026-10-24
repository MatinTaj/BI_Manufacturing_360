"""Create only missing ignored local report pointers for an extracted/clone handover.
No database access and no overwrites of existing Phase 8/9 deliverables.
"""
from pathlib import Path
import hashlib,json,shutil
ROOT=Path(__file__).resolve().parents[1]
def main():
    pending=[]
    for phase in ('phase9a','phase9b'):
        pointer=ROOT/'powerbi'/phase/'report_path.txt'
        if pointer.exists():
            print(phase+': existing pointer preserved');continue
        target=ROOT/'reports/local'/phase;target.mkdir(parents=True,exist_ok=True)
        if phase=='phase9a':
            source=ROOT/'reports/phase9a_20261024T233001/live_schema_columns.json'
            if not source.exists():raise FileNotFoundError('Required public live_schema_columns.json evidence is missing')
            destination=target/'live_schema_columns.json'
            if not destination.exists():shutil.copyfile(source,destination)
        pointer.write_text(str(target),encoding='utf-8')
        pending.append(target)
        print(phase+': created ignored machine-local pointer')
    if pending:
        snapshot={str(p.relative_to(ROOT)):hashlib.sha256(p.read_bytes()).hexdigest() for p in ROOT.rglob('*') if p.is_file() and not any(x in p.parts for x in ('.git','.venv','__pycache__')) and ROOT/'reports/local' not in p.parents}
        for target in pending:
            f=target/'protected_files_before.json'
            if not f.exists():f.write_text(json.dumps(snapshot,indent=2)+'\n',encoding='utf-8')
if __name__=='__main__':main()
