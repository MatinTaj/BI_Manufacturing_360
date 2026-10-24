"""Offline PostgreSQL 18 AST, schema, CSV-constraint and baseline checks.
No database driver, psql invocation, server process or network connection.
Requires pglast 8.x; optional --parser-path locates an isolated installation.
"""
import argparse
import calendar
import csv
from datetime import date, timedelta
from decimal import Decimal, ROUND_HALF_UP, ROUND_FLOOR, localcontext
import hashlib
import json
from pathlib import Path
import re
import sys

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[1]


def require(ok, message):
    if not ok:
        raise ValueError(message)


def walk(value):
    if isinstance(value,dict):
        yield value
        for child in value.values(): yield from walk(child)
    elif isinstance(value,list):
        for child in value: yield from walk(child)


def strings(items):
    return [item['String']['sval'] for item in items]


def evaluate(node, row):
    if node is None: return None
    if 'ColumnRef' in node: return row[strings(node['ColumnRef']['fields'])[-1]]
    if 'A_Const' in node:
        v=node['A_Const']
        if v.get('isnull'): return None
        if 'ival' in v: return Decimal(v['ival'].get('ival',0))
        if 'fval' in v: return Decimal(v['fval']['fval'])
        if 'sval' in v: return v['sval']['sval']
        if 'boolval' in v: return v['boolval'].get('boolval',False)
    if 'TypeCast' in node:
        v=node['TypeCast']; value=evaluate(v['arg'],row); target=strings(v['typeName']['names'])[-1]
        if target=='numeric': return Decimal(str(value))
        if target in ('int4','int8','integer'): return int(value)
        if target=='date': return value if isinstance(value,date) else date.fromisoformat(value)
        if target=='interval': return ('interval',value)
        if target=='text': return str(value)
        raise ValueError('Unsupported offline cast '+target)
    if 'CoalesceExpr' in node:
        return next((v for v in (evaluate(a,row) for a in node['CoalesceExpr']['args']) if v is not None),None)
    if 'NullTest' in node:
        v=node['NullTest']; result=evaluate(v['arg'],row) is None
        return result if v['nulltesttype']=='IS_NULL' else not result
    if 'BoolExpr' in node:
        v=node['BoolExpr']; args=[bool(evaluate(a,row)) for a in v['args']]
        if v['boolop']=='AND_EXPR': return all(args)
        if v['boolop']=='OR_EXPR': return any(args)
        return not args[0]
    if 'CaseExpr' in node:
        v=node['CaseExpr']; value=evaluate(v.get('arg'),row)
        for entry in v['args']:
            w=entry['CaseWhen']; condition=evaluate(w['expr'],row)
            if (condition if 'arg' not in v else value==condition): return evaluate(w['result'],row)
        return evaluate(v.get('defresult'),row)
    if 'FuncCall' in node:
        v=node['FuncCall']; name=strings(v['funcname'])[-1]; args=[evaluate(a,row) for a in v.get('args',[])]
        if name=='round': return args[0].quantize(Decimal(1).scaleb(-int(args[1]) if len(args)>1 else 0),rounding=ROUND_HALF_UP)
        if name=='floor': return args[0].to_integral_value(rounding=ROUND_FLOOR)
        if name=='abs': return abs(args[0])
        if name=='mod': return args[0] % args[1]
        if name=='length': return Decimal(len(args[0]))
        if name=='btrim': return args[0].strip()
        if name=='least': return min(args)
        if name=='date_trunc': return args[1].replace(day=1)
        if name=='extract':
            field,value=args
            return Decimal({'year':value.year,'month':value.month,'day':value.day,'quarter':(value.month-1)//3+1}[field])
        raise ValueError('Unsupported offline function '+name)
    if 'MinMaxExpr' in node: return min(evaluate(a,row) for a in node['MinMaxExpr']['args'])
    if 'A_Expr' in node:
        v=node['A_Expr']; kind=v['kind']; left=evaluate(v.get('lexpr'),row)
        if kind=='AEXPR_IN':
            items=v['rexpr']['List']['items'] if isinstance(v['rexpr'],dict) else v['rexpr']
            result=left in [evaluate(a,row) for a in items]
            return result if strings(v['name'])[-1]=='=' else not result
        right=evaluate(v.get('rexpr'),row); op=strings(v['name'])[-1]
        if kind=='AEXPR_NULLIF': return None if left==right else left
        if op in ('=','<>','<','<=','>','>='):
            return {'=':lambda:left==right,'<>':lambda:left!=right,'<':lambda:left<right,
                    '<=':lambda:left<=right,'>':lambda:left>right,'>=':lambda:left>=right}[op]()
        if op=='+':
            if isinstance(left,date) and isinstance(right,tuple):
                require(right[1]=='1 month - 1 day','Unexpected interval')
                return left.replace(day=calendar.monthrange(left.year,left.month)[1])
            return left+right
        if op=='-': return -right if left is None else left-right
        if op=='*': return left*right
        if op=='/': return left/right
        raise ValueError('Unsupported offline operator '+op)
    raise ValueError('Unsupported offline expression '+str(node)[:180])


class Binder:
    """Check column/relation references and view output names without a database.
    Does not claim operator/type resolution or planner equivalence to a server.
    """
    def __init__(self,relations): self.relations=relations; self.selects=0

    def select(self, tree, ctes=None, outer=None):
        stmt=tree.get('SelectStmt',tree); ctes=dict(ctes or {}); outer=dict(outer or {}); self.selects+=1
        for wrapped in stmt.get('withClause',{}).get('ctes',[]):
            entry=wrapped['CommonTableExpr']; ctes[entry['ctename']]=self.select(entry['ctequery'],ctes,outer)
        if stmt.get('op','SETOP_NONE')!='SETOP_NONE':
            left=self.select(stmt['larg'],ctes,outer); right=self.select(stmt['rarg'],ctes,outer)
            require(len(left)==len(right),'Set-operation column count mismatch'); return left
        aliases={}
        def source(wrapped):
            if 'RangeVar' in wrapped:
                v=wrapped['RangeVar']; key=(v.get('schemaname'),v['relname'])
                values=ctes.get(v['relname']) if key[0] is None else None
                if values is None:
                    require(key in self.relations,'Unknown relation '+str(key)); values=self.relations[key]
                return {v.get('alias',{}).get('aliasname',v['relname']):list(values)}
            if 'RangeSubselect' in wrapped:
                v=wrapped['RangeSubselect']; values=self.select(v['subquery'],ctes,{**outer,**aliases})
                alias=v['alias']; values=strings(alias['colnames']) if alias.get('colnames') else values
                return {alias['aliasname']:values}
            if 'JoinExpr' in wrapped:
                v=wrapped['JoinExpr']; left=source(v['larg']); aliases.update(left); right=source(v['rarg']); aliases.update(right)
                for item in v.get('usingClause',[]):
                    name=item['String']['sval']
                    require(any(name in cols for cols in left.values()) and any(name in cols for cols in right.values()),'Unknown USING key '+name)
                return {**left,**right}
            raise ValueError('Unsupported FROM source '+str(wrapped)[:100])
        for wrapped in stmt.get('fromClause',[]): aliases.update(source(wrapped))
        outputs=[]
        if 'valuesLists' in stmt: outputs=['column'+str(i+1) for i in range(len(stmt['valuesLists'][0]['List']['items']))]
        for target in stmt.get('targetList',[]):
            t=target['ResTarget']; val=t['val']; cref=val.get('ColumnRef')
            if cref and any('A_Star' in v for v in cref['fields']):
                fields=cref['fields']; outputs+=aliases[strings(fields[:-1])[0]] if len(fields)>1 else [c for cols in aliases.values() for c in cols]
            else:
                outputs.append(t.get('name') or (strings(cref['fields'])[-1] if cref else '?column?'))
        visible={**outer,**aliases}; allcols={c for cols in visible.values() for c in cols}
        def references(value):
            if isinstance(value,dict):
                if 'SelectStmt' in value:
                    self.select(value,ctes,visible); return
                if 'ColumnRef' in value:
                    fields=value['ColumnRef']['fields']
                    if any('A_Star' in x for x in fields): return
                    names=strings(fields)
                    if len(names)>1:
                        require(names[-2] in visible and names[-1] in visible[names[-2]],'Unknown qualified column '+'.'.join(names))
                    else: require(names[0] in allcols,'Unknown column '+names[0])
                    return
                for key,child in value.items():
                    if key not in ('withClause','fromClause','larg','rarg'):references(child)
            elif isinstance(value,list):
                for child in value:references(child)
        references(stmt)
        # JOIN ON clauses belong to the same source scope.
        def join_quals(item):
            if 'JoinExpr' in item:
                join=item['JoinExpr'];references(join.get('quals'))
                join_quals(join['larg']);join_quals(join['rarg'])
        for item in stmt.get('fromClause',[]):join_quals(item)
        return outputs


def run(parser_path=None):
    if parser_path:sys.path.insert(0,str(Path(parser_path).resolve()))
    import pglast
    from pglast import parser
    require(parser.get_postgresql_version()[0]==18,'Use a PostgreSQL 18 parser')
    contract=json.loads((HERE/'database_contract.json').read_text()); manifest=json.loads((HERE/'input_manifest.json').read_text())
    relations={('erp',n):[c['name'] for c in t['columns']] for n,t in contract['tables'].items()}
    sql_trees={}; statements=0; plpgsql=0
    for file in sorted(HERE.glob('*.sql')):
        tree=json.loads(parser.parse_sql_json(file.read_text(encoding='utf-8')));sql_trees[file.name]=tree;statements+=len(tree['stmts'])
        for wrapped in tree['stmts']:
            stmt=wrapped['stmt']
            if 'DoStmt' in stmt:
                body=next(a['DefElem']['arg']['String']['sval'] for a in stmt['DoStmt']['args'] if a['DefElem']['defname']=='as')
                parser.parse_plpgsql_json('DO $$'+body+'$$;');plpgsql+=1
            if 'CreateStmt' in stmt:
                v=stmt['CreateStmt']; rel=v['relation']
                if rel['schemaname']=='audit':relations[('audit',rel['relname'])]=[x['ColumnDef']['colname'] for x in v['tableElts'] if 'ColumnDef' in x]
    binder=Binder(relations); view_count=0
    for name in ('03_views.sql','05_validate.sql'):
        for wrapped in sql_trees[name]['stmts']:
            stmt=wrapped['stmt']
            if 'ViewStmt' in stmt:
                v=stmt['ViewStmt']; columns=binder.select(v['query']); key=(v['view']['schemaname'],v['view']['relname'])
                require(len(columns)==len(set(columns)),'Duplicate view output columns: '+str(key))
                relations[key]=columns;view_count+=1
            elif 'SelectStmt' in stmt:binder.select(stmt)
    # Analytical views must never read expected baseline values or embed financial constants.
    for node in walk(sql_trees['03_views.sql']):
        if 'RangeVar' in node:require(node['RangeVar'].get('schemaname')!='audit','Analytical view depends on baseline audit data')
        if 'A_Const' in node:
            v=node['A_Const'];number=v.get('ival',{}).get('ival',v.get('fval',{}).get('fval'))
            if number is not None:require(Decimal(str(number)) in {Decimal(0),Decimal(1),Decimal(100)},'Financial constant in analytical view')
    tables={}; row_checks=0
    for name, spec in contract['tables'].items():
        file=ROOT/'data/staging'/f'{name}.csv'; entry=manifest['datasets'][name]
        require(hashlib.sha256(file.read_bytes()).hexdigest()==entry['sha256'],'Approved CSV hash changed: '+name)
        with file.open(encoding='utf-8',newline='') as stream:
            reader=csv.DictReader(stream);require(reader.fieldnames==entry['columns']==[c['name'] for c in spec['columns']],'Header/order mismatch: '+name)
            data=list(reader)
        require(len(data)==entry['rows'],'Row count mismatch: '+name)
        rows=[]
        for raw in data:
            row={}
            for col in spec['columns']:
                value=raw[col['name']];typ=col['type'];require(value!='','Null/empty input: '+name+'.'+col['name'])
                if typ=='date':value=date.fromisoformat(value)
                elif typ=='integer':
                    number=Decimal(value);require(number==number.to_integral_value(),'Fractional integer');value=number
                elif typ.startswith('numeric'):
                    value=Decimal(value);digits,scale=map(int,re.findall(r'\d+',typ))
                    require(value.is_finite() and value==value.quantize(Decimal(1).scaleb(-scale)) and abs(value)<Decimal(10)**(digits-scale),'Numeric scale/precision loss: '+name+'.'+col['name'])
                row[col['name']]=value
            rows.append(row)
        tables[name]=rows
        for keys in [spec['primary_key'],*spec['unique']]:
            require(len({tuple(r[c] for c in keys) for r in rows})==len(rows),'Duplicate key '+name+str(keys))
        for expression in spec['checks']:
            expr=json.loads(parser.parse_sql_json('SELECT '+expression))['stmts'][0]['stmt']['SelectStmt']['targetList'][0]['ResTarget']['val']
            for row in rows:
                with localcontext() as ctx:
                    ctx.prec=48
                    require(bool(evaluate(expr,row)),'CSV fails planned SQL CHECK: '+name+' :: '+expression+' :: '+str(row.get(spec['primary_key'][0])))
                row_checks+=1
    for name,spec in contract['tables'].items():
        for relation in spec['foreign_keys']:
            parent={tuple(r[c] for c in relation['references']) for r in tables[relation['parent']]}
            require(all(tuple(r[c] for c in relation['columns']) in parent for r in tables[name]),'Foreign key mismatch: '+name)
    copies=(HERE/'02_import.psql').read_text(encoding='utf-8').splitlines();copy_count=0;loaded=set()
    for line in copies:
        if not line.startswith('\\copy '):continue
        match=re.fullmatch(r"\\copy erp\.(\w+) \(([^)]+)\) FROM '(\w+)\.csv' WITH \(FORMAT csv, HEADER MATCH, ENCODING 'UTF8'\);",line)
        require(match is not None,'Malformed client COPY command')
        name,cols,filename=match.groups();require(name==filename and [c.strip() for c in cols.split(',')]==manifest['datasets'][name]['columns'],'COPY column mismatch')
        require(all(f['parent'] in loaded for f in contract['tables'][name]['foreign_keys']),'COPY not parent-first: '+name)
        loaded.add(name);copy_count+=1
    require(copy_count==19 and loaded==set(tables),'Incomplete import plan')
    # Independently recompute source P&L and compare all approved monetary metrics.
    ref=ROOT/manifest['phase7_report']/'financial_comparison.csv'
    require(hashlib.sha256(ref.read_bytes()).hexdigest()==manifest['phase7_financial_sha256'],'Phase 7 reference hash changed')
    with ref.open(newline='',encoding='utf-8') as stream: expected=[r for r in csv.DictReader(stream) if r['dataset']=='candidate']
    metrics_checked=0
    for period in ('2024','2025','combined'):
        select=lambda name:[r for r in tables[name] if period=='combined' or str(r['month_id']).startswith(period)]
        sales=select('sales');opex=select('operating_expenses')
        totals={'revenue':sum(r['net_revenue_eur'] for r in sales),'cogs':sum(r['cogs_eur'] for r in sales),
                'outbound_freight':sum(r['outbound_freight_eur'] for r in sales),
                'selling_expenses':sum(r['amount_eur'] for r in opex if r['expense_category']=='selling'),
                'administrative_expenses':sum(r['amount_eur'] for r in opex if r['expense_category']=='administration'),
                'idle_cost':sum(r['idle_cost_eur'] for r in select('manufacturing_costs')),
                'production_loss':sum(r['production_loss_expense_eur'] for r in select('production_cost_allocation'))}
        totals['gross_profit']=totals['revenue']-totals['cogs']
        totals['operating_profit']=totals['gross_profit']-sum(totals[c] for c in ('outbound_freight','selling_expenses','administrative_expenses','idle_cost','production_loss'))
        totals['gross_margin_pct']=100*totals['gross_profit']/totals['revenue'];totals['operating_margin_pct']=100*totals['operating_profit']/totals['revenue']
        e=next(r for r in expected if r['period']==period)
        for col,actual in totals.items():
            require(abs(actual-Decimal(e[col]))<=(Decimal('0.00000001') if col.endswith('_pct') else 0),'P&L reference mismatch '+period+'.'+col);metrics_checked+=1
    result=dict(status='PASS',postgres_connected=False,database_created=False,csv_modified=False,
        parser_version=pglast.__version__,postgres_parser_version=parser.get_postgresql_version(),
        parsed_sql_statements=statements,parsed_plpgsql_blocks=plpgsql,validated_select_scopes=binder.selects,
        views=view_count,csv_tables=len(tables),copy_commands=copy_count,row_check_evaluations=row_checks,
        baseline_metric_comparisons=metrics_checked,
        limitation='Offline syntax/name/data checks only; server type resolution, COPY, transactions, permissions, planner and execution remain untested.')
    return result


if __name__=='__main__':
    cli=argparse.ArgumentParser(description=__doc__);cli.add_argument('--parser-path');cli.add_argument('--report',type=Path)
    args=cli.parse_args();result=run(args.parser_path)
    if args.report:args.report.write_text(json.dumps(result,indent=2)+'\n',encoding='utf-8')
    print(json.dumps(result,indent=2))
