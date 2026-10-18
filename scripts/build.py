import csv,json,pathlib,copy
P=pathlib.Path(__file__).resolve().parents[1]
# Independent requirements: hand-specified task/action/resource allowlists, not inferred from policies.
REQ={
'provisioning': [('ec2:RunInstances','arn:aws:ec2:us-east-1:111122223333:instance/*'),('ec2:DescribeInstances','*')],
'monitoring': [('ec2:DescribeInstances','*'),('cloudwatch:GetMetricData','*')],
'remediation': [('ec2:StopInstances','arn:aws:ec2:us-east-1:111122223333:instance/*'),('ec2:DescribeInstances','*')],
'orchestration': [('lambda:InvokeFunction','arn:aws:lambda:us-east-1:111122223333:function:agentiam-workflow'),('states:StartExecution','arn:aws:states:us-east-1:111122223333:stateMachine:agentiam-workflow')],
}
CANDIDATES=[('ec2:RunInstances','arn:aws:ec2:us-east-1:111122223333:instance/*'),('ec2:DescribeInstances','*'),('ec2:StopInstances','arn:aws:ec2:us-east-1:111122223333:instance/*'),('cloudwatch:GetMetricData','*'),('lambda:InvokeFunction','arn:aws:lambda:us-east-1:111122223333:function:agentiam-workflow'),('states:StartExecution','arn:aws:states:us-east-1:111122223333:stateMachine:agentiam-workflow'),('iam:CreateUser','*'),('s3:DeleteBucket','arn:aws:s3:::agentiam-example'),('ec2:TerminateInstances','arn:aws:ec2:us-east-1:111122223333:instance/*')]
# Include action-required valid resources and near-miss resources; ARN resources beginning with * require action-compatible resource type.
rows=[]
for task,allows in REQ.items():
 for action,res in CANDIDATES:
  rows.append(dict(case_id=f'C{len(rows)+1:03d}',task=task,action=action,resource=res,expected='allowed' if (action,res) in allows else 'denied',rationale='requirements matrix v1'))
with (P/'data/oracle.csv').open('w',newline='') as f:
 w=csv.DictWriter(f,fieldnames=rows[0].keys());w.writeheader();w.writerows(rows)
(P/'data/requirements.json').write_text(json.dumps(REQ,indent=2))
def policy(pairs):
 return {'Version':'2012-10-17','Statement':[{'Effect':'Allow','Action':a,'Resource':r} for a,r in pairs]}
union=list(dict.fromkeys(x for a in REQ.values() for x in a))
for task,allows in REQ.items():
 # baseline is pooled broad identity policy; AgentIAM has task identity and separate boundary
 (P/f'policies/{task}_baseline.json').write_text(json.dumps(policy(union),indent=2))
 (P/f'policies/{task}_agentiam.json').write_text(json.dumps(policy(allows),indent=2))
 (P/f'policies/{task}_boundary.json').write_text(json.dumps(policy(allows),indent=2))
 # deliberately defective variants; same independent boundary used for agentiam
 mutants={
 'pooled_role':policy(union),
 'extra_sensitive_action':policy(allows+[('iam:CreateUser','*')]),
 'missing_required_action':policy(allows[:-1]),
 'explicit_deny_required':{'Version':'2012-10-17','Statement':policy(allows)['Statement']+[{'Effect':'Deny','Action':allows[0][0],'Resource':allows[0][1]}]},
 'wildcard_all':policy([('*','*')])
 }
 for name,pol in mutants.items(): (P/f'policies/{task}_mutant_{name}.json').write_text(json.dumps(pol,indent=2))
print(f'Prepared {len(rows)} independent oracle requests, {len(REQ)*5} mutated policies')
