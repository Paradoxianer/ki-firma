import os
from github_utils import push_file_to_repo

def write_and_commit_file(repo_name: str, local_repo_path: str, rel_path: str, content: str, commit_message: str = None):
    """
    Speichert die Datei lokal im Projekt und pusht sie ins GitHub-Repository.

    :param repo_name: Name des GitHub-Repos
    :param local_repo_path: Lokaler Pfad des Projekts
    :param rel_path: Relativer Pfad zur Datei (z. B. lib/widgets/button.dart)
    :param content: Dateiinhalte
    :param commit_message: Commit-Nachricht (optional)
    """

    full_path = os.path.join(local_repo_path, rel_path)
    os.makedirs(os.path.dirname(full_path), exist_ok=True)

    # Lokal schreiben
    with open(full_path, "w", encoding="utf-8") as f:
        f.write(content)

    # Push an GitHub
    push_file_to_repo(repo_name, rel_path, content, commit_message or f"📝 Update {rel_path}")

    return full_path
