
import os
from github_utils import (
    push_file_to_repo,
    comment_on_issue
    get_open_issues
)
from gpt_utils import (
    call_ollama    
    call_gpt_and_parse_json
)
from readme_generator import generate_readme

def log(msg):
    print(f"🎨 [frontend_agent] {msg}")

def run_frontend_agent_for_issue(issue, repo, local_path):
    number = issue["issue_number"]
    title = issue["title"]
    description = issue.get("body", "")
    open_issues = get_open_issues(repo)

    # Lies README als Projektkontext
    readme_path = os.path.join(local_path, "README.md")
    if not os.path.exists(readme_path):
        log("⚠️ README.md nicht gefunden – kein Kontext.")
        readme_context = ""
    else:
        with open(readme_path, "r", encoding="utf-8") as f:
            readme_context = f.read()

    log(f"🧠 Starte Frontend-Code Generation für Issue #{number}: {title}")
    
    prompt = f"""
Du bist ein Flutter-Frontend-Entwickler. Hier ist eine Projektübersicht:

{readme_context}

derzeit sind folgende Issues offen
{open_issues}

Bearbeite diese Aufgabe:
Titel: {title}
Beschreibung:
""" 
{description}
"""

Implementiere das Feature.
Gib den Code innerhalb eines JSON-Objekt mit folgenden Feldern zurück:

{{
  "file": "lib/screens/login_screen.dart",
  "code": "..."
}}

Der filepfad soll sinnvoll zur Funktion passen (z. B. lib/screens/, lib/widgets/, lib/services/).
"""
    response = call_gpt_and_parse_json("frontend_agent", prompt)

    filepath=response["file"]
    code = response["code"]

    if not filepath or not code:
        code = extract_dart_code(response)
        if not code
            comment = call_ollama( "ich habe folgenden Respone bekommen {response} zu folgendem prompt {prompt} Wie würdest du den issue kommentieren um beim nächsten mal sinnvollen code erstellt zu bekommen")
            comment_on_issue(repo, number, comment)
        return None

    push_file_to_repo(repo, filepath, code, f"💻 Frontend-Code für Issue #{number}")
    log(f"✅ Datei geschrieben: {filepath}")

    # README aktualisieren
    generate_readme(load_project_state(), local_path)
    return filepath
