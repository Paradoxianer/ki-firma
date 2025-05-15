
import os
import json
import re
import requests
from datetime import datetime

OLLAMA_URL = os.getenv("OPENAI_API_BASE", "http://localhost:11434")
OLLAMA_MODEL = os.getenv("OPENAI_MODEL", "deepseek-coder:6.7b")

LOG_PATH = "logs/gpt/gpt_log.txt"
os.makedirs("logs/gpt", exist_ok=True)

def log_gpt_interaction(agent_name, prompt, response):
    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    with open(LOG_PATH, "a", encoding="utf-8") as f:
        f.write("=" * 80 + "\n")
        f.write(f"[{timestamp}] Agent: {agent_name}\n")
        f.write(">>> PROMPT:\n")
        f.write(prompt.strip() + "\n\n")
        f.write(">>> RESPONSE:\n")
        f.write(response.strip() + "\n\n")

def extract_json_from_text(text):
    try:
        match = re.search(r"```json\s*(\[.*?\])\s*```", text, re.DOTALL)
        if match:
            return json.loads(match.group(1))
        start = text.find("[")
        end = text.rfind("]")
        if start != -1 and end != -1:
            return json.loads(text[start:end+1])
    except Exception:
        pass
    return None

def extract_code_block(text, language=None):
    pattern = r"```" + (language if language else "") + r"\s*(.*?)```"
    match = re.search(pattern, text, re.DOTALL)
    return match.group(1).strip() if match else text.strip()

def call_ollama(prompt):
    response = requests.post(
        f"{OLLAMA_URL}/api/generate",
        json={"model": OLLAMA_MODEL, "prompt": prompt, "stream": False}
    )
    if not response.ok:
        raise Exception(f"Ollama-Fehler: {response.status_code} - {response.text}")
    return response.json().get("response", "").strip()

def call_gpt_and_parse_json(agent_name, prompt, max_attempts=10):
    for attempt in range(max_attempts):
        result = call_ollama(prompt)
        log_gpt_interaction(agent_name, prompt, result)

        try:
            return json.loads(result)
        except json.JSONDecodeError:
            parsed = extract_json_from_text(result)
            if parsed:
                return parsed
            prompt = f"""
Es wurde folgende Frage an Deepseek gestellt
"""
prompt
"""
Deepseek lieferte folgendes zurück

"""
{result}
"""
Die Ausgabe konnte nicht als JSON geparsed werden. 
Erwartetes Format: Liste von Objekten. Gib einen verbesserten Prompt zurück
"""
            prompt = call_ollama(prompt)
    raise ValueError("GPT konnte nach mehreren Versuchen kein gültiges JSON liefern.")
