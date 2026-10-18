# AgentIAM-QV: Reproducible authorization regression study

## Evidence status (October 18, 2026)

**Executed:** deterministic LOCAL offline policy evaluator using simplified IAM-like rules. **Not executed:** AWS IAM SimulateCustomPolicy, AWS deployed workflows, STS and CloudTrail experiments. AWS authorization responses are not in this package. Do not publish local numbers as measurements from AWS.

## Study design

- Four manually specified task-permission requirements and an independently generated oracle of 36 case-level expected decisions (8 authorized, 28 unauthorized).
- Seven policy types per task: one deliberately overprivileged pooled-role baseline, one task-scoped AgentIAM policy with separate permissions boundary, and five mutated policies (20 mutants total).
- Nine candidate action/resource combinations per task, all authored as benchmark fixtures (not real observed cloud traffic).
- 252 tested policy/case decisions; results recorded in `results/offline_decisions.csv`.

## Executed offline results

| Configuration | Evaluations | Valid allowed | Valid denied | Unauthorized allowed | Unauthorized denied | Accuracy | False-allow rate |
|---|---:|---:|---:|---:|---:|---:|---:|
| Shared pooled-role baseline | 36 | 8 | 0 | 16 | 12 | 55.56% | 57.14% |
| AgentIAM (task-scoped + boundary) | 36 | 8 | 0 | 0 | 28 | 100% | 0% |

Across twenty mutated policy documents, eight mutants produced at least one observable oracle mismatch: four missing-permission mutations and four explicit-deny mutations. Twelve extra-permission mutations were *not detected by the behavior-only oracle* because the independent boundary masked the changes within the tested set. A 'not detected' mutant is not necessarily valid or safe under other conditions.

## Interpretation for software quality

The offline experiment implements authorization regression testing, test-oracle separation, and a simple mutation-testing protocol. A test detection rate of 8/20 (40%) is the proportion of these constructed variants producing observable test failures; **it is not an established mutation score** because equivalence and boundary-masked mutants have not been independently adjudicated. Policy permission boundaries provide a second control but do not repair excessively permissive underlying identity policies.

## Methodological and implementation limitations

The baseline is deliberately weak, the requirements and mutations are authored fixtures, and case selection is small. A perfect result for AgentIAM is expected from the design of these matching fixtures and should not be generalized. The offline evaluator is not AWS IAM and does not model conditions, resource-specific semantics, service control policies, principal/session policies, or the complete AWS authorization evaluation procedure. Some proposed action/resource combinations may require redesign for valid AWS interpretation; AWS simulation results should be vetted for missing context and applicability before publication. Credentials are not provided. The experiments have no externally validated data, cloud workload sampling, or evidence of adoption. An independent reviewer should verify the oracle and classify equivalent/masked mutants before drawing comparative claims.

## Reproduction

From the project root (Python 3.9+):

```bash
python3 scripts/build.py
python3 scripts/run.py --engine offline
python3 scripts/analyze_mutations.py
```

To request *real IAM simulator* results in a properly authorized AWS environment (only after reviewing permissions and policies):

```bash
python3 -m pip install boto3
aws sts get-caller-identity
python3 scripts/run.py --engine aws
python3 scripts/analyze_mutations.py
```

AWS simulation does not execute actual AWS operations and should be described as AWS policy-simulation data, not as live EC2/S3 or production traces. Raw API responses should ideally be preserved for external validation; the existing runner only records decisions and selected metadata in CSV.

## GitHub publication advice

Publish all policy fixtures, independent requirements, oracle, source scripts, offline outputs, and limitations. Do not commit access tokens, credential files, private bucket identifiers, CloudTrail records, or real account identifiers. Replace placeholders before using any real infrastructure. GitHub is a reproducibility artifact, not evidence of real-world external adoption or EB-1A eligibility on its own.
