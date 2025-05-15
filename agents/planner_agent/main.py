
import os
import json
from dotenv import load_dotenv
from gpt_utils import call_gpt_and_parse_json
from github_utils import get_open_issues, update_issue_labels

load_dotenv()

def log(msg):
    print(f"📌 [planner_agent] {msg}")

def generate_feature_tasks(feature_title, feature_description, repo_name=None):
    log(f"🧠 Erstelle Aufgaben für Feature: {feature_title}")
    existing_issues = get_open_issues(repo_name) if repo_name else []
    existing_issues_text = json.dumps(existing_issues, indent=2) if existing_issues else "[]"

    prompt = f"""
Du bist Planer für die Entwicklung einer Flutter App
Was wäre die nächste wichtigste und sinnvolle  zu implentieren...
für folgendes Feature eines Softwareprojekts:

Titel: {feature_title}
Beschreibung: {feature_description}

Diese Aufgaben existieren bereits im Projekt:
{existing_issues_text}

Erzeuge daraus notwendige Aufgaben die implementiert werden müssen und noch kein Issue haben, mit einer ausführlichen und klaren Beschreibung.
Erstelle nur neue Aufgaben, falls nötig. Jede Aufgabe soll Titel, Beschreibung und ein passendes Label (frontend, backend, qa oder devops) enthalten.

Format:
[
  {{
    "title": "...",
    "body": "...",
    "labels": ["frontend"]
  }},
  ...
]
"""
    aufgaben = call_gpt_and_parse_json("planner_agent", prompt)
    # ✅ Rückgabe prüfen und nur gültige Aufgaben weitergeben
    def is_valid_task(task):
        return isinstance(task, dict) and "title" in task and "labels" in task

    if not isinstance(aufgaben, list):
        print("[WARN] GPT-Antwort war kein Aufgaben-Array. Rückgabe wird ignoriert.")
        aufgaben = []

    valid_tasks = [t for t in aufgaben if is_valid_task(t)]
    invalid_tasks = [t for t in aufgaben if not is_valid_task(t)]

    if invalid_tasks:
        print(f"[WARN] Ungültige Aufgaben gefunden und ignoriert: {invalid_tasks}")

    return valid_tasks
    return 

def prioritize_issues(repo):
    issues = get_open_issues(repo)
    if not issues:
        log("✅ Keine offenen Issues gefunden.")
        return

    prompt = f"""
Du bist ein Projektmanager. Priorisiere die folgenden Aufgaben anhand von Titel, Beschreibung und Labels. Vergib pro Aufgabe eine Priorität von 1 (hoch) bis 3 (niedrig) und gib aktualisierte Labels zurück:

{json.dumps(issues, indent=2)}

Format:
[
  {{
    "number": 23,
    "priority": 1,
    "labels": ["frontend", "open"]
  }},
  ...
]
"""

    prioritized = call_gpt_and_parse_json("planner_agent", prompt)
    for item in prioritized:
        number = item["number"]
        labels = item["labels"]
        prio = item["priority"]
        if f"prio{prio}" not in labels:
            labels.append(f"prio{prio}")
        update_issue_labels(repo, number, labels)
        log(f"✅ Issue #{number} aktualisiert mit Labels: {labels}")

# Für CLI-Test
if __name__ == "__main__":
    test = generate_feature_tasks("Loginseite", "Ein Nutzer kann sich anmelden und die App verwenden.", "mitglieder_app")
    print(json.dumps(test, indent=2, ensure_ascii=False))
