
import os
import json
import base64
import requests
from dotenv import load_dotenv

# Lade Umgebungsvariablen aus zentraler .env
load_dotenv()

GITHUB_USERNAME = os.getenv("GITHUB_USERNAME")
GITHUB_TOKEN = os.getenv("GITHUB_TOKEN")

HEADERS = {
    "Authorization": f"token {GITHUB_TOKEN}",
    "Accept": "application/vnd.github+json"
}

def create_or_update_repo(repo_name, description="KI-Projekt"):
    url = f"https://api.github.com/repos/{GITHUB_USERNAME}/{repo_name}"
    res = requests.get(url, headers=HEADERS)
    if res.status_code == 200:
        repo_info = res.json()
        if repo_info.get("description", "") != description:
            patch = requests.patch(url, headers=HEADERS, json={"description": description})
        return True
    data = {"name": repo_name, "description": description, "private": False}
    r = requests.post("https://api.github.com/user/repos", json=data, headers=HEADERS)
    return r.status_code == 201

def create_github_issue(repo, title, body="", labels=None):
    url = f"https://api.github.com/repos/{GITHUB_USERNAME}/{repo}/issues"
    data = {"title": title, "body": body, "labels": labels or ["open"]}
    return requests.post(url, headers=HEADERS, json=data)

def comment_on_issue(repo, issue_number, comment_text):
    github_token = os.getenv("GITHUB_TOKEN")
    if not github_token:
        raise EnvironmentError("GITHUB_TOKEN nicht gesetzt")

    url = f"https://api.github.com/repos/{repo}/issues/{issue_number}/comments"
    headers = {
        "Authorization": f"Bearer {github_token}",
        "Accept": "application/vnd.github+json"
    }
    data = {
        "body": comment_text
    }

    response = requests.post(url, headers=headers, json=data)
    if response.status_code == 201:
        print(f"💬 Kommentar zu Issue #{issue_number} erfolgreich erstellt.")
    else:
        print(f"⚠️ Fehler beim Kommentieren: {response.status_code} – {response.text}")


def get_open_issues(repo):
    url = f"https://api.github.com/repos/{GITHUB_USERNAME}/{repo}/issues"
    res = requests.get(url, headers=HEADERS, params={"state": "open"})
    issues = []
    if res.status_code == 200:
        for i in res.json():
            if "pull_request" not in i:
                labels = [l["name"] for l in i.get("labels", [])]
                issues.append({
                    "issue_number": i["number"],
                    "title": i["title"],
                    "labels": labels
                })
    return issues

def get_all_issues(repo):
    url = f"https://api.github.com/repos/{GITHUB_USERNAME}/{repo}/issues"
    res = requests.get(url, headers=HEADERS)
    return res.json() if res.status_code == 200 else []

def update_issue_labels(repo, issue_number, labels):
    url = f"https://api.github.com/repos/{GITHUB_USERNAME}/{repo}/issues/{issue_number}"
    requests.patch(url, headers=HEADERS, json={"labels": labels})

def push_file_to_repo(repo, path, content, message):
    url = f"https://api.github.com/repos/{GITHUB_USERNAME}/{repo}/contents/{path}"
    encoded = base64.b64encode(content.encode()).decode()
    data = {"message": message, "content": encoded}
    return requests.put(url, headers=HEADERS, json=data)

def get_file_from_repo(repo, path):
    url = f"https://api.github.com/repos/{GITHUB_USERNAME}/{repo}/contents/{path}"
    res = requests.get(url, headers=HEADERS)
    if res.status_code == 200:
        content = res.json().get("content", "")
        return base64.b64decode(content).decode()
    return ""

def close_issue(repo, issue_number):
    url = f"https://api.github.com/repos/{GITHUB_USERNAME}/{repo}/issues/{issue_number}"
    requests.patch(url, headers=HEADERS, json={"state": "closed"})
