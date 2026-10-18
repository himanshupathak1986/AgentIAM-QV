"""Usage: python scripts/run.py --engine offline|aws. AWS calls need IAM SimulateCustomPolicy permission."""
import argparse,csv,json,pathlib,fnmatch,datetime
P=pathlib.Path(__file__).resolve().parents[1]
args=argparse.ArgumentParser();args.add_argument('--engine',choices=['offline','aws'],required=True);o=args.parse_args()
rows=list(csv.DictReader((P/'data/oracle.csv').open()))
# Offline engine is a constrained teaching implementation, NOT an AWS IAM policy evaluator.
def match(pol,action,res):
 deny=False;allow=False
 for s in pol['Statement']:
  acts=s['Action'] if isinstance(s['Action'],list) else [s['Action']]
  resources=s['Resource'] if isinstance(s['Resource'],list) else [s['Resource']]
  if any(fnmatch.fnmatchcase(action.lower(),a.lower()) for a in acts) and any(fnmatch.fnmatchcase(res,r) for r in resources):
   if s['Effect']=='Deny':deny=True
   elif s['Effect']=='Allow':allow=True
 return not deny and allow
if o.engine=='aws':
 import boto3
 client=boto3.client('iam')

def evaluate(pol,case,boundary=None):
 if o.engine=='offline':return ('allowed' if match(pol,case['action'],case['resource']) and (boundary is None or match(boundary,case['action'],case['resource'])) else 'denied',None)
 kwargs={'PolicyInputList':[json.dumps(pol)],'ActionNames':[case['action']],'ResourceArns':[case['resource']]}
 if boundary is not None:kwargs['PermissionsBoundaryPolicyInputList']=[json.dumps(boundary)]
 resp=client.simulate_custom_policy(**kwargs)
 decision=resp['EvaluationResults'][0]['EvalDecision']
 return ('allowed' if decision=='allowed' else 'denied',{'aws_eval_decision':decision,'missing_context_values':resp['EvaluationResults'][0].get('MissingContextValues',[])})
results=[]
for task in sorted({r['task'] for r in rows}):
 scenarios=['baseline','agentiam']+['mutant_'+n for n in ['pooled_role','extra_sensitive_action','missing_required_action','explicit_deny_required','wildcard_all']]
 for scenario in scenarios:
  pol=json.loads((P/f'policies/{task}_{scenario}.json').read_text())
  boundary=None if scenario=='baseline' else json.loads((P/f'policies/{task}_boundary.json').read_text())
  for case in (r for r in rows if r['task']==task):
   decision,raw=evaluate(pol,case,boundary)
   results.append({**case,'scenario':scenario,'observed':decision,'correct':int(decision==case['expected']),'aws_details':json.dumps(raw) if raw is not None else ''})
out=P/'results'/f'{o.engine}_decisions.csv'
with out.open('w',newline='') as f:
 w=csv.DictWriter(f,fieldnames=results[0].keys());w.writeheader();w.writerows(results)
summary=[]
for scenario in sorted(set(r['scenario'] for r in results)):
 rs=[r for r in results if r['scenario']==scenario]
 TP=sum(r['expected']=='allowed' and r['observed']=='allowed' for r in rs)
 FN=sum(r['expected']=='allowed' and r['observed']=='denied' for r in rs)
 FP=sum(r['expected']=='denied' and r['observed']=='allowed' for r in rs)
 TN=sum(r['expected']=='denied' and r['observed']=='denied' for r in rs)
 summary.append({'scenario':scenario,'n':len(rs),'legitimate_allowed':TP,'legitimate_denied':FN,'unauthorized_allowed':FP,'unauthorized_denied':TN,'accuracy':round((TP+TN)/len(rs),4),'false_allow_rate':round(FP/(FP+TN),4) if FP+TN else '', 'false_deny_rate':round(FN/(FN+TP),4) if FN+TP else ''})
with (P/'results'/f'{o.engine}_summary.csv').open('w',newline='') as f:
 w=csv.DictWriter(f,fieldnames=summary[0].keys());w.writeheader();w.writerows(summary)
print('Engine:',o.engine,'cases:',len(results),'\n'+json.dumps(summary,indent=2))
