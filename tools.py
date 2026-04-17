"""Tool definitions and handlers for the SAP Basis Consultant AI Agent (Gemini)."""

import json
import subprocess
import sys
from datetime import datetime
from pathlib import Path

from google.genai import types

from config import OUTPUT_DIR

# ---------------------------------------------------------------------------
# Tool definitions — Gemini function declarations
# ---------------------------------------------------------------------------

TOOL_DECLARATIONS = types.Tool(
    function_declarations=[
        types.FunctionDeclaration(
            name="generate_document",
            description=(
                "Generates a structured professional document (SOP, runbook, checklist, "
                "technical guide, report) for SAP Basis topics. Returns full Markdown content "
                "with document header, sections, tables, and revision history. The calling "
                "application converts this to the user's requested format (DOCX, PDF, etc.)."
            ),
            parameters=types.Schema(
                type="OBJECT",
                properties={
                    "title": types.Schema(
                        type="STRING",
                        description="Document title, e.g., 'SAP Kernel Upgrade SOP for S/4HANA'",
                    ),
                    "doc_type": types.Schema(
                        type="STRING",
                        enum=["sop", "runbook", "checklist", "guide", "report", "template", "policy"],
                        description="Type of document to generate",
                    ),
                    "format": types.Schema(
                        type="STRING",
                        enum=["markdown", "docx", "pdf"],
                        description="Target output format",
                    ),
                    "content": types.Schema(
                        type="STRING",
                        description=(
                            "Full Markdown content of the document including headers, "
                            "sections, tables, code blocks, and all details"
                        ),
                    ),
                    "classification": types.Schema(
                        type="STRING",
                        enum=["public", "internal", "confidential"],
                        description="Document classification level",
                    ),
                },
                required=["title", "doc_type", "format", "content"],
            ),
        ),
        types.FunctionDeclaration(
            name="generate_chart",
            description=(
                "Generates a chart, graph, or dashboard visualization for SAP system metrics, "
                "performance trends, or analytical data. Returns both the data table and a fully "
                "self-contained Python script to render the visualization."
            ),
            parameters=types.Schema(
                type="OBJECT",
                properties={
                    "chart_title": types.Schema(
                        type="STRING",
                        description="Title of the chart, e.g., 'SAP System Response Time Trend'",
                    ),
                    "chart_type": types.Schema(
                        type="STRING",
                        enum=[
                            "line", "bar", "stacked_bar", "pie", "heatmap",
                            "scatter", "area", "gauge", "combined",
                        ],
                        description="Type of chart to generate",
                    ),
                    "data_json": types.Schema(
                        type="STRING",
                        description=(
                            'JSON string of the data to plot. Structure: '
                            '{"columns": [...], "rows": [[...], ...]}'
                        ),
                    ),
                    "python_script": types.Schema(
                        type="STRING",
                        description=(
                            "Complete, self-contained Python script using matplotlib or plotly "
                            "that generates the chart and saves it as a PNG or HTML file"
                        ),
                    ),
                    "insights": types.Schema(
                        type="STRING",
                        description="Key insights and actionable recommendations from the data",
                    ),
                    "output_filename": types.Schema(
                        type="STRING",
                        description="Filename for the generated chart, e.g., 'response_time_trend.png'",
                    ),
                },
                required=[
                    "chart_title", "chart_type", "data_json",
                    "python_script", "insights", "output_filename",
                ],
            ),
        ),
        types.FunctionDeclaration(
            name="generate_abap_code",
            description=(
                "Generates ABAP code for SAP Basis administration tasks such as monitoring "
                "reports, automation scripts, data extraction programs, user analysis, or "
                "transport management utilities."
            ),
            parameters=types.Schema(
                type="OBJECT",
                properties={
                    "program_name": types.Schema(
                        type="STRING",
                        description="ABAP program name, e.g., 'Z_BASIS_JOB_RUNTIME_ANALYSIS'",
                    ),
                    "description": types.Schema(
                        type="STRING",
                        description="What the program does and what Basis task it supports",
                    ),
                    "abap_code": types.Schema(
                        type="STRING",
                        description=(
                            "Complete ABAP source code with inline comments, error handling, "
                            "and test/simulation mode"
                        ),
                    ),
                    "target_release": types.Schema(
                        type="STRING",
                        description="Target SAP_BASIS release, e.g., '7.50', '7.56', '7.93'",
                    ),
                    "authorization_objects": types.Schema(
                        type="ARRAY",
                        items=types.Schema(type="STRING"),
                        description="Authorization objects required to run the program",
                    ),
                    "usage_instructions": types.Schema(
                        type="STRING",
                        description="How to deploy, execute, and interpret results",
                    ),
                },
                required=["program_name", "description", "abap_code", "usage_instructions"],
            ),
        ),
        types.FunctionDeclaration(
            name="generate_diagram",
            description=(
                "Generates architecture diagrams, flowcharts, process flows, or system landscape "
                "visualizations for SAP environments using Mermaid diagram syntax."
            ),
            parameters=types.Schema(
                type="OBJECT",
                properties={
                    "diagram_title": types.Schema(
                        type="STRING",
                        description="Title of the diagram",
                    ),
                    "diagram_type": types.Schema(
                        type="STRING",
                        enum=[
                            "flowchart", "sequence", "architecture",
                            "process_flow", "network", "state", "gantt", "er",
                        ],
                        description="Type of diagram to generate",
                    ),
                    "mermaid_code": types.Schema(
                        type="STRING",
                        description="Complete Mermaid diagram code",
                    ),
                    "description": types.Schema(
                        type="STRING",
                        description="Narrative description of what the diagram shows",
                    ),
                },
                required=["diagram_title", "diagram_type", "mermaid_code", "description"],
            ),
        ),
    ]
)


