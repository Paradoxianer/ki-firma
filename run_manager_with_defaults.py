import subprocess
import sys
import os

if not os.path.exists("agents/manager_agent/main.py"):
    print("❌ Script bitte aus dem Projektstammverzeichnis starten!")
    sys.exit(1)

proc = subprocess.Popen(
    ["python3", "-u", "-m", "agents.manager_agent.main"],  # -u = unbuffered
    stdin=subprocess.PIPE,
    stdout=subprocess.PIPE,
    stderr=subprocess.STDOUT,
    text=True
)

defaults = [
    "mitglieder_app\n",
    "Eine einfache App zur Verwaltung von Mitgliedern. Die App zeigt eine Startseite mit Login. Nach dem Login sieht der Nutzer eine Liste von Mitgliedern mit Namen, E-Mail-Adresse und einem Button zur Detailansicht. Es soll außerdem eine Seite geben, um ein neues Mitglied hinzuzufügen. Das Design soll schlicht und modern sein.\n",
    "/home/matthias/development\n"
]

for line in defaults:
    proc.stdin.write(line)
    proc.stdin.flush()

for output in proc.stdout:
    print(output, end="")

