#!/usr/bin/env python3
"""
SAP Basis Consultant AI Agent — Interactive Chat Application
=============================================================
An AI-powered SAP Basis expert (Rufus) built on the Google Gemini API.

Usage:
    python app.py                  # Interactive terminal chat
    python app.py --web            # Launch Gradio web UI (if installed)

Requires:
    GEMINI_API_KEY set in .env or as an environment variable.
"""

import argparse
import sys

from google import genai
from google.genai import types
from rich.console import Console
from rich.markdown import Markdown
from rich.panel import Panel
from rich.theme import Theme

from config import (
    GEMINI_API_KEY,
    GREETING,
    MAX_TOKENS,
    MODEL,
    SYSTEM_PROMPT_FILE,
)
from tools import TOOL_DECLARATIONS, dispatch_tool_call

# ---------------------------------------------------------------------------
# Console setup
# ---------------------------------------------------------------------------
custom_theme = Theme({
    "info": "cyan",
    "warning": "yellow",
    "error": "bold red",
    "user": "bold green",
    "assistant": "bold blue",
})
console = Console(theme=custom_theme)

# ---------------------------------------------------------------------------
# Load system prompt
# ---------------------------------------------------------------------------
def load_system_prompt() -> str:
    try:
        return SYSTEM_PROMPT_FILE.read_text(encoding="utf-8")
    except FileNotFoundError:
        console.print("[error]system_prompt.txt not found. Using fallback.[/error]")
        return "You are Rufus, an expert SAP Basis Consultant."


# ---------------------------------------------------------------------------
# Core chat engine
# ---------------------------------------------------------------------------
class SAPBasisAgent:
    """Manages conversation state and Gemini API interaction."""

    def __init__(self, api_key: str, model: str, max_tokens: int):
        if not api_key:
            console.print(
                "[error]GEMINI_API_KEY is not set. "
                "Copy .env.example to .env and add your key.[/error]"
            )
            sys.exit(1)

        self.client = genai.Client(api_key=api_key)
        self.model = model
        self.max_tokens = max_tokens
        self.system_prompt = load_system_prompt()
        self.history: list[types.Content] = []
        self.tools = TOOL_DECLARATIONS

    def chat(self, user_message: str) -> str:
        """Send a user message, handle function calls in a loop, return final text."""
        # Add user message to history
        self.history.append(
            types.Content(role="user", parts=[types.Part.from_text(text=user_message)])
        )

        response = self._call_api()

        # Function-calling loop: keep going until the model returns text only
        while self._has_function_calls(response):
            function_call_parts = []
            function_response_parts = []

            for part in response.candidates[0].content.parts:
                if part.function_call:
                    fn_name = part.function_call.name
                    fn_args = dict(part.function_call.args) if part.function_call.args else {}
                    function_call_parts.append(part)

                    console.print(
                        f"  [info]⚙ Calling tool:[/info] {fn_name}",
                        highlight=False,
                    )

                    result = dispatch_tool_call(fn_name, fn_args)

                    # Show brief status
                    status = result.get("status", "")
                    msg = result.get("message", "")
                    if status == "success":
                        console.print(f"    [info]✓ {msg}[/info]", highlight=False)
                    elif msg:
                        console.print(f"    [warning]{msg}[/warning]", highlight=False)

                    function_response_parts.append(
                        types.Part.from_function_response(
                            name=fn_name,
                            response=result,
                        )
                    )

            # Add the model's function call to history
            self.history.append(
                types.Content(
                    role="model",
                    parts=response.candidates[0].content.parts,
                )
            )

            # Add function responses to history
            self.history.append(
                types.Content(role="user", parts=function_response_parts)
            )

            response = self._call_api()

        # Extract final text
        try:
            assistant_text = response.text or ""
        except (AttributeError, ValueError):
            assistant_text = "I'm sorry, I couldn't generate a response. Please try again."

        # Add model response to history
        self.history.append(
            types.Content(
                role="model",
                parts=[types.Part.from_text(text=assistant_text)],
            )
        )

        return assistant_text

    def _has_function_calls(self, response) -> bool:
        """Check if the response contains any function calls."""
        if not response.candidates:
            return False
        content = response.candidates[0].content
        if content is None or not content.parts:
            return False
        for part in content.parts:
            if part.function_call:
                return True
        return False

    def _call_api(self):
        """Make a single API call."""
        try:
            return self.client.models.generate_content(
                model=self.model,
                contents=self.history,
                config=types.GenerateContentConfig(
                    system_instruction=self.system_prompt,
                    tools=[self.tools],
                    max_output_tokens=self.max_tokens,
                    temperature=0.0,
                ),
            )
        except Exception as exc:
            error_msg = str(exc).lower()
            if "api key" in error_msg or "authentication" in error_msg or "401" in error_msg:
                console.print("[error]Invalid API key. Check your .env file.[/error]")
                sys.exit(1)
            elif "429" in error_msg or "quota" in error_msg or "rate" in error_msg:
                console.print("[error]Rate limited. Please wait a moment and try again.[/error]")
                raise
            else:
                console.print(f"[error]API error: {exc}[/error]")
                raise