# ---------------------------------------------------------------------------
# Tool handler functions
# ---------------------------------------------------------------------------

def _timestamp() -> str:
    return datetime.now().strftime("%Y%m%d_%H%M%S")


def handle_generate_document(params: dict) -> dict:
    """Save the generated document as a Markdown file in the output directory."""
    title = params.get("title", "Untitled")
    content = params.get("content", "")
    doc_type = params.get("doc_type", "guide")
    classification = params.get("classification", "internal")

    safe_name = "".join(c if c.isalnum() or c in " _-" else "_" for c in title)
    safe_name = safe_name.strip().replace(" ", "_")[:80]
    filename = f"{safe_name}_{_timestamp()}.md"
    filepath = OUTPUT_DIR / filename

    filepath.write_text(content, encoding="utf-8")

    return {
        "status": "success",
        "message": f"Document saved to: {filepath}",
        "file": str(filepath),
        "title": title,
        "doc_type": doc_type,
        "classification": classification,
    }


def handle_generate_chart(params: dict) -> dict:
    """Save the chart script and attempt to execute it to produce the image."""
    chart_title = params.get("chart_title", "chart")
    python_script = params.get("python_script", "")
    output_filename = params.get("output_filename", "chart.png")
    insights = params.get("insights", "")

    script_name = f"chart_{_timestamp()}.py"
    script_path = OUTPUT_DIR / script_name
    patched_script = python_script.replace(
        output_filename, str(OUTPUT_DIR / output_filename).replace("\\", "/")
    )
    script_path.write_text(patched_script, encoding="utf-8")

    chart_file = OUTPUT_DIR / output_filename
    try:
        result = subprocess.run(
            [sys.executable, str(script_path)],
            capture_output=True, text=True, timeout=30,
        )
        if result.returncode == 0:
            return {
                "status": "success",
                "message": f"Chart generated: {chart_file}",
                "script": str(script_path),
                "chart": str(chart_file),
                "insights": insights,
            }
        else:
            return {
                "status": "script_saved",
                "message": (
                    f"Chart script saved to {script_path}. "
                    f"Execution error: {result.stderr[:500]}"
                ),
                "script": str(script_path),
                "insights": insights,
            }
    except Exception as exc:
        return {
            "status": "script_saved",
            "message": f"Chart script saved to {script_path}. Could not auto-run: {exc}",
            "script": str(script_path),
            "insights": insights,
        }


