#!/usr/bin/env python3
"""A general-purpose AI assistant agent powered by Claude.

It chats with you in the terminal and can take actions on your behalf:
run shell commands, read/write files, and search/fetch the web.
Anything that changes your system asks for your approval first
(unless you start it with --yes).

Usage:
    export ANTHROPIC_API_KEY=sk-ant-...
    python agent.py                 # interactive chat
    python agent.py "summarize every .md file in this folder"   # one task
"""

import argparse
import json
import os
import subprocess
import sys
from pathlib import Path

import anthropic

MODEL = os.environ.get("AGENT_MODEL", "claude-opus-5")
MAX_TOOL_OUTPUT = 20_000
MAX_STEPS = 50

SYSTEM_PROMPT = f"""You are a capable personal assistant agent working for the user on their computer.
Current working directory: {os.getcwd()}

You can run shell commands, read and write files, and search or fetch the web.
Work autonomously toward the user's goal: plan briefly, act with tools, check the
results, and keep going until the task is done. Then give a short summary of what
you did and anything the user must do themselves (e.g. things that need their
login, payment, or a personal decision).

Never guess at facts you can check. Do not do anything destructive or irreversible
(deleting data, sending messages, spending money) unless the user clearly asked for it."""

TOOLS = [
    {
        "name": "run_shell",
        "description": "Run a shell command and return its stdout, stderr and exit code. "
        "Use for anything a terminal can do: inspecting files, running scripts, git, installing packages.",
        "input_schema": {
            "type": "object",
            "properties": {
                "command": {"type": "string", "description": "The shell command to run."},
                "timeout": {"type": "integer", "description": "Seconds before the command is killed (default 120)."},
            },
            "required": ["command"],
            "additionalProperties": False,
        },
    },
    {
        "name": "read_file",
        "description": "Read a text file and return its contents.",
        "input_schema": {
            "type": "object",
            "properties": {"path": {"type": "string", "description": "Path to the file."}},
            "required": ["path"],
            "additionalProperties": False,
        },
    },
    {
        "name": "write_file",
        "description": "Create or overwrite a text file with the given content. Parent folders are created as needed.",
        "input_schema": {
            "type": "object",
            "properties": {
                "path": {"type": "string", "description": "Path to the file."},
                "content": {"type": "string", "description": "Full file content to write."},
            },
            "required": ["path", "content"],
            "additionalProperties": False,
        },
    },
    {
        "name": "list_dir",
        "description": "List the entries of a directory (folders end with '/').",
        "input_schema": {
            "type": "object",
            "properties": {"path": {"type": "string", "description": "Directory path (default '.')."}},
            "additionalProperties": False,
        },
    },
    # Server-side tools: run on Anthropic's servers, no local code needed.
    {"type": "web_search_20260209", "name": "web_search", "max_uses": 10},
    {"type": "web_fetch_20260209", "name": "web_fetch", "max_uses": 10},
]

# Tools that change the system and need the user's OK first.
NEEDS_APPROVAL = {"run_shell", "write_file"}


def truncate(text: str) -> str:
    if len(text) <= MAX_TOOL_OUTPUT:
        return text
    return text[:MAX_TOOL_OUTPUT] + f"\n... [truncated {len(text) - MAX_TOOL_OUTPUT} chars]"


def run_shell(command: str, timeout: int = 120) -> str:
    try:
        proc = subprocess.run(command, shell=True, capture_output=True, text=True, timeout=timeout)
    except subprocess.TimeoutExpired:
        return f"Command timed out after {timeout}s"
    return truncate(f"exit code: {proc.returncode}\nstdout:\n{proc.stdout}\nstderr:\n{proc.stderr}")


def read_file(path: str) -> str:
    return truncate(Path(path).expanduser().read_text(errors="replace"))


def write_file(path: str, content: str) -> str:
    p = Path(path).expanduser()
    p.parent.mkdir(parents=True, exist_ok=True)
    p.write_text(content)
    return f"Wrote {len(content)} characters to {p}"


def list_dir(path: str = ".") -> str:
    p = Path(path).expanduser()
    entries = sorted(e.name + ("/" if e.is_dir() else "") for e in p.iterdir())
    return truncate("\n".join(entries) or "(empty)")


