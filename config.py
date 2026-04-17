"""Configuration for the SAP Basis Consultant AI Agent."""

import os
from pathlib import Path
from dotenv import load_dotenv

load_dotenv()

# Paths
BASE_DIR = Path(__file__).parent
SYSTEM_PROMPT_FILE = BASE_DIR / "system_prompt.txt"
OUTPUT_DIR = BASE_DIR / "output"
OUTPUT_DIR.mkdir(exist_ok=True)

# API settings
GEMINI_API_KEY = os.getenv("GEMINI_API_KEY", "")
MODEL = os.getenv("MODEL", "gemini-2.5-flash")
MAX_TOKENS = int(os.getenv("MAX_TOKENS", "8192"))

# Greeting message shown at session start
GREETING = """
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
  SAP Basis Oracle  —  AI-Powered SAP Basis Consultant (Rufus)
  Powered by Google Gemini
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

  I can help you with:
    • Troubleshooting  — ST22, SM21, SM37 errors and more
    • Procedures       — Kernel upgrades, patching, system copies
    • Documents        — SOPs, runbooks, checklists
    • Visualizations   — Performance charts and dashboards
    • ABAP Code        — Monitoring reports and automation
    • Architecture     — Landscape diagrams and flowcharts
    • Security         — User admin, roles, SSO, hardening
    • Cloud            — SAP on AWS / Azure / GCP / RISE

  Tip: Tell me your SAP version, DB, and OS for tailored answers.
  Type 'exit' or 'quit' to end the session.
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
"""
