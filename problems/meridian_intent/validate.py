import json
from pathlib import Path
from sklearn.metrics import f1_score, accuracy_score

INTENTS = [
    "greeting", "capabilities", "gratitude", "data_catalog",
    "pivot_table", "technical", "support", "no_rag",
]

DEV_PATH = Path("problems/meridian_intent/data/dev.jsonl")


def _load_dev():
    with open(DEV_PATH, "r", encoding="utf-8") as f:
        return [json.loads(line) for line in f if line.strip()]


def validate_with_dev(program_output, dev_data):
    predictions = program_output  # 30
    dev = dev_data  # 30 ← правильные ответы для нового dev
    if len(predictions) != len(dev):
        return {
            "fitness": -1000.0,
            "accuracy": 0.0,
            "f1_clarification": 0.0,
            "invalid_combo_rate": 1.0,
            "is_valid": 0.0,
            "error": f"Expected list of {len(dev)} predictions, got {type(predictions).__name__}",
        }

    y_true, y_pred = [], []
    clar_true, clar_pred = [], []
    invalid_count = 0

    for item, pred in zip(dev, predictions):
        if isinstance(pred, dict):
            intent = pred.get("intent", "technical")
            clar = bool(pred.get("needs_clarification", False))
        else:
            intent = "technical"
            clar = False

        if intent not in INTENTS:
            intent = "technical"

        y_true.append(item["intent"])
        y_pred.append(intent)
        clar_true.append(item["needs_clarification"])
        clar_pred.append(clar)

        if clar and intent != "data_catalog":
            invalid_count += 1

    macro_f1 = f1_score(y_true, y_pred, average="macro", labels=INTENTS, zero_division=0)
    accuracy = accuracy_score(y_true, y_pred)
    f1_clar = f1_score(clar_true, clar_pred, zero_division=0)
    invalid_rate = invalid_count / len(y_true) if y_true else 1.0

    return {
        "fitness": float(macro_f1),
        "accuracy": float(accuracy),
        "f1_clarification": float(f1_clar),
        "invalid_combo_rate": float(invalid_rate),
        "is_valid": 1.0,
    }