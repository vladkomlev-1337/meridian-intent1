import json
import os
from pathlib import Path
from openai import OpenAI

INTENTS = [
    "greeting", "capabilities", "gratitude", "data_catalog",
    "pivot_table", "technical", "support", "no_rag",
]

SYSTEM_PROMPT = """Ты - классификатор намерений платформы "Меридиан" компании "Аркадия".

Верни JSON: {"intent": "<класс>", "needs_clarification": <true|false>}

КЛАССЫ:
- greeting: приветствие/нейтральное прощание без рабочей задачи
- capabilities: вопрос о функциях/возможностях ассистента
- gratitude: благодарность/подтверждение завершённости
- data_catalog: поиск объектов данных (таблицы/витрины/дашборды)
- pivot_table: построение/изменение числовой сводной таблицы
- technical: содержательный вопрос/объяснение/методика/ошибка/доступ/продукт (по умолчанию)
- support: явная просьба об операторе или выбор варианта с оператором
- no_rag: ответ целиком по истории (повтор/сокращение/перевод/оформление)

ПРАВИЛА:
- needs_clarification=true ТОЛЬКО для data_catalog, когда неясно: искать объекты или объяснять тему
- При сомнении support/technical, pivot_table/technical, no_rag/technical — выбирай technical
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
            temperature=0.2,
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
    # Инвариант: clar только для data_catalog
    if intent != "data_catalog":
        clar = False
    return {"intent": intent, "needs_clarification": clar}

def classify_all(dev_data):

    predictions = []
    for item in dev_data:
        pred = classify(item["history"], item["text"])
        predictions.append(pred)
    return predictions

def entrypoint():
    dev_path = os.environ.get(
        "DEV_PATH",
        "problems/meridian_intent/data/dev.jsonl"
    )
    with open(dev_path, "r", encoding="utf-8") as f:
        dev = [json.loads(line) for line in f if line.strip()]

    predictions = []
    for item in dev:
        pred = classify(item["history"], item["text"])
        predictions.append(pred)

    return predictions