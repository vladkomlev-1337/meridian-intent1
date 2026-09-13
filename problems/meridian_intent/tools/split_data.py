import json
from pathlib import Path
input_path = Path("problems/meridian_intent/data/examples.jsonl")
output_path = Path("problems/meridian_intent/data")
def clean_item(item: dict) -> dict:
    return {
        "id" : item["id"],
        "group_id" : item["group_id"],
        "history" : item["history"],
        "text" : item["text"],
        "intent" : item["intent"],
        "needs_clarification" : item["needs_clarification"],
    }
def main():
    train, dev = [], []
    with open(input_path, "r", encoding="utf-8") as file:
        for line in file:
            line = line.strip()
            if not line:
                continue
            item = json.loads(line)
            clean = clean_item(item)
            if item["split"] == "train":
                train.append(clean)
            elif item["split"] == "dev":
                dev.append(clean)
            else:
                raise ValueError(f"неизвестный split: {item['split']} в {item['id']}")
    with open(output_path / "train.jsonl", "w", encoding="utf-8") as file:
        for item in train:
            file.write(json.dumps(item, ensure_ascii=False) + "\n")
    with open(output_path / "dev.jsonl", "w", encoding="utf-8") as file:
        for item in dev:
            file.write(json.dumps(item, ensure_ascii=False) + "\n")
if __name__ == "__main__":
    main()