import json
import matplotlib.pyplot as plt
import numpy as np
from pathlib import Path

RESULTS_DIR = Path('results')

with open(RESULTS_DIR / 'comparison.json') as f:
    data = json.load(f)

baseline = data['baseline']
best = data['best']
n_runs = data['n_runs']

fig, axes = plt.subplots(1, 2, figsize=(14, 5))

ax = axes[0]
runs = list(range(1, n_runs + 1))
ax.plot(runs, baseline['fitness']['values'], 'o-', label='Baseline', color='#1f77b4', linewidth=2, markersize=8)
ax.plot(runs, best['fitness']['values'], 's-', label='После мутации', color='#2ca02c', linewidth=2, markersize=8)
ax.axhline(y=baseline['fitness']['mean'], color='#1f77b4', linestyle='--', alpha=0.5)
ax.axhline(y=best['fitness']['mean'], color='#2ca02c', linestyle='--', alpha=0.5)
ax.set_xlabel('Прогон')
ax.set_ylabel('fitness (macro-F1)')
ax.set_title('Fitness по прогонам')
ax.legend()
ax.grid(True, alpha=0.3)


ax = axes[1]
metrics = ['fitness', 'accuracy', 'f1_clarification', 'invalid_combo_rate']
metric_labels = ['fitness\n(macro-F1)', 'accuracy', 'f1_clarification', 'invalid_combo_rate']

baseline_means = [baseline[m]['mean'] for m in metrics]
best_means = [best[m]['mean'] for m in metrics]
baseline_stds = [baseline[m]['std'] for m in metrics]
best_stds = [best[m]['std'] for m in metrics]

x = np.arange(len(metrics))
width = 0.35

ax.bar(x - width/2, baseline_means, width, yerr=baseline_stds, label='Baseline', color='#1f77b4', capsize=5)
ax.bar(x + width/2, best_means, width, yerr=best_stds, label='После мутации', color='#2ca02c', capsize=5)
ax.set_xticks(x)
ax.set_xticklabels(metric_labels, fontsize=9)
ax.set_ylabel('Значение')
ax.set_title('Сравнение метрик (mean ± std)')
ax.legend()
ax.grid(True, alpha=0.3, axis='y')
ax.set_ylim(0, 1.15)

plt.tight_layout()
plt.savefig(RESULTS_DIR / 'comparison_plot.png', dpi=150, bbox_inches='tight')