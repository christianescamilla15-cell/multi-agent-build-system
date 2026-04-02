# Product

Multi-Agent Build System is a Python CLI tool that autonomously builds 5 portfolio projects using a pipeline of 6 specialized AI agents (Architect, Developer, QA Tester, Reviewer, Documenter, Deployer). Each agent calls Claude (Anthropic) to generate architecture designs, source code, test reports, quality reviews, documentation, and deployment configs for a predefined set of AI-powered web projects.

## Target Projects

1. Chatbot Multi-Agente — multi-agent customer support chatbot
2. Content Studio — AI content + image generation platform
3. Finance AI Dashboard — financial analytics with ML predictions
4. HR Scout — CV parsing and candidate scoring system
5. Client Hub — No-Code client portal with Airtable integration

## Key Behaviors

- Supports `--demo` mode that generates mock outputs without an API key
- Each project build produces a `build_result.json` summarizing agent outcomes
- Agents share a `context` dict to pass outputs downstream in the pipeline
