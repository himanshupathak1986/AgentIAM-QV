### 6.3 Software Quality Verification through Authorization Regression Testing

We evaluate authorization correctness using an independent task-operation oracle and policy mutation testing. Four AgentIAM workflows (provisioning, monitoring, remediation, and orchestration) are paired with a fixed set of AWS actions and resource ARNs, yielding 36 expected authorization decisions. The oracle is specified separately from the IAM policies to reduce circularity. A task-scoped identity policy with a permissions boundary is compared with a deliberately overprivileged pooled-role baseline. Twenty mutant policies introduce extra permissions, missing required permissions, wildcard privileges, and explicit denials. We measure the false-allow rate, false-deny rate, and whether the boundary contains an otherwise unsafe policy mutation.

**Results paragraph (conditional; complete ONLY after running AWS simulator):** AWS IAM policy-simulator results, raw response records, evaluator version, and policy fixtures are made available in the accompanying repository [URL]. Table X reports the number of tested decisions, false allows and false denies by configuration. The policy simulator tests modeled access decisions, not actual AWS service execution, STS credential handling, or CloudTrail coverage; results should therefore be interpreted as authorization-model evidence rather than live-cloud security guarantees.

**Suggested compact results table (fill from `results/aws_summary.csv`, never from offline results for AWS claims):**

| Configuration | Tests | False allows | False denies | Accuracy |
| --- | ---: | ---: | ---: | ---: |
| Shared-role baseline | [AWS result] | [AWS result] | [AWS result] | [AWS result] |
| AgentIAM + permission boundary | [AWS result] | [AWS result] | [AWS result] | [AWS result] |

*Note:* If only the offline engine is used, label this section "illustrative offline policy-model check" rather than AWS experimental evaluation, with appropriate limitations.

**Alternative compact table for a constrained page (offline evidence only):**

| Configuration | Accuracy | False allows |
| --- | ---: | ---: |
| Shared-role baseline | 55.56% | 16/28 |
| AgentIAM + boundary | 100% | 0/28 |

*36 manually designed offline cases per configuration, not AWS simulator results. Eight of 20 mutation variants produced observable regressions.* See `figures/offline_authorization_comparison.pdf` and `figures/offline_mutation_outcomes.pdf` for plots derived from the CSV data.
