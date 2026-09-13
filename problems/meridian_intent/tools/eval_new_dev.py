import sys
import json
import argparse
import statistics
from pathlib import Path
from datetime import datetime

sys.path.insert(0, 'problems/meridian_intent')
sys.path.insert(0, 'problems/meridian_intent/initial_programs')

import validate
import best_program

OUR_DEV = "problems/meridian_intent/data/dev.jsonl"
N_RUNS = 10


def load_dev(path):
    with open(path, encoding='utf-8') as f:
        return [json.loads(line) for line in f if line.strip()]


def evaluate(module, dev_data, n_runs=N_RUNS):
    all_results = []
    for _ in range(n_runs):
        predictions = module.classify_all(dev_data)
        result = validate.validate_with_dev(predictions, dev_data)
        all_results.append(result)

    metrics = {}
    for key in ['fitness', 'accuracy', 'f1_clarification', 'invalid_combo_rate']:
        values = [r[key] for r in all_results]
        metrics[key] = {
            'mean': statistics.mean(values),
            'std': statistics.stdev(values) if len(values) > 1 else 0.0,
            'min': min(values),
            'max': max(values),
        }
    return metrics


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("new_dev", help="Новый dev.jsonl")
    parser.add_argument("--output", default="results/new_dev_comparison.md")
    args = parser.parse_args()

    our_dev = load_dev(OUR_DEV)
    new_dev = load_dev(args.new_dev)

    print(f"Наш dev: {len(our_dev)} примеров")
    print(f"Новый dev: {len(new_dev)} примеров")
    print(f"Прогонов: {N_RUNS}")
    print()

    our_metrics = evaluate(best_program, our_dev)

    new_metrics = evaluate(best_program, new_dev)

    timestamp = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
    Path('results').mkdir(exist_ok=True)
    with open(args.output, 'w', encoding='utf-8') as f:
        f.write(f"# Оценка best_program: наш dev vs новый dev\n\n")
        f.write(f"**Дата:** {timestamp}\n")
        f.write(f"**Программа:** `best_program`\n")
        f.write(f"**Прогонов:** {N_RUNS}\n\n")
        f.write(f"- Наш dev: `{OUR_DEV}` ({len(our_dev)} примеров)\n")
        f.write(f"- Новый dev: `{args.new_dev}` ({len(new_dev)} примеров)\n\n")

        f.write("## Сравнение\n\n")
        f.write("| Метрика | dev | Новый dev | Разница |\n")
        f.write("|---------|-----|-----------|---------|\n")
        for key in ['fitness', 'accuracy', 'f1_clarification', 'invalid_combo_rate']:
            o = our_metrics[key]
            n = new_metrics[key]
            delta = n['mean'] - o['mean']
            f.write(f"| `{key}` | {o['mean']:.4f} ± {o['std']:.4f} | "
                    f"{n['mean']:.4f} ± {n['std']:.4f} | {delta:+.4f} |\n")

    print(f"\nОтчёт: {args.output}")


if __name__ == "__main__":
    main()