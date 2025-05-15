
import os
import json
import subprocess
from dotenv import load_dotenv
from gpt_utils import call_ollama, extract_code_block, log_gpt_interaction
from github_utils import (
    get_open_issues,
    get_file_from_repo,
    push_file_to_repo,
    create_github_issue,
    close_issue,
    update_issue_labels
)

load_dotenv()

def log(msg):
    print(f"🧪 [qa_agent] {msg}")

def generate_test_code(title, code):
    prompt = f"""
Du bist ein Flutter-Testentwickler.
Erstelle eine vollständige Testdatei mit `flutter_test`, um dieses Widget zu testen:

Titel: {title}

Widget-Quellcode:
```dart
{code}
```

Verwende `testWidgets`, prüfe auf sichtbare Texte, Buttons, Eingabefelder.
Gib **nur den Dart-Testcode** zurück.
"""
    result = call_ollama(prompt)
    log_gpt_interaction("qa_agent", prompt, result)
    return extract_code_block(result, "dart")

def run_flutter_tests(project_path):
    log("▶️ Starte `flutter test`...")
    try:
        result = subprocess.run(
            ["flutter", "test"],
            cwd=project_path,
            stdout=subprocess.PIPE,
            stderr=subprocess.STDOUT,
            text=True,
            timeout=90
        )
        print(result.stdout)
        return "All tests passed" in result.stdout
    except Exception as e:
        log(f"❌ Fehler beim Ausführen von Tests: {e}")
        return False

def run_qa_agent(repo_name, local_path):
    issues = get_open_issues(repo_name)
    review_issues = [i for i in issues if "qa" in i["labels"] and "done" not in i["labels"]]

    if not review_issues:
        log("✅ Keine offenen QA-Issues.")
        return

    all_passed = True
    results = []

    for issue in review_issues:
        number = issue["issue_number"]
        title = issue["title"].replace("Überprüfen: ", "").strip()
        filename = title.lower().replace(" ", "_") + ".dart"
        widget_path = f"lib/{filename}"
        test_path = os.path.join(local_path, "test", filename.replace(".dart", "_test.dart"))

        log(f"🧪 Erzeuge Test für: {title} (#{number})")
        code = get_file_from_repo(repo_name, widget_path)
        if not code:
            log(f"⚠️ Datei nicht gefunden: {widget_path}")
            continue

        test_code = generate_test_code(title, code)

        os.makedirs(os.path.dirname(test_path), exist_ok=True)
        with open(test_path, "w", encoding="utf-8") as f:
            f.write(test_code)

        log("▶️ Führe Tests aus...")
        result = subprocess.run(
            ["flutter", "test"],
            cwd=local_path,
            stdout=subprocess.PIPE,
            stderr=subprocess.STDOUT,
            text=True,
            timeout=90
        )
        passed = "All tests passed" in result.stdout
        results.append({"issue": number, "passed": passed, "output": result.stdout})
        all_passed = all_passed and passed

        if passed:
            log(f"✅ Tests bestanden – schließe Issue #{number}")
            close_issue(repo_name, number)
        else:
            log(f"❌ Tests fehlgeschlagen – Kommentiere & Bug-Issue wird erstellt")

            # Kommentar auf ursprüngliches Issue
            comment_on_issue(repo_name, number, f"❌ Test fehlgeschlagen:\n```\n{result.stdout[:1000]}\n```")

            # GPT erzeugt Bugbeschreibung
            from gpt_utils import call_gpt_and_parse_json
            bug = call_gpt_and_parse_json("qa_agent", f"""
Ein automatischer Flutter-Test ist fehlgeschlagen. Erstelle daraus ein kurzes Bug-Issue.

Fehlermeldung:
\"\"\"
{result.stdout[:1200]}
\"\"\"

Format:
{{
  "title": "...",
  "body": "...",
  "labels": ["bug"]
}}
""")

            if isinstance(bug, dict) and "title" in bug:
                create_github_issue(repo_name, bug["title"], bug["body"], bug.get("labels", ["bug"]))
                update_issue_labels(repo_name, number, ["qa", "bug"])

    # QA-Report speichern
    report = {
        "status": "success" if all_passed else "failed",
        "results": results,
        "failures": [r for r in results if not r["passed"]]
    }
    with open("qa_report.json", "w", encoding="utf-8") as f:
        json.dump(report, f, indent=2)

    log("📄 QA-Report gespeichert.")

if __name__ == "__main__":
    run_qa_agent("dein_repo_name", "/pfad/zum/projekt")
