import os
from datetime import datetime

LOG_PATH = "logs/gpt/gpt_log.txt"

def log_gpt_interaction(agent_name, prompt, response):
    os.makedirs("logs/gpt", exist_ok=True)
    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    with open(LOG_PATH, "a", encoding="utf-8") as f:
        f.write("=" * 80 + "\n")
        f.write(f"[{timestamp}] Agent: {agent_name}\n")
        f.write(">>> PROMPT:\n")
        f.write(prompt.strip() + "\n\n")
        f.write(">>> RESPONSE:\n")
        f.write(response.strip() + "\n\n")

