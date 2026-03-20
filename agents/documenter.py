"""
Agente Documentador — Genera documentacion completa del proyecto.
Produce README.md, API.md y DEPLOYMENT.md.
"""

import json
import os
import time

# Colores para terminal
CYAN = "\033[96m"
GREEN = "\033[92m"
YELLOW = "\033[93m"
RED = "\033[91m"
RESET = "\033[0m"
BOLD = "\033[1m"

AGENT_NAME = "Documentador"
AGENT_EMOJI = "[DOC]"


def _build_prompt(project_config, architecture, code_manifest, review):
    """Construye el prompt para el agente documentador."""
    stack_str = "\n".join(f"  - {k}: {v}" for k, v in project_config["stack"].items())
    features_str = "\n".join(f"  - {f}" for f in project_config["features"])
    endpoints = architecture.get("endpoints", [])
    endpoints_str = "\n".join(f"  - {e['method']} {e['path']}: {e['description']}" for e in endpoints)
    setup = code_manifest.get("setup_instructions", [])
    setup_str = "\n".join(f"  {i+1}. {s}" for i, s in enumerate(setup))
    name = project_config["name"]
    slug = project_config["slug"]
    desc = project_config["description"]
    port = project_config["port"]
    score = review.get("final_score", "N/A")

    return f"""Eres un technical writer senior. Genera documentacion completa para este proyecto.

PROYECTO: {name}
DESCRIPCION: {desc}
PUERTO: {port}
STACK: {stack_str}
FEATURES: {features_str}
ENDPOINTS: {endpoints_str}
SETUP: {setup_str}
SCORE REVIEW: {score}/100

Genera un JSON con 3 documentos Markdown:
{{
  "readme": "contenido README.md",
  "api_docs": "contenido API.md",
  "deployment": "contenido DEPLOYMENT.md"
}}

Cada documento profesional, completo, en espanol. Responde SOLO con JSON valido."""


def _generate_mock(project_config, architecture, code_manifest):
    """Genera documentacion mock para modo demo."""
    slug = project_config["slug"]
    name = project_config["name"]
    port = project_config["port"]
    desc = project_config["description"]

    stack_items = "\n".join(f"- **{k}**: {v}" for k, v in project_config["stack"].items())
    features_items = "\n".join(f"- {f}" for f in project_config["features"])

    setup_steps = code_manifest.get("setup_instructions", ["npm install", "Copiar .env.example a .env", "npm run dev"])
    setup_md = "\n".join(f"{i+1}. {s}" for i, s in enumerate(setup_steps))

    readme = f"""# {name}

> {desc}

## Funcionalidades

{features_items}

## Stack Tecnologico

{stack_items}

## Requisitos Previos

- Node.js >= 18.0
- npm >= 9.0
- API Key de Anthropic (Claude)

## Instalacion

```bash
git clone <repo-url>
cd {slug}
npm install
cd server && npm install
cd ..
cp .env.example .env
```

## Uso

```bash
npm run dev          # Frontend en http://localhost:{port}
cd server && npm run dev  # Backend en http://localhost:{port + 1000}
```

## Estructura del Proyecto

```
{slug}/
  src/                  # Frontend React
    components/         # Componentes reutilizables
    pages/              # Paginas/vistas
    hooks/              # Custom hooks
    App.jsx             # Componente raiz
    main.jsx            # Entry point
  server/               # Backend
    routes/             # Rutas API
    services/           # Logica de negocio
    middleware/          # Middleware
    index.js            # Entry point backend
  .env.example          # Variables de entorno
  package.json          # Dependencias frontend
  vite.config.js        # Configuracion Vite
```

## Variables de Entorno

| Variable | Descripcion | Requerida |
|----------|-------------|-----------|
| `ANTHROPIC_API_KEY` | API Key de Claude | Si |
| `PORT` | Puerto del frontend | No (default: {port}) |

## Licencia

MIT License - Christian Hernandez
"""

    api_docs = f"""# API Documentation - {name}

Base URL: `http://localhost:{port + 1000}/api`

## Endpoints

### `GET /api/health`

Health check del servicio.

**Response:** `{{"status": "ok", "service": "{slug}"}}`

### `POST /api/ai/generate` [Auth Required]

Genera contenido usando IA.

**Request:**
```json
{{"prompt": "Tu prompt aqui", "options": {{}}}}
```

**Response:**
```json
{{"result": "Contenido generado", "usage": {{"input_tokens": 50, "output_tokens": 200}}}}
```

## Codigos de Error

| Codigo | Descripcion |
|--------|-------------|
| 200 | Exito |
| 400 | Request invalido |
| 401 | No autenticado |
| 429 | Rate limit |
| 500 | Error del servidor |
"""

    deployment = f"""# Guia de Despliegue - {name}

## Opcion 1: Docker

```bash
docker-compose up -d --build
```

Frontend: http://localhost:{port}
Backend: http://localhost:{port + 1000}

## Opcion 2: VPS (Ubuntu)

```bash
sudo apt update && sudo apt install -y nodejs npm nginx
git clone <repo> /var/www/{slug}
cd /var/www/{slug}
npm install && npm run build
cd server && npm install
npm install -g pm2
pm2 start server/index.js --name {slug}-api
```

## Variables de Entorno en Produccion

```env
NODE_ENV=production
ANTHROPIC_API_KEY=sk-ant-...
PORT={port + 1000}
```
"""

    return {"readme": readme, "api_docs": api_docs, "deployment": deployment}


