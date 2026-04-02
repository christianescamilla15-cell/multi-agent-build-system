|# Project Structure

```
multi-agent-system/
├── orchestrator.py        # CLI entry point; runs the 6-agent pipeline
├── config.py              # PROJECTS list, MODEL, MAX_TOKENS, OUTPUT_DIR
├── requirements.txt
├── .env.example
├── agents/
│   ├── __init__.py
│   ├── architect.py       # Generates architecture.json
│   ├── developer.py       # Generates source code files
│   ├── qa_tester.py       # Generates qa_report.json
│   ├── reviewer.py        # Generates review.json (score + grade)
│   ├── documenter.py      # Generates README.md, API.md, DEPLOYMENT.md
│   └── deployer.py        # Generates docker-compose.yml, deploy.sh
├── utils/
│   ├── __init__.py
│   ├── claude_api.py      # Shared Claude client + call_claude() helper
│   ├── logger.py          # AgentLogger class with colored terminal output
│   └── dashboard.py       # Real-time terminal dashboard
└── web-demo/              # Standalone React/Vite demo app (separate concern)
```

## Agent Contract

Every agent module must expose a `run(project_config, context) -> dict` function returning:

```python
{
    "agent": str,       # agent key (e.g. "architect")
    "project": str,     # project slug
    "status": str,      # "success" | "error" | "skipped"
    "output": dict,     # parsed output (passed to next agents via context)
    "error": str|None,
    "duration": float,  # seconds
}
```

## Context Dict (shared between agents)

| Key              | Set by        | Used by                        |
|------------------|---------------|--------------------------------|
| `client`         | orchestrator  | all agents                     |
| `demo_mode`      | orchestrator  | all agents                     |
| `output_dir`     | orchestrator  | all agents                     |
| `architecture`   | architect     | developer, qa_tester, reviewer |
| `code_manifest`  | developer     | qa_tester, reviewer, documenter|
| `qa_report`      | qa_tester     | reviewer, documenter           |
| `review`         | reviewer      | documenter, deployer           |
| `docs`           | documenter    | deployer                       |

## Output Directory

Builds write to `output/{project-slug}/` — this directory is gitignored and created at runtime.

## Conventions

- All prompts instruct Claude to respond with raw JSON only (no markdown fences)
- Each agent strips markdown fences defensively before `json.loads()`
- Demo/mock mode is triggered when `context["demo_mode"] is True` or `client is None`
- Terminal colors are defined as module-level ANSI constants in each file (not imported from utils)
- `AgentLogger` in `utils/logger.py` is the preferred logger for new agents
