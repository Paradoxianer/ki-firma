import os
import requests
import re

from dotenv import load_dotenv

load_dotenv()

GITHUB_USERNAME = os.getenv("GITHUB_USERNAME")
GITHUB_TOKEN = os.getenv("GITHUB_TOKEN")
PROJECT_ID = "HA_Offizier"
REPO_NAME = PROJECT_ID
HEADERS = {
    "Authorization": f"token {GITHUB_TOKEN}",
    "Accept": "application/vnd.github+json"
}

ARTIFACTS_DIR = os.path.join(os.path.dirname(__file__), "artifacts")
ARTIFACTS = ["app-release.apk", "web.zip"]

def get_next_version(repo):
    url = f"https://api.github.com/repos/{GITHUB_USERNAME}/{repo}/releases"
    r = requests.get(url, headers=HEADERS)
    if r.status_code != 200:
        print(f"⚠️ Fehler beim Abrufen der Releases: {r.status_code}")
        return "v1.0.0"

    releases = r.json()
    version_pattern = re.compile(r"v(\d+)\.(\d+)\.(\d+)")

    max_version = (1, 0, -1)  # Start bei -1, damit v1.0.0 korrekt ist

    for release in releases:
        tag = release.get("tag_name", "")
        match = version_pattern.match(tag)
        if match:
            major, minor, patch = map(int, match.groups())
            if (major, minor, patch) > max_version:
                max_version = (major, minor, patch)

    next_patch = max_version[2] + 1
    next_version = f"v{max_version[0]}.{max_version[1]}.{next_patch}"
    return next_version


def get_latest_commit_sha(repo):
    url = f"https://api.github.com/repos/{GITHUB_USERNAME}/{repo}/commits/main"
    r = requests.get(url, headers=HEADERS)
    return r.json()["sha"] if r.status_code == 200 else None

def create_release(repo, tag_name, release_name, body="Automatisch erstellt"):
    url = f"https://api.github.com/repos/{GITHUB_USERNAME}/{repo}/releases"
    data = {
        "tag_name": tag_name,
        "target_commitish": "main",
        "name": release_name,
        "body": body,
        "draft": False,
        "prerelease": False
    }
    r = requests.post(url, json=data, headers=HEADERS)
    if r.status_code == 201:
        print(f"🚀 Release {tag_name} erstellt.")
        return r.json()["upload_url"].split("{")[0]  # Nur den Upload-Teil
    else:
        print(f"❌ Fehler beim Release: {r.status_code} → {r.text}")
        return None

def upload_asset(upload_url, filepath):
    filename = os.path.basename(filepath)
    headers = HEADERS.copy()
    headers["Content-Type"] = "application/octet-stream"

    with open(filepath, "rb") as f:
        data = f.read()

    params = {"name": filename}
    url = f"{upload_url}?name={filename}"
    r = requests.post(url, headers=headers, data=data)

    if r.status_code == 201:
        print(f"📦 Datei '{filename}' erfolgreich hochgeladen.")
    else:
        print(f"❌ Fehler beim Hochladen von '{filename}': {r.status_code} – {r.text}")

if __name__ == "__main__":
    print("🔧 DevOps-Agent mit Anhang-Upload gestartet...")
    sha = get_latest_commit_sha(REPO_NAME)

    if sha:
        version = get_next_version(REPO_NAME)
        upload_url = create_release(REPO_NAME, version, f"{PROJECT_ID} – Erstveröffentlichung")

        if upload_url:
            for artifact in ARTIFACTS:
                path = os.path.join(ARTIFACTS_DIR, artifact)
                if os.path.isfile(path):
                    upload_asset(upload_url, path)
                else:
                    print(f"⚠️ Datei fehlt: {artifact}")
    else:
        print("⚠️ Kein Commit gefunden.")