def handle_generate_abap_code(params: dict) -> dict:
    """Save the ABAP code to a file in the output directory."""
    program_name = params.get("program_name", "Z_UNNAMED")
    abap_code = params.get("abap_code", "")
    description = params.get("description", "")
    usage = params.get("usage_instructions", "")
    target_release = params.get("target_release", "")
    auth_objects = params.get("authorization_objects", [])

    filename = f"{program_name}_{_timestamp()}.abap"
    filepath = OUTPUT_DIR / filename

    header = (
        f"*----------------------------------------------------------------------*\n"
        f"* Program  : {program_name}\n"
        f"* Description: {description}\n"
        f"* Target Release: {target_release or 'N/A'}\n"
        f"* Auth Objects: {', '.join(auth_objects) if auth_objects else 'N/A'}\n"
        f"*----------------------------------------------------------------------*\n\n"
    )

    filepath.write_text(header + abap_code, encoding="utf-8")

    usage_file = OUTPUT_DIR / f"{program_name}_{_timestamp()}_USAGE.md"
    usage_file.write_text(
        f"# {program_name}\n\n{description}\n\n## Usage\n\n{usage}\n",
        encoding="utf-8",
    )

    return {
        "status": "success",
        "message": f"ABAP code saved to: {filepath}",
        "file": str(filepath),
        "program_name": program_name,
    }


def handle_generate_diagram(params: dict) -> dict:
    """Save the Mermaid diagram to a file in the output directory."""
    diagram_title = params.get("diagram_title", "Diagram")
    mermaid_code = params.get("mermaid_code", "")
    description = params.get("description", "")

    safe_name = "".join(c if c.isalnum() or c in " _-" else "_" for c in diagram_title)
    safe_name = safe_name.strip().replace(" ", "_")[:80]
    filename = f"{safe_name}_{_timestamp()}.mmd"
    filepath = OUTPUT_DIR / filename

    filepath.write_text(mermaid_code, encoding="utf-8")

    html_filename = f"{safe_name}_{_timestamp()}.html"
    html_path = OUTPUT_DIR / html_filename
    html_content = f"""<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <title>{diagram_title}</title>
    <script src="https://cdn.jsdelivr.net/npm/mermaid/dist/mermaid.min.js"></script>
    <style>
        body {{ font-family: 'Segoe UI', sans-serif; margin: 2rem; background: #f8f9fa; }}
        h1 {{ color: #1a1a2e; }}
        .description {{ color: #555; margin-bottom: 1.5rem; max-width: 800px; }}
        .mermaid {{ background: white; padding: 2rem; border-radius: 8px; box-shadow: 0 2px 8px rgba(0,0,0,0.1); }}
    </style>
</head>
<body>
    <h1>{diagram_title}</h1>
    <p class="description">{description}</p>
    <div class="mermaid">
{mermaid_code}
    </div>
    <script>mermaid.initialize({{startOnLoad: true, theme: 'default'}});</script>
</body>
</html>"""
    html_path.write_text(html_content, encoding="utf-8")

    return {
        "status": "success",
        "message": f"Diagram saved to: {filepath}  |  HTML preview: {html_path}",
        "mermaid_file": str(filepath),
        "html_file": str(html_path),
        "diagram_title": diagram_title,
    }


# ---------------------------------------------------------------------------
# Dispatcher — routes tool calls to the right handler
# ---------------------------------------------------------------------------

HANDLERS = {
    "generate_document": handle_generate_document,
    "generate_chart": handle_generate_chart,
    "generate_abap_code": handle_generate_abap_code,
    "generate_diagram": handle_generate_diagram,
}


def dispatch_tool_call(tool_name: str, tool_input: dict) -> dict:
    """Execute a tool call and return a result dict."""
    handler = HANDLERS.get(tool_name)
    if handler is None:
        return {"error": f"Unknown tool: {tool_name}"}
    try:
        return handler(tool_input)
    except Exception as exc:
        return {"error": str(exc)}
