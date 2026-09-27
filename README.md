# AI Agent

A personal assistant agent powered by Claude. You tell it what you want in plain English and it does the work: it runs terminal commands, reads and writes files, and searches and reads the web.

## Setup

```bash
pip install -r requirements.txt
export ANTHROPIC_API_KEY=sk-ant-...   # get one at https://console.anthropic.com
```

## Use

```bash
python agent.py                                   # chat mode: give it tasks one after another
python agent.py "find the 5 largest files here"   # run one task and exit
python agent.py --yes "..."                       # skip approval prompts (careful!)
```

Some example tasks:
- "Organize the files in ~/Downloads into folders by type"
- "Research the best budget laptops of 2026 and write a comparison to laptops.md"
- "Read report.csv and tell me the top 3 insights"
- "Write a Python script that renames all photos by date, then run it"

## Safety

Before it runs a shell command or writes a file, the agent asks you `Allow? [y/N]`. Reading files and searching the web don't need approval. Only use `--yes` in a folder where mistakes won't hurt.

## Configuration

- `AGENT_MODEL`: the model to use (default `claude-opus-5`)
- If the model declines a request, the agent automatically retries it on a fallback model.

---

## YouTube Video Agent

`youtube_agent/` runs the Health Support Studio YouTube channel. It picks health topics, writes and fact-checks scripts, narrates them with a free AI voice over branded graphics and stock footage, and uploads 1 video a day as private for review. See [youtube_agent/README.md](youtube_agent/README.md) for setup.
