<div align="center">

# 🤖 SAP Basis Oracle
### AI-Powered SAP Basis Consultant

**Rufus** — A domain-specific AI agent built on Google Gemini that acts as a senior SAP Basis Consultant with 25+ years of expertise. Ask questions, get step-by-step procedures, generate professional documents, visualizations, ABAP code, and architecture diagrams — all from a single chat interface.

[![Python](https://img.shields.io/badge/Python-3.10%2B-blue?logo=python&logoColor=white)](https://www.python.org/)
[![Gemini](https://img.shields.io/badge/Google%20Gemini-API-4285F4?logo=google&logoColor=white)](https://aistudio.google.com/)
[![Gradio](https://img.shields.io/badge/Gradio-Web%20UI-orange?logo=gradio&logoColor=white)](https://gradio.app/)
[![License](https://img.shields.io/badge/License-MIT-green)](LICENSE)

[Features](#-features) · [Quick Start](#-quick-start) · [How It Works](#-how-it-works) · [Example Queries](#-example-queries) · [Project Structure](#-project-structure) · [Configuration](#-configuration)

</div>

---

## ✨ Features

| Capability | Description |
|---|---|
| 💬 **Expert Chat** | Multi-turn conversation with full context memory across the session |
| 📄 **Document Generation** | SOPs, runbooks, checklists, guides — saved as Markdown to `output/` |
| 📊 **Chart & Visualization** | Performance trend charts, dashboards via matplotlib/plotly |
| 💻 **ABAP Code Generation** | Monitoring reports, automation scripts, RFC utilities |
| 🏗️ **Architecture Diagrams** | Mermaid-powered flowcharts and landscape diagrams with HTML preview |
| 🖥️ **Dual Interface** | Rich terminal CLI **or** Gradio browser-based web UI |
| ⚙️ **Autonomous Tool Use** | Gemini function calling loop — agent decides when to invoke tools |

---

## 🧠 What Rufus Knows

Rufus covers **13 SAP Basis domains** out of the box:

- **System Administration** — SM51, SM66, SM21, ST22, work processes, kernel architecture
- **Installation & Configuration** — SWPM, ASCS/ERS, Web Dispatcher, Fiori, Solution Manager
- **Transport Management** — TMS, STMS, tp/R3trans, ChaRM, client copies
- **User & Security** — SU01, PFCG, GRC, SSO (SAML/Kerberos), security hardening
- **Database Admin** — SAP HANA, Oracle (BR*Tools), SQL Server, DB2, MaxDB
- **Performance Tuning** — ST03N, ST05, ST02, SQL traces, memory tuning
- **Patching & Upgrades** — Kernel upgrades, SPAM/SAINT, SUM/DMO, S/4HANA conversion
- **Backup & DR** — HSR, Pacemaker/HA clusters, backint, RTO/RPO planning
- **Integration** — RFC, IDocs, PI/PO, SAP Integration Suite, BTP
- **Cloud** — SAP on AWS / Azure / GCP, RISE with SAP, VM sizing
- **S/4HANA** — Conversion assessment, Fiori, CDS views, simplification items
- **ABAP for Basis** — Custom monitoring reports, automation programs
- **Compliance** — License management (LAW/USMM), SAP ILM, audit support

---

## 🚀 Quick Start

### Prerequisites
- Python 3.10+
- A [Google Gemini API key](https://aistudio.google.com/apikey) (free tier available)

### 1. Clone the repository

```bash
git clone https://github.com/your-username/sap-basis-oracle.git
cd sap-basis-oracle
```

### 2. Create a virtual environment & install dependencies

```bash
python -m venv .venv

# Windows
.venv\Scripts\activate

# macOS / Linux
source .venv/bin/activate

pip install -r requirements.txt
```

### 3. Configure your API key

```bash
cp .env.example .env
```

Edit `.env` and add your key:
```env
GEMINI_API_KEY=your_api_key_here
MODEL=gemini-2.5-flash
MAX_TOKENS=8192
```

### 4. Run

```bash
# Terminal chat (default)
python app.py

# Browser-based web UI
pip install gradio
python app.py --web

# Use a specific model
python app.py --model gemini-2.5-pro
```

---

## ⚙️ How It Works

```
┌──────────────┐     ┌────────────────────┐     ┌─────────────────┐
│  User Input   │────▶│   SAPBasisAgent    │────▶│  Google Gemini  │
│ CLI or Gradio │◀────│   (app.py)         │◀────│  (LLM + Tools)  │
└──────────────┘     └────────┬───────────┘     └─────────────────┘
                               │ function calls
                     ┌─────────▼───────────┐
                     │     tools.py         │
                     │  ┌───────────────┐   │
                     │  │ generate_doc  │   │──▶ output/*.md
                     │  │ generate_chart│   │──▶ output/*.png / .html
                     │  │ generate_abap │   │──▶ output/*.abap
                     │  │ generate_diag │   │──▶ output/*.mmd + .html
                     │  └───────────────┘   │
                     └─────────────────────┘
```

### The Function Calling Loop

When you ask Rufus something, here's what happens under the hood:

1. **Your message** is appended to `self.history` and sent to Gemini along with the system prompt and 4 tool schemas
2. **Gemini decides** — either respond with text, or invoke a tool (e.g., `generate_document`)
3. **If a tool is called**, `app.py` dispatches it to the matching handler in `tools.py`, which saves a file to `output/` and returns a result dict
4. **The result** is fed back to Gemini as a function response — it can call more tools or produce a final text reply
5. **Loop continues** until Gemini produces a pure text response, which is rendered as Markdown in your UI

The entire conversation history (including tool calls and results) is maintained in `self.history`, giving Rufus full context across turns.

---

## 💡 Example Queries

```
# Troubleshooting
"I'm getting DBIF_RSQL_SQL_ERROR dumps in ST22 after a HANA revision update"
"SM37 shows my batch job stuck in Active status for 12 hours — how do I diagnose?"

# Procedures
"Walk me through a kernel upgrade on S/4HANA 2023 running on SLES 15"
"How do I configure SAP Web Dispatcher with SSL termination for Fiori?"

# Document Generation
"Create a complete SOP for SPAM/SAINT patching on ECC 6.0 EHP8"
"Generate a disaster recovery runbook for our HANA-based S/4HANA on AWS"

# Charts & Visualization
"Generate a dashboard showing CPU, memory, response time, and job throughput"

# ABAP Code
"Write a report that analyzes background job runtimes over the last 30 days"
"Create an ABAP program to test all RFC destinations and report their status"

# Architecture Diagrams
"Draw an HA architecture for S/4HANA on Azure with HANA System Replication"
"Create a flowchart for the transport request lifecycle from DEV to PRD"
```

---

## 📁 Project Structure

```
sap-basis-oracle/
│
├── app.py               # Main application — agent logic, CLI, and Gradio web UI
├── config.py            # Environment variables, paths, and constants
├── tools.py             # Gemini function declarations + file-writing handlers
├── system_prompt.txt    # Full Rufus persona — edit to change AI behavior
│
├── requirements.txt     # Python dependencies
├── .env.example         # API key configuration template
│
└── output/              # All generated artifacts land here
    ├── *.md             # Generated documents (SOPs, runbooks, checklists)
    ├── *.abap           # Generated ABAP code
    ├── *.mmd            # Mermaid diagram source files
    ├── *.html           # Diagram HTML previews (open in browser)
    ├── *.py             # Chart generation scripts
    └── *.png / *.html   # Rendered charts
```

---

## 🤖 Available Models

| Model | Best For | Speed |
|---|---|---|
| `gemini-2.5-flash` | Fast responses, everyday queries (default) | ⚡⚡⚡ |
| `gemini-2.5-pro` | Complex reasoning, maximum quality | ⚡⚡ |
| `gemini-2.0-flash` | Lightweight, fastest responses | ⚡⚡⚡⚡ |

Override at runtime:
```bash
python app.py --model gemini-2.5-pro
```

---

## 🔧 Configuration

All settings are controlled via the `.env` file:

| Variable | Default | Description |
|---|---|---|
| `GEMINI_API_KEY` | *(required)* | Your Google AI Studio API key |
| `MODEL` | `gemini-2.5-flash` | Gemini model to use |
| `MAX_TOKENS` | `8192` | Maximum output tokens per response |

To customize Rufus's personality, expertise scope, or response style — just edit `system_prompt.txt`. No Python changes needed.

---

## 🛠️ Tech Stack

| Component | Technology |
|---|---|
| LLM | Google Gemini (`google-genai`) |
| Terminal UI | Rich |
| Web UI | Gradio |
| Charts | Matplotlib + Plotly |
| Diagrams | Mermaid.js (HTML preview) |
| Config | python-dotenv |

---

## 📋 Requirements

```
google-genai>=1.0.0
python-dotenv>=1.0.0
matplotlib>=3.8.0
plotly>=5.18.0
rich>=13.7.0
gradio          # optional, for --web mode
```

---

## 🤝 Contributing

Contributions are welcome! Some ideas:

- Add a `web_search` tool to fetch live SAP Notes and KBAs
- RAG integration with your organization's internal SAP documentation
- Export documents to `.docx` / `.pdf` via `python-docx` or `reportlab`
- Add a voice interface using a speech-to-text library

---

## ⚠️ Disclaimer

This agent provides AI-generated SAP Basis guidance. Always validate recommendations in a sandbox/development system before applying them to production. Never apply changes directly to production without proper testing and change management procedures.

---

## 📄 License

MIT License — see [LICENSE](LICENSE) for details.

---

<div align="center">

Built with ❤️ using [Google Gemini](https://aistudio.google.com/) · [Gradio](https://gradio.app/) · [Rich](https://github.com/Textualize/rich)

</div>