HANDLERS = {"run_shell": run_shell, "read_file": read_file, "write_file": write_file, "list_dir": list_dir}


def approve(name: str, args: dict, auto_yes: bool) -> bool:
    if auto_yes or name not in NEEDS_APPROVAL:
        return True
    if name == "run_shell":
        preview = f"$ {args.get('command')}"
    else:
        preview = f"write {args.get('path')} ({len(args.get('content', ''))} chars)"
    answer = input(f"\n\033[33mAgent wants to: {preview}\nAllow? [y/N] \033[0m").strip().lower()
    return answer in ("y", "yes")


def execute_tool(block, auto_yes: bool) -> dict:
    args = block.input if isinstance(block.input, dict) else json.loads(block.input)
    result = {"type": "tool_result", "tool_use_id": block.id}
    if not approve(block.name, args, auto_yes):
        return {**result, "content": "The user declined this action.", "is_error": True}
    try:
        output = HANDLERS[block.name](**args)
        print(f"\033[2m[{block.name}] done\033[0m")
        return {**result, "content": output}
    except Exception as e:  # report tool failures back to Claude instead of crashing
        return {**result, "content": f"{type(e).__name__}: {e}", "is_error": True}


def run_turn(client: anthropic.Anthropic, messages: list, auto_yes: bool) -> None:
    """Let Claude work on the latest user message until it has nothing left to do."""
    for _ in range(MAX_STEPS):
        response = client.beta.messages.create(
            model=MODEL,
            max_tokens=16000,
            system=SYSTEM_PROMPT,
            tools=TOOLS,
            messages=messages,
            thinking={"type": "adaptive"},
            betas=["server-side-fallback-2026-07-01"],
            fallbacks="default",
        )
        messages.append({"role": "assistant", "content": response.content})

        for block in response.content:
            if block.type == "text" and block.text.strip():
                print(f"\n\033[36mAgent:\033[0m {block.text}")
            elif block.type == "server_tool_use":
                print(f"\033[2m[{block.name}] {json.dumps(block.input)[:120]}\033[0m")

        if response.stop_reason == "refusal":
            print("\n[The request was declined by the model.]")
            return
        if response.stop_reason == "max_tokens":
            print("\n[Response hit the token limit.]")
            return
        if response.stop_reason == "pause_turn":
            continue  # long server-tool turn: send the history back to resume it
        if response.stop_reason != "tool_use":
            return

        tool_results = [execute_tool(b, auto_yes) for b in response.content if b.type == "tool_use"]
        messages.append({"role": "user", "content": tool_results})

    print(f"\n[Stopped after {MAX_STEPS} steps. Say 'continue' to keep going.]")


def main() -> None:
    parser = argparse.ArgumentParser(description="Claude-powered personal assistant agent")
    parser.add_argument("task", nargs="*", help="Run a single task and exit")
    parser.add_argument("--yes", action="store_true", help="Auto-approve shell commands and file writes")
    args = parser.parse_args()

    client = anthropic.Anthropic()
    messages: list = []

    if args.task:
        messages.append({"role": "user", "content": " ".join(args.task)})
        run_turn(client, messages, args.yes)
        return

    print(f"AI agent ready ({MODEL}). Tell me what to do. Type 'exit' to quit.")
    while True:
        try:
            user_input = input("\n\033[32mYou:\033[0m ").strip()
        except (EOFError, KeyboardInterrupt):
            print()
            break
        if user_input.lower() in ("exit", "quit"):
            break
        if not user_input:
            continue
        messages.append({"role": "user", "content": user_input})
        try:
            run_turn(client, messages, args.yes)
        except anthropic.AuthenticationError:
            sys.exit("Invalid or missing API key. Set ANTHROPIC_API_KEY.")
        except anthropic.RateLimitError:
            print("\n[Rate limited - wait a moment and try again.]")
        except anthropic.APIStatusError as e:
            print(f"\n[API error {e.status_code}: {e.message}]")
        except anthropic.APIConnectionError:
            print("\n[Could not reach the API - check your connection.]")


if __name__ == "__main__":
    main()
