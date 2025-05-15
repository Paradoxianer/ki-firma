# KI-Firma – GPT-gesteuerte Software-Generierungsplattform

Die **KI-Firma** ist ein modulares Python-basiertes Agentensystem, das mithilfe von GPT automatisch komplette Flutter-Apps generieren, testen und dokumentieren kann. Ziel ist es, durch ein koordiniertes Agentensystem den gesamten Entwicklungsprozess – von der Feature-Planung bis zur Auslieferung – zu automatisieren.

## 🔧 Hauptfunktionen

- 🧠 Automatisierte Feature-Planung mit GPT
- ✍️ Codegenerierung für Frontend und Backend (Flutter)
- ✅ Automatische Testgenerierung und -ausführung (Flutter-Tests)
- 📄 API-Dokumentation durch GPT-Erweiterung
- 📘 Dynamische README-Erzeugung basierend auf Codeinhalten
- 🧪 QA-Agent mit Fehlerrückführung
- 🔁 Feedback-Schleifen und Multi-Runden-Iteration
- 🗣️ Agenten kommunizieren über Github Issues
- 🗃️ GitHub-Integration: Issues, Commits, Kommentare, Labels

## 🧱 Projektstruktur

```
ki-firma/
├── agents/
│   ├── manager_agent/       → Koordiniert alle Schritte
│   ├── planner_agent/       → Generiert Aufgaben aus Feature-Beschreibung
│   ├── frontend_agent/      → Erstellt Flutter-UI-Code
│   ├── backend_agent/       → Erstellt Service-/Logikcode + API-Doku
│   ├── qa_agent/            → Führt Tests aus, meldet Fehler
├── gpt_utils.py             → GPT-Kommunikation & Parsing
├── github_utils.py          → GitHub API-Hilfsfunktionen
├── readme_generator.py      → Erzeugt README.md aus Projektstatus + Code
├── project_state.json       → Lokaler Zustand des Projekts (Features, Beschreibung)
├── .env                     → Umgebungsvariablen (z. B. GITHUB_TOKEN)
├── .summaries.json          → Zwischenspeicher für Dateizusammenfassungen
└── docs/
    └── api_docs.md          → Automatisch generierte API-Dokumentation
```

## 🚀 Erste Schritte

### 1. Repository klonen

```bash
git clone https://github.com/Paradoxianer/ki-firma.git
cd ki-firma
```

### 2. Umgebung vorbereiten

- Python 3.10+
- `.env`-Datei mit `GITHUB_TOKEN` (Repo-Write-Rechte)

```env
GITHUB_TOKEN=ghp_...
```

### 3. Projekt starten

```bash
python agents/manager_agent/main.py
```

Dann interaktiv:
- Projektname
- Projektbeschreibung
- Lokaler Pfad (für Flutter-Repo)

### 4. Beispiel: Automatisierte Runde

- Features werden geplant
- Tasks werden erstellt
- GPT-Agenten erzeugen Code
- QA-Agent testet
- README + API werden aktualisiert

## 💡 Beispiel für Featurebeschreibung

```text
Die App soll es Nutzern ermöglichen, sich zu registrieren und einzuloggen. Nach dem Login sollen sie ihr Profil sehen und bearbeiten können.
```

## 📦 Erweiterungsideen

- Design_Agent erweiter dass er Stable Diffusion nutzt
- Deployment auf Android/iOS/Web
- Support_Agent der issues erzeugen kann
- PR_Agent
- usw.
- Einführung eines "Boss_Agenten" der mithilfe von Templates nach bedarf neue "Agenten" erschaffen und für das Projekt "einstellen" kann

## 📝 Lizenz

MIT License

## 🤖 Autor

Erstellt von Paradoxianer – unterstützt durch GPT-Agenten.
