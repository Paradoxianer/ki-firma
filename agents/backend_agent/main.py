import os
from write_utils import write_and_commit_file
from github_utils import (
    push_file_to_repo,
    comment_on_issue,
    get_open_issues
)
from gpt_utils import (
    call_ollama,
    call_gpt_and_parse_json
)
from readme_generator import generate_readme

def log(msg):
    print(f"🔧 [backend_agent] {msg}")

def load_api(local_path):
    api_path = os.path.join(local_path, "docs", "api_docs.md")
    if os.path.exists(api_path):
        with open(api_path, "r", encoding="utf-8") as f:
            return f.read()
    return ""

def update_api_docs(issue, repo, local_path, readme_context, open_issues):
    api_path = os.path.join(local_path, "docs", "api_docs.md")
    current_api = load_api(local_path)

    title = issue["title"]
    description = issue.get("body", "")

    prompt = f"""
Du bist ein Flutter-Backend-Entwickler. Hier ist die Projektübersicht:

{readme_context}

Derzeitige API-Dokumentation:
{current_api}

Offene Issues:
{open_issues}

Neue Backend-Funktion:
Titel: {title}
Beschreibung:
\"\"\"
{description}
\"\"\"

Erweitere die Markdown-API-Doku, wenn nötig. Gib die **neue api_docs.md** komplett zurück.
"""
    new_md = call_ollama(prompt)
    write_and_commit_file(repo, local_path, "docs/api_docs.md", new_md, "📄 API-Dokumentation aktualisiert")

def run_backend_agent_for_issue(issue, repo, local_path):
    number = issue["issue_number"]
    title = issue["title"]
    description = issue.get("body", "")

    # Lade Kontext
    readme_path = os.path.join(local_path, "README.md")
    readme_context = ""
    if os.path.exists(readme_path):
        with open(readme_path, "r", encoding="utf-8") as f:
            readme_context = f.read()

    open_issues = get_open_issues(repo)
    open_issues_str = "\n".join(f"- {i['title']}" for i in open_issues)

    log(f"🧠 Starte Backend-Code für Issue #{number}: {title}")

    prompt = f"""
Du bist ein Flutter-Backend-Entwickler. Hier ist die Projektübersicht:

{readme_context}

Aktuelle API-Dokumentation:
{load_api(local_path)}

Derzeitige offene Issues:
{open_issues_str}

Bearbeite diese Aufgabe:
Titel: {title}
Beschreibung:
\"\"\"
{description}
\"\"\"

Gib den Code als JSON zurück:

{{
  "file": "lib/services/my_service.dart",
  "code": "<der vollständige Dart-Code>"
}}
"""

    response = call_gpt_and_parse_json("backend_agent", prompt)

    # Fehlerbehandlung
    if not isinstance(response, dict) or "file" not in response or "code" not in response:
        comment = call_ollama(f"""
Ich habe vom GPT folgendes Response bekommen, das kein valides JSON war:

{response}

Prompt war:
{prompt}

Wie würdest du dieses Issue auf GitHub kommentieren?
""")
        comment_on_issue(repo, number, comment)
        return None

    filepath = response["file"]
    code = response["code"]

    write_and_commit_file(repo, local_path, filepath, code, f"💻 Backend-Code für Issue #{number}")
    log(f"✅ Datei geschrieben: {filepath}")

    # Aktualisiere API-Doku
    update_api_docs(issue, repo, local_path, readme_context, open_issues_str)

    # README aktualisieren
    from project_state import load_project_state  # Falls getrennt
    generate_readme(load_project_state(), local_path, repo)

    return filepath

