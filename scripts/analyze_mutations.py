"""Report per-policy mutation results from recorded authorization decisions."""
import csv, pathlib
P=pathlib.Path(__file__).resolve().parents[1]
for engine in ('offline','aws'):
 source=P/'results'/f'{engine}_decisions.csv'
 if not source.exists(): continue
 rows=list(csv.DictReader(source.open()))
 items=[]
 for task in sorted({r['task'] for r in rows}):
  control={r['case_id']:r for r in rows if r['task']==task and r['scenario']=='agentiam'}
  for scenario in sorted({r['scenario'] for r in rows if r['scenario'].startswith('mutant_')}):
   rs=[r for r in rows if r['task']==task and r['scenario']==scenario]
   differences=sum(r['observed']!=control[r['case_id']]['observed'] for r in rs)
   failures=sum(r['observed']!=r['expected'] for r in rs)
   items.append(dict(task=task,mutant=scenario,case_count=len(rs),changed_decisions=differences,oracle_failures=failures,regression_detected=int(failures>0),status='Detected by tests' if failures else 'No observable regression (possibly boundary-contained)'))
 target=P/'results'/f'{engine}_mutation_analysis.csv'
 with target.open('w',newline='') as f:
  w=csv.DictWriter(f,fieldnames=items[0]);w.writeheader();w.writerows(items)
 print(engine, 'mutants:',len(items),'detected:',sum(int(r['regression_detected']) for r in items),'not detected:',sum(not int(r['regression_detected']) for r in items))
