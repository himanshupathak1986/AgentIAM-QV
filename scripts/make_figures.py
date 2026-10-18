#!/usr/bin/env python3
"""Regenerate publication figures from executed offline CSV outputs (not AWS observations)."""
import csv
from pathlib import Path
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt

ROOT = Path(__file__).resolve().parents[1]
RESULTS = ROOT / 'results'
FIGURES = ROOT / 'figures'
FIGURES.mkdir(exist_ok=True)
with (RESULTS / 'offline_summary.csv').open(newline='') as f:
    summaries = {r['scenario']: r for r in csv.DictReader(f)}
with (RESULTS / 'offline_mutation_analysis.csv').open(newline='') as f:
    mutants = list(csv.DictReader(f))

# Figure 1: percentage scale, actual offline results.
labels = ['Shared-role baseline', 'AgentIAM + boundary']
accuracy = [float(summaries[k]['accuracy']) * 100 for k in ['baseline','agentiam']]
false_allow = [float(summaries[k]['false_allow_rate']) * 100 for k in ['baseline','agentiam']]
fig, ax = plt.subplots(figsize=(7.2, 3.5))
y = [0,1]; h = 0.29
for i, vals in enumerate((accuracy, false_allow)):
    offset = (-h/2 if i==0 else h/2)
    bars = ax.barh([t+offset for t in y], vals, height=h, label=['Decision accuracy','False-allow rate'][i])
    for b, v in zip(bars,vals): ax.text(min(v+1.2,103), b.get_y()+b.get_height()/2, f'{v:.1f}%', va='center', fontsize=9)
ax.set_yticks(y, labels); ax.invert_yaxis(); ax.set_xlim(0,111)
ax.set_xlabel('Percent of test cases (offline policy model)')
ax.set_title('Authorization quality: baseline vs AgentIAM')
ax.legend(loc='lower right', frameon=False)
ax.spines[['top','right']].set_visible(False)
fig.tight_layout()
for ext in ('png','svg','pdf'): fig.savefig(FIGURES / f'offline_authorization_comparison.{ext}', dpi=180, bbox_inches='tight')
plt.close(fig)

# Figure 2: Mutation outcomes count, no implicit claim that boundary-mask=defect detected.
detected = sum(int(m['regression_detected']) for m in mutants)
unchanged = len(mutants)-detected
fig, ax = plt.subplots(figsize=(6.6,3.1))
bars = ax.barh(['Observable regression', 'No decision change'], [detected,unchanged])
for b, val in zip(bars,[detected,unchanged]): ax.text(val+0.18,b.get_y()+b.get_height()/2,f'{val}/20',va='center')
ax.set_xlim(0,15); ax.set_xlabel('Policy mutations (count)')
ax.set_title('Mutation outcomes in the offline test suite')
ax.invert_yaxis(); ax.spines[['top','right']].set_visible(False)
fig.tight_layout()
for ext in ('png','svg','pdf'): fig.savefig(FIGURES / f'offline_mutation_outcomes.{ext}', dpi=180, bbox_inches='tight')
plt.close(fig)
print(f'Generated 6 figures from {len(mutants)} mutation rows: {detected} observable, {unchanged} unchanged')
