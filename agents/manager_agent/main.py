
import os
import json
import time
from dotenv import load_dotenv
from gpt_utils import call_gpt_and_parse_json

from github_utils import (
    create_or_update_repo,
    create_github_issue,
    get_open_issues,
    update_issue_labels,
    push_file_to_repo
)
from readme_generator import generate_readme

load_dotenv()
TEMPLATE_DIR = os.path.join(os.path.dirname(__file__), "templates")
PROJECT_STATE_FILE = "project_state.json"


def log(msg):
    print(f"🧠 [manager_agent] {msg}")

def push_template_file(repo, rel_path, target_path):
    full_path = os.path.join(TEMPLATE_DIR, rel_path)
    log(f"📋 Übertrage Template: {rel_path} → {target_path}")
    with open(full_path, "r") as f:
        content = f.read()
    push_file_to_repo(repo, target_path, content, f"Add {target_path}")

def load_project_state():
    if os.path.exists(PROJECT_STATE_FILE):
        with open(PROJECT_STATE_FILE, "r", encoding="utf-8") as f:
            return json.load(f)
    return {"features": [], "description": ""}

def save_project_state(state):
    with open(PROJECT_STATE_FILE, "w", encoding="utf-8") as f:
        json.dump(state, f, indent=2, ensure_ascii=False)

def generate_feature_list(description):
    log("📃 Featureliste wird generiert...")
    prompt = f"""
Du bist ein Projektplaner. Erstelle auf Basis dieser Beschreibung eine Liste von Features mit Titel, Beschreibung und Priorität (1 = hoch):

\"\"\"
{description}
\"\"\"

Format:
[
  {{
    "title": "...",
    "description": "...",
    "priority": 1
  }},
  ...
]
"""
    return call_gpt_and_parse_json("manager_agent", prompt)

def generate_feature_tasks(feature_title, feature_description):
    log(f"🧩 Erzeuge Tasks für Feature: {feature_title}")
    from agents.planner_agent.main import generate_feature_tasks
    return generate_feature_tasks(feature_title, feature_description)

def plan_next_actions(issues):
    log("🧠 GPT plant die nächsten Schritte...")
    prompt_base = f"""
Du bist ein KI-Projektleiter. Entscheide anhand dieser offenen Aufgaben (Titel, Labels, Priorität), welche als Nächstes bearbeitet werden sollen. Gib die nächsten 3–5 Schritte zurück:

{json.dumps(issues, indent=2)}

Format:
[
  {{
    "agent": "frontend" | "backend" | "qa" | "devops",
    "issue_number": int
  }}
]
"""
    prompt = prompt_base

    for attempt in range(3):
        result = call_gpt_and_parse_json("manager_agent", prompt)

        if isinstance(result, list) and all("agent" in r and "issue_number" in r for r in result):
            return result

        log(f"⚠️ Versuch {attempt+1}/3 fehlgeschlagen – Anfrage wird neu gestellt.")

        prompt = f"""
Die vorherige Antwort war kein gültiges JSON im folgenden Format:

[
  {{
    "agent": "frontend" | "backend" | "qa" | "devops",
    "issue_number": int
  }}
]

Hier sind die offenen Aufgaben:
{json.dumps(issues, indent=2)}
Bitte antworte **nur** mit einer gültigen JSON-Liste wie oben.
"""

    log("❌ GPT konnte keinen gültigen Plan liefern.")
    return []


def call_agent_by_name(agent, repo, local_path):
    log(f"🤝 Übergabe an Agent: {agent}")
    try:
        module = __import__(f"agents.{agent}_agent.main", fromlist=["run"])
        if agent == "qa":
            module.run_qa_agent(repo, local_path)
        else:
            getattr(module, f"run_{agent}_agent")(repo)
    except Exception as e:
        log(f"❌ Fehler beim Agent '{agent}': {e}")
        suggest_fix_with_gpt(agent, str(e))

def suggest_fix_with_gpt(agent_name, error_msg):
    log("📡 Anfrage an GPT zur Fehlerdiagnose...")
    prompt = f"""
Ich habe beim Starten eines Python-Moduls für einen Agenten einen Fehler erhalten:

Agent: {agent_name}
Fehlermeldung: {error_msg}

Was ist wahrscheinlich die Ursache und wie kann ich es beheben?
"""
    result = call_gpt_and_parse_json("manager_agent", prompt)
    print("💡 GPT-Vorschlag zur Fehlerbehebung:")
    print(json.dumps(result, indent=2, ensure_ascii=False))

def setup_project():
    log("🚀 Initialisiere Projekt...")
    repo = input("📦 Projektname: ").strip()
    description = input("🧠 Projektbeschreibung: ").strip()
    local_path = input("📁 Lokaler Pfad (für Tests): ").strip()

    if not create_or_update_repo(repo, description):
        log("❌ Repo konnte nicht erstellt oder aktualisiert werden.")
        return

    push_template_file(repo, "workflows/flutter.yml", ".github/workflows/flutter.yml")
    push_template_file(repo, "workflows/test.yml", ".github/workflows/test.yml")

    # Lade oder erzeuge Projektstatus
    project_state = load_project_state()
    max_rounds = 3

    if not project_state.get("features"):
        features = generate_feature_list(description)
        project_state["features"] = features
        project_state["description"] = description
        save_project_state(project_state)

    # Iteriere über ALLE Features – keine Statusprüfung
    for f in project_state["features"]:
        title = f["title"]
        desc = f["description"]

        log(f"🚀 Bearbeite Feature: {title}")
        tasks = generate_feature_tasks(title, desc)

        for round_think in range(max_rounds):
            for t in tasks:
                if "title" in t and "labels" in t:
                    create_github_issue(repo, t["title"], t.get("body", ""), t.get("labels", []))
                else:
                    print(f"[WARN] Ungültige Aufgabe übersprungen: {t}")

            issues = get_open_issues(repo)
            plan = plan_next_actions(issues)

            for step in plan:
                log(f"🔁 Starte Agent {step['agent']} für Issue #{step['issue_number']}")
                for round_num in range(max_rounds):
                    call_agent_by_name(step["agent"], repo, local_path)

                    if step["agent"] == "qa":
                        if qa_agent_detected_issues():
                            log("🔁 QA meldet Fehler – neue Iteration")
                        else:
                            log("✅ QA erfolgreich – Schleife abgeschlossen")
                            break  # QA war erfolgreich → zur nächsten Planungseinheit

        save_project_state(project_state)
        generate_readme(project_state, local_path, repo)

        log(f"📌 Feature '{title}' wurde verarbeitet – Status bitte manuell prüfen.")

    
    
if __name__ == "__main__":
    setup_project()
