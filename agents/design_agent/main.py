
import os
import json
import re
import requests
from dotenv import load_dotenv
from gpt_logger import log_gpt_interaction


load_dotenv()

OLLAMA_URL = os.getenv("OPENAI_API_BASE", "http://localhost:11434")
OLLAMA_MODEL = os.getenv("OPENAI_MODEL", "deepseek-coder:6.7b")
GITHUB_USERNAME = os.getenv("GITHUB_USERNAME")
GITHUB_TOKEN = os.getenv("GITHUB_TOKEN")
HEADERS = {
    "Authorization": f"token " + GITHUB_TOKEN,
    "Accept": "application/vnd.github+json"
}

def log(msg):
    print(f"🎨 [design_agent] {msg}")

def ollama_chat(prompt):
    log("🤖 Anfrage an GPT wird gestellt...")
    response = requests.post(
        f"{OLLAMA_URL}/api/generate",
        json={"model": OLLAMA_MODEL, "prompt": prompt, "stream": False}
    )
    if response.ok:
        answer = response.json().get("response", "").strip()
        log_gpt_interaction("🎨 [design_agent]", prompt, answer)
        return response.json().get("response", "").strip()
    else:
        raise Exception(f"Ollama-Fehler: {response.status_code} - {response.text}")

def extract_json_from_text(text):
    try:
        match = re.search(r"```json\s*(\{.*?\})\s*```", text, re.DOTALL)
        if match:
            return json.loads(match.group(1))
        brace_start = text.find("{")
        brace_end = text.rfind("}")
        if brace_start != -1 and brace_end != -1:
            return json.loads(text[brace_start:brace_end+1])
    except Exception as e:
        log("⚠️ Konnte JSON aus Text nicht extrahieren.")
    return None

def create_design_issue(repo, title, body, labels=["design", "frontend", "open"]):
    url = f"https://api.github.com/repos/{GITHUB_USERNAME}/{repo}/issues"
    data = {"title": title, "body": body, "labels": labels}
    requests.post(url, headers=HEADERS, json=data)

def run_design_agent(repo_name, feature_title, feature_description):
    log(f"🧠 Starte Design-Agent für: {feature_title}")
    prompt = f"""
Du bist ein UI/UX-Designer für eine mobile App. Erstelle einen Designvorschlag für folgendes Feature:

Titel: {feature_title}
Beschreibung: {feature_description}

Deine Antwort soll ASCII-Mockups, Komponentenstruktur für Flutter und Design-Empfehlungen enthalten.
Gib alles als Markdown-Text zurück.
"""

    result = None
    for attempt in range(10):
        raw = ollama_chat(prompt)
        if raw.strip():
            result = raw.strip()
            break
        log(f"⚠️ Versuch {attempt+1}/10: Leere GPT-Antwort.")
    if not result:
        log("❌ GPT konnte keine gültige Designbeschreibung liefern.")
        return

    issue_title = f"Designvorschlag: {feature_title}"
    create_design_issue(repo_name, issue_title, result)
    log(f"📐 Design-Issue '{issue_title}' wurde im Repo '{repo_name}' erstellt.")

if __name__ == "__main__":
    import argparse
    parser = argparse.ArgumentParser()
    parser.add_argument("--repo", required=True)
    parser.add_argument("--title", required=True)
    parser.add_argument("--description", required=True)
    args = parser.parse_args()

    run_design_agent(args.repo, args.title, args.description)