def run(project_config, context=None):
    """Ejecuta el agente documentador."""
    if context is None:
        context = {}

    start_time = time.time()
    slug = project_config["slug"]
    print(f"\n{CYAN}{BOLD}{AGENT_EMOJI} Agente Documentador{RESET} - Generando documentacion de {slug}...")

    result = {
        "agent": "documenter", "project": slug,
        "status": "pending", "output": None, "error": None, "duration": 0,
    }

    try:
        client = context.get("client")
        demo_mode = context.get("demo_mode", False)
        architecture = context.get("architecture", {})
        code_manifest = context.get("code_manifest", {})
        review = context.get("review", {})

        if demo_mode or client is None:
            print(f"  {YELLOW}[DEMO]{RESET} Generando documentacion mock...")
            docs = _generate_mock(project_config, architecture, code_manifest)
        else:
            from config import MODEL, MAX_TOKENS
            print(f"  {CYAN}[API]{RESET} Consultando {MODEL}...")
            prompt = _build_prompt(project_config, architecture, code_manifest, review)
            response = client.messages.create(
                model=MODEL, max_tokens=MAX_TOKENS,
                messages=[{"role": "user", "content": prompt}],
            )
            raw = response.content[0].text.strip()
            if raw.startswith("```"):
                raw = raw.split("\n", 1)[1]
                if raw.endswith("```"):
                    raw = raw[: raw.rfind("```")]
            docs = json.loads(raw)

        output_dir = context.get("output_dir", f"output/{slug}")
        docs_dir = os.path.join(output_dir, "docs")
        os.makedirs(docs_dir, exist_ok=True)

        files_written = []
        for filename, key in [("README.md", "readme"), ("API.md", "api_docs"), ("DEPLOYMENT.md", "deployment")]:
            content = docs.get(key, "")
            if content:
                with open(os.path.join(docs_dir, filename), "w", encoding="utf-8") as f:
                    f.write(content)
                files_written.append(filename)

        result["status"] = "success"
        result["output"] = docs
        result["output_dir"] = docs_dir
        result["files_written"] = files_written

        elapsed = time.time() - start_time
        result["duration"] = round(elapsed, 2)
        joined = ", ".join(files_written)
        print(f"  {GREEN}[OK]{RESET} Documentacion en {elapsed:.1f}s: {joined}")
        print(f"       -> {docs_dir}/")

    except json.JSONDecodeError as e:
        result["status"] = "error"
        result["error"] = f"Error parseando JSON: {e}"
        result["duration"] = round(time.time() - start_time, 2)
        print(f"  {RED}[ERROR]{RESET} JSON invalido: {e}")
    except Exception as e:
        result["status"] = "error"
        result["error"] = str(e)
        result["duration"] = round(time.time() - start_time, 2)
        print(f"  {RED}[ERROR]{RESET} {e}")

    return result
