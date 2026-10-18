# AgentIAM: Independent Authorization Oracle and Mutation Experiments

## Evidence status

- `results/offline_*` are **local deterministic model checks**, NOT AWS observations and NOT production data.
- `results/aws_*` do not exist until a researcher runs the AWS policy simulator with valid credentials.
- Input requirements and IAM policy JSON are authored research fixtures, NOT observational data. Their design choices materially affect reported effect sizes.
- AWS IAM **SimulateCustomPolicy** evaluates permission decisions only; it does not execute EC2/Lambda/S3 actions, validate STS issuance, prove CloudTrail audit coverage, or model all live authorization conditions. AWS warns simulator results can differ from real deployment.

## How cases were collected

The `data/requirements.json` file is a manually specified, independent task-to-allowed-API map (4 tasks, 2 intended permissions per task). `scripts/build.py` expands it against a fixed universe of 9 candidate action/resource combinations into `data/oracle.csv` (36 rows: 8 expected allow, 28 expected deny). It *does not* infer expected outcomes from the IAM policy files. All cases are synthetic research fixtures, so do not call them actual incident observations.

`build.py` also constructs task-specific IAM identity and boundary documents, an intentionally overprivileged pooled-role baseline, and five mutants per task: pooled role, extra sensitive action, removal of necessary permission, explicit deny, and wildcard permission.

## Reproduction (offline)

```sh
python3 scripts/build.py
python3 scripts/run.py --engine offline
```

The offline engine is an intentionally small allow/deny matcher for these simplified research fixtures; **it is not an implementation of AWS IAM and cannot validate AWS behavior**. In this generated fixture, the common boundary masks three overpermission mutants and two permission-removal mutants produce test failures. A masked mutant still represents a policy-maintenance problem and should be reported separately rather than ignored.

## AWS evaluation

Prerequisites: Python 3.9+, `pip install boto3`, configured AWS credentials with the **iam:SimulateCustomPolicy** permission; local network access. The service may require permission to use the simulator, but no cloud infrastructure provisioning is necessary.

```sh
aws sts get-caller-identity
python3 scripts/run.py --engine aws
```

Output files are `results/aws_decisions.csv` and `results/aws_summary.csv`. `aws_decisions.csv` retains AWS decision strings and missing-context flags. Check the `missing_context_values` field; if nonempty, do not interpret that response as conclusive. Check policy/resource compatibility, resource scoping, and whether your organization's policies affect desired live deployment. AWS returns `allowed`, `implicitDeny`, or `explicitDeny`, the latter two being counted as denied for the confusion matrix. **No dangerous operations are executed by these simulator calls**.

If using AWS service-specific action/resources that require multiple resource types for actual operation, policy simulation with a single resource ARN may not fully characterize live authorization. Add real configuration-specific test cases and authorized environment tests before generalizing.

## Metrics and formulas

For the independent expected allow/deny oracle, TP=valid allowed, FN=valid denied, FP=invalid allowed, TN=invalid denied.
- False-allow rate = FP / (FP + TN)
- False-deny rate = FN / (TP + FN)
- Accuracy = (TP + TN) / N
- Mutation **test detection**: mutants whose observed decision differs from expected oracle; **boundary containment**: overly permissive identity-policy mutants remaining denied by the boundary. Report these separately.

## Scientific limitations

This is a deterministic, small, researcher-designed benchmark, not a random sample of real-world workloads. The baseline is intentionally weak (pooled permissions) and is not representative of all traditional IAM designs. Input fixtures, desired outcomes, and mutations are all disclosed. The offline check uses a narrow action/resource matching subset. The use of the independent requirement oracle reduces direct circularity, but does not ensure external validity. Neither simulated nor offline results establish causal security improvements in AWS production. For a peer-reviewed contribution, extend the benchmark using real documented policies (with sensitive data removed), independent review of expected authorization, harder conditions/resource constraints, larger mutation operators and multiple baselines, then preserve untouched AWS simulator JSON responses.

## Manuscript placement

Section 6.3, *Software Quality Verification through Authorization Regression Testing*, after Section 6.2. **Do not place the offline results in the manuscript as AWS evidence.** Only describe executed AWS results when `aws_decisions.csv` is produced and examined.

## Official AWS docs

https://docs.aws.amazon.com/cli/latest/reference/iam/simulate-custom-policy.html
https://docs.aws.amazon.com/IAM/latest/APIReference/API_SimulatePrincipalPolicy.html

## Executed study results and per-mutant data

Read [`EXPERIMENT_REPORT.md`](EXPERIMENT_REPORT.md) for verified offline counts, caveats and reproduction steps. The per-mutant offline results are in `results/offline_mutation_analysis.csv`; regenerate using `python3 scripts/analyze_mutations.py`. These results are model-based and **must not** be presented as AWS IAM API responses.

## Publication-ready offline figures and compact paper table

The figure-generation script reads the actual CSV outputs (rather than embedding outcome numbers):

```sh
python3 scripts/analyze_mutations.py
python3 scripts/make_figures.py
```

- [`figures/offline_authorization_comparison.png`](figures/offline_authorization_comparison.png): comparison of authorization accuracy and unauthorized false-allow rate.
- [`figures/offline_mutation_outcomes.png`](figures/offline_mutation_outcomes.png): 8 mutations with observable regressions versus 12 without decision changes.
- Corresponding `.svg` and `.pdf` files offer vector graphics for paper production.
- All visuals describe only the **simplified offline policy model**, not AWS IAM or a production deployment. Mutation non-detection does not mean a test confirmed the mutated policy is safe.

**Compact manuscript table:**

| Configuration | Accuracy | False allows |
|:--|--:|--:|
| Shared-role baseline | 55.56% | 16/28 |
| AgentIAM + boundary | 100% | 0/28 |

*Table note: 36 offline authorization cases per configuration; researcher-defined fixtures. Separate mutation tests produced observable authorization regressions for 8/20 mutants.*
