import json
import os
from pathlib import Path
from openai import OpenAI

INTENTS = [
    "greeting", "capabilities", "gratitude", "data_catalog",
    "pivot_table", "technical", "support", "no_rag",
]

SYSTEM_PROMPT = """Ты - классификатор намерений.

Верни JSON: {"intent": "<класс>", "needs_clarification": <true|false>}

КЛАССЫ:
- greeting
- capabilities
- gratitude
- data_catalog
- pivot_table
- technical
- support
- no_rag

ПРАВИЛА:
- needs_clarification=true только для data_catalog.
"""


def _client():
    return OpenAI(
        base_url=os.environ.get("LOCAL_LLM_PROXY", "http://localhost:8090/v1"),
        api_key=os.environ.get("OPENAI_API_KEY", "my-super-secret-key"),
    )


def classify(history, text):
    messages = [{"role": "system", "content": SYSTEM_PROMPT}]
    for msg in history:
        messages.append({"role": msg["role"], "content": msg["content"]})
    messages.append({"role": "user", "content": text})

    try:
        resp = _client().chat.completions.create(
            model="GigaChat-3-Ultra",
            messages=messages,
            temperature=0.0,
            max_tokens=200,
        )
        raw = resp.choices[0].message.content
        data = json.loads(raw)
    except Exception:
        return {"intent": "technical", "needs_clarification": False}

    intent = data.get("intent", "technical")
    if intent not in INTENTS:
        intent = "technical"
    clar = bool(data.get("needs_clarification", False))
    if clar and intent != "data_catalog":
        clar = False
    return {"intent": intent, "needs_clarification": clar}


def entrypoint():
    dev_path = Path("problems/meridian_intent/data/dev.jsonl")
    with open(dev_path, "r", encoding="utf-8") as f:
        dev = [json.loads(line) for line in f if line.strip()]

    predictions = []
    for item in dev:
        pred = classify(item["history"], item["text"])
        predictions.append(pred)

    return predictions