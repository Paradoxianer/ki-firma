import os
import json
from gpt_utils import call_ollama
from github_utils import push_file_to_repo

SUMMARY_CACHE = ".summaries.json"

def log(msg):
    print(f"📘 [readme_generator] {msg}")

def summarize_file(path):
    # Lade Cache
    summaries = {}
    if os.path.exists(SUMMARY_CACHE):
        with open(SUMMARY_CACHE, "r", encoding="utf-8") as f:
            summaries = json.load(f)

    if path in summaries:
        return summaries[path]

    try:
        with open(path, "r", encoding="utf-8") as f:
            content = f.read()
    except Exception as e:
        log(f"[WARN] Datei nicht lesbar: {path}")
        return "Datei konnte nicht gelesen werden."

    prompt = f"""
Fasse den folgenden Code in 1-3 Sätzen zusammen. Nenne dabei Zweck und Funktion der Datei:

Dateiname: {os.path.basename(path)}

Inhalt:
\"\"\"
{content}
\"\"\"

Zusammenfassung:
\"\"\"
    """

    summary = call_ollama("readme_generator", prompt).strip()

    summaries[path] = summary
    with open(SUMMARY_CACHE, "w", encoding="utf-8") as f:
        json.dump(summaries, f, indent=2, ensure_ascii=False)

    return summary

def generate_readme(project_state, repo_path, repo_name=None):
    log("📄 Generiere README.md...")

    lines = []

    # Projektbeschreibung
    lines.append("# Projektübersicht")
    lines.append(project_state.get("description", "Keine Beschreibung vorhanden."))

    # Featureliste
    lines.append("\n## Features")
    for f in project_state.get("features", []):
        desc = f.get("description", "")
        status = f.get("status", "offen")
        lines.append(f"- **{f['title']}** ({status}): {desc}")

    # Strukturübersicht
    lines.append("\n## Struktur und Dateibeschreibungen")
    for root, _, files in os.walk(repo_path):
        for file in files:
            if file.startswith(".") or file in ["README.md", "project_state.json"]:
                continue
            rel_path = os.path.relpath(os.path.join(root, file), repo_path)
            if rel_path.endswith((".py", ".dart", ".yaml")):
                summary = summarize_file(os.path.join(root, file))
                lines.append(f"### `{rel_path}`\n{summary}\n")

    # Abhängigkeiten
    lines.append("\n## Abhängigkeiten")
    pubspec = os.path.join(repo_path, "pubspec.yaml")
    requirements = os.path.join(repo_path, "requirements.txt")
    if os.path.exists(pubspec):
        lines.append("```yaml")
        lines.append(open(pubspec, encoding="utf-8").read())
        lines.append("```")
    elif os.path.exists(requirements):
        lines.append("```txt")
        lines.append(open(requirements, encoding="utf-8").read())
        lines.append("```")
    else:
        lines.append("_Keine Abhängigkeitsdateien gefunden._")

    # Speichern lokal
    readme_path = os.path.join(repo_path, "README.md")
    content = "\n".join(lines)
    with open(readme_path, "w", encoding="utf-8") as f:
        f.write(content)

    log(f"✅ README.md gespeichert unter: {readme_path}")

    # Optional: ins GitHub-Repo pushen
    if repo_name:
        push_file_to_repo(repo_name, "README.md", content, "📝 Update README")
        log("📤 README.md ins Repository übertragen.")

