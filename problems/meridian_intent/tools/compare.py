import sys
import json
import statistics
from pathlib import Path
from datetime import datetime

sys.path.insert(0, 'problems/meridian_intent')
sys.path.insert(0, 'problems/meridian_intent/initial_programs')

import validate
import baseline
import best_program


N_RUNS = 10
RESULTS_DIR = Path('results')


def evaluate_module(module, n_runs: int = N_RUNS) -> dict:
    all_results = []
    print(f'  Прогонов: {n_runs}')
    for i in range(n_runs):
        output = module.entrypoint()
        result = validate.validate(output)
        all_results.append(result)
        print(f'    Прогон {i+1}/{n_runs}: fitness={result["fitness"]:.4f}, '
              f'accuracy={result["accuracy"]:.4f}, '
              f'f1_clar={result["f1_clarification"]:.4f}')

    metrics = {}
    for key in ['fitness', 'accuracy', 'f1_clarification', 'invalid_combo_rate']:
        values = [r[key] for r in all_results]
        metrics[key] = {
            'mean': statistics.mean(values),
            'std': statistics.stdev(values) if len(values) > 1 else 0.0,
            'min': min(values),
            'max': max(values),
            'values': values,
        }
    return metrics


def format_metric(m: dict) -> str:
    return f'{m["mean"]:.4f} ± {m["std"]:.4f}'


def main():
    RESULTS_DIR.mkdir(exist_ok=True)
    timestamp = datetime.now().strftime('%Y-%m-%d %H:%M:%S')

    print('=' * 60)
    print(f'Сравнение baseline до и после мутации')
    print(f'Прогонов на программу: {N_RUNS}')
    print(f'Время: {timestamp}')
    print('=' * 60)

    print()
    print("Baseline")
    baseline_metrics = evaluate_module(baseline)

    print()
    print("После мутации")
    best_metrics = evaluate_module(best_program)

    md = []
    md.append('# Сравнение\n')
    md.append(f'**Дата:** {timestamp}\n')
    md.append(f'**Прогонов на программу:** {N_RUNS}\n')
    md.append("")
    md.append('| Метрика | Baseline | После мутации | Улучшение |')
    md.append('|---------|----------|---------------|-----------|')

    for key in ['fitness', 'accuracy', 'f1_clarification', 'invalid_combo_rate']:
        b = baseline_metrics[key]
        best = best_metrics[key]
        delta = best['mean'] - b['mean']
        delta_str = f'{delta:+.4f}'
        md.append(f'| `{key}` | {format_metric(b)} | {format_metric(best)} | **{delta_str}** |')

    md.append('')
    md.append('## Детальные метрики\n')
    md.append('### Baseline\n')
    md.append('| Метрика | Mean | Std | Min | Max |')
    md.append('|---------|------|-----|-----|-----|')
    for key in ['fitness', 'accuracy', 'f1_clarification', 'invalid_combo_rate']:
        m = baseline_metrics[key]
        md.append(f'| `{key}` | {m["mean"]:.4f} | {m["std"]:.4f} | {m["min"]:.4f} | {m["max"]:.4f} |')

    md.append('')
    md.append('### Best program\n')
    md.append('| Метрика | Mean | Std | Min | Max |')
    md.append('|---------|------|-----|-----|-----|')
    for key in ['fitness', 'accuracy', 'f1_clarification', 'invalid_combo_rate']:
        m = best_metrics[key]
        md.append(f'| `{key}` | {m["mean"]:.4f} | {m["std"]:.4f} | {m["min"]:.4f} | {m["max"]:.4f} |')

    md.append('')
    md.append('## Все прогоны\n')
    md.append('### Baseline\n')
    md.append('| Прогон | fitness | accuracy | f1_clarification | invalid_combo_rate |')
    md.append('|--------|---------|----------|------------------|-------------------|')
    for i in range(N_RUNS):
        row = [f'| {i+1} ']
        for key in ['fitness', 'accuracy', 'f1_clarification', 'invalid_combo_rate']:
            row.append(f'| {baseline_metrics[key]["values"][i]:.4f} ')
        row.append('|')
        md.append(''.join(row))

    md.append('')
    md.append('### После мутации\n')
    md.append('| Прогон | fitness | accuracy | f1_clarification | invalid_combo_rate |')
    md.append('|--------|---------|----------|------------------|-------------------|')
    for i in range(N_RUNS):
        row = [f'| {i+1} ']
        for key in ['fitness', 'accuracy', 'f1_clarification', 'invalid_combo_rate']:
            row.append(f'| {best_metrics[key]["values"][i]:.4f} ')
        row.append('|')
        md.append(''.join(row))

    md.append('')
    md.append('## Выводы\n')
    fitness_delta = best_metrics['fitness']['mean'] - baseline_metrics['fitness']['mean']
    md.append(f'- **Baseline:** mean fitness = {baseline_metrics["fitness"]["mean"]:.4f} ± {baseline_metrics["fitness"]["std"]:.4f}')
    md.append(f'- **После мутации:** mean fitness = {best_metrics["fitness"]["mean"]:.4f} ± {best_metrics["fitness"]["std"]:.4f}')
    md.append(f'- **Улучшение:** {fitness_delta:+.4f}')
    md.append('')

    md_path = RESULTS_DIR / 'comparison.md'
    with open(md_path, 'w', encoding='utf-8') as f:
        f.write('\n'.join(md))
    print(f'\nСохранено: {md_path}')

    json_path = RESULTS_DIR / 'comparison.json'
    with open(json_path, 'w', encoding='utf-8') as f:
        json.dump({
            'timestamp': timestamp,
            'n_runs': N_RUNS,
            'baseline': baseline_metrics,
            'best': best_metrics,
        }, f, indent=2, ensure_ascii=False)


if __name__ == '__main__':
    main()