# ---------------------------------------------------------------------------
# Terminal (CLI) interface
# ---------------------------------------------------------------------------
def run_terminal(agent: SAPBasisAgent) -> None:
    console.print(Panel(GREETING, border_style="blue", expand=False))

    while True:
        try:
            user_input = console.input("[user]You:[/user] ").strip()
        except (EOFError, KeyboardInterrupt):
            console.print("\n[info]Session ended. Goodbye![/info]")
            break

        if not user_input:
            continue
        if user_input.lower() in ("exit", "quit", "bye"):
            console.print("[info]Session ended. Goodbye![/info]")
            break

        console.print()
        with console.status("[info]Rufus is thinking...[/info]", spinner="dots"):
            try:
                reply = agent.chat(user_input)
            except Exception as exc:
                console.print(f"[error]Error: {exc}[/error]")
                continue

        console.print()
        console.print(Markdown(reply))
        console.print()


# ---------------------------------------------------------------------------
# Gradio web interface (optional)
# ---------------------------------------------------------------------------
def run_web(agent: SAPBasisAgent) -> None:
    try:
        import gradio as gr
    except ImportError:
        console.print(
            "[error]Gradio is not installed. Run: pip install gradio[/error]"
        )
        sys.exit(1)

    def respond(message: str, history: list) -> str:
        return agent.chat(message)

    chat_kwargs = dict(
        fn=respond,
        title="SAP Basis Oracle — AI Consultant (Rufus)",
        description=(
            "Ask me anything about SAP Basis: troubleshooting, procedures, "
            "architecture, ABAP code, documents, charts, and more."
        ),
        examples=[
            "Explain the difference between ENSA1 and ENSA2.",
            "Walk me through a kernel upgrade on S/4HANA 2023.",
            "Create a security hardening checklist for SAP NetWeaver 7.50.",
            "Write an ABAP report that analyzes background job runtimes.",
            "Draw a high-availability architecture for S/4HANA on Azure.",
        ],
    )

    # 'theme' kwarg was removed in Gradio 5.x — only pass it if supported
    try:
        demo = gr.ChatInterface(**chat_kwargs, theme=gr.themes.Soft())
    except TypeError:
        demo = gr.ChatInterface(**chat_kwargs)

    demo.launch(share=False)


# ---------------------------------------------------------------------------
# Entry point
# ---------------------------------------------------------------------------
def main() -> None:
    parser = argparse.ArgumentParser(
        description="SAP Basis Consultant AI Agent (Rufus)"
    )
    parser.add_argument(
        "--web", action="store_true",
        help="Launch the Gradio web UI instead of the terminal chat",
    )
    parser.add_argument(
        "--model", type=str, default=None,
        help=f"Override the model (default: {MODEL})",
    )
    args = parser.parse_args()

    model = args.model or MODEL
    agent = SAPBasisAgent(
        api_key=GEMINI_API_KEY,
        model=model,
        max_tokens=MAX_TOKENS,
    )

    if args.web:
        run_web(agent)
    else:
        run_terminal(agent)


if __name__ == "__main__":
    main()
