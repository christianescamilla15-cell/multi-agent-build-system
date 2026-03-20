"""
Agente Deployer — Genera configuracion de despliegue.
Produce docker-compose.yml, deploy.sh y .env.example.
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

AGENT_NAME = "Deployer"
AGENT_EMOJI = "[DPL]"


def _build_prompt(project_config, architecture, code_manifest):
    """Construye el prompt para el agente deployer."""
    stack_str = "\n".join(f"  - {k}: {v}" for k, v in project_config["stack"].items())
    slug = project_config["slug"]
    name = project_config["name"]
    port = project_config["port"]
    bp = port + 1000

    return f"""Eres un DevOps senior. Genera la configuracion de despliegue completa.

PROYECTO: {name}
SLUG: {slug}
PUERTO FRONTEND: {port}
PUERTO BACKEND: {bp}
STACK: {stack_str}

Genera un JSON con:
{{
  "docker_compose": "contenido docker-compose.yml",
  "deploy_script": "contenido deploy.sh",
  "env_example": "contenido .env.example",
  "dockerfile_frontend": "Dockerfile frontend",
  "dockerfile_backend": "Dockerfile backend",
  "nginx_conf": "configuracion nginx"
}}

Responde SOLO con JSON valido."""


def _generate_mock(project_config):
    """Genera configuracion de deploy mock para modo demo."""
    slug = project_config["slug"]
    name = project_config["name"]
    port = project_config["port"]
    bp = port + 1000

    backend_stack = project_config["stack"].get("backend", "")
    is_python = "Python" in backend_stack or "FastAPI" in backend_stack

    docker_compose = f"""version: "3.8"

services:
  frontend:
    build:
      context: .
      dockerfile: Dockerfile.frontend
    ports:
      - "{port}:{port}"
    environment:
      - VITE_API_URL=http://backend:{bp}
    depends_on:
      backend:
        condition: service_healthy
    restart: unless-stopped
    networks:
      - {slug}-net

  backend:
    build:
      context: ./server
      dockerfile: Dockerfile
    ports:
      - "{bp}:{bp}"
    env_file:
      - .env
    volumes:
      - ./data:/app/data
    healthcheck:
      test: ["CMD", "curl", "-f", "http://localhost:{bp}/api/health"]
      interval: 30s
      timeout: 10s
      retries: 3
    restart: unless-stopped
    networks:
      - {slug}-net

  nginx:
    image: nginx:alpine
    ports:
      - "80:80"
      - "443:443"
    volumes:
      - ./nginx.conf:/etc/nginx/conf.d/default.conf
    depends_on:
      - frontend
      - backend
    restart: unless-stopped
    networks:
      - {slug}-net

networks:
  {slug}-net:
    driver: bridge
"""

    if is_python:
        dockerfile_backend = f"""FROM python:3.12-slim
WORKDIR /app
RUN apt-get update && apt-get install -y --no-install-recommends curl && rm -rf /var/lib/apt/lists/*
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt
COPY . .
HEALTHCHECK --interval=30s --timeout=10s CMD curl -f http://localhost:{bp}/api/health || exit 1
EXPOSE {bp}
CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "{bp}"]
"""
    else:
        dockerfile_backend = f"""FROM node:20-alpine
WORKDIR /app
COPY package*.json ./
RUN npm ci --only=production
COPY . .
HEALTHCHECK --interval=30s --timeout=10s CMD wget -q --spider http://localhost:{bp}/api/health || exit 1
EXPOSE {bp}
CMD ["node", "index.js"]
"""

    dockerfile_frontend = f"""FROM node:20-alpine AS builder
WORKDIR /app
COPY package*.json ./
RUN npm ci
COPY . .
RUN npm run build

FROM nginx:alpine
COPY --from=builder /app/dist /usr/share/nginx/html
EXPOSE {port}
CMD ["nginx", "-g", "daemon off;"]
"""

    deploy_script = f"""#!/usr/bin/env bash
set -euo pipefail

RED='\\033[0;31m'; GREEN='\\033[0;32m'; YELLOW='\\033[1;33m'; CYAN='\\033[0;36m'; NC='\\033[0m'
PROJECT="{slug}"

log_info()  {{ echo -e "${{CYAN}}[INFO]${{NC}}  $1"; }}
log_ok()    {{ echo -e "${{GREEN}}[OK]${{NC}}    $1"; }}
log_warn()  {{ echo -e "${{YELLOW}}[WARN]${{NC}}  $1"; }}
log_error() {{ echo -e "${{RED}}[ERROR]${{NC}} $1"; }}

show_help() {{
    echo "Uso: ./deploy.sh [COMANDO]"
    echo "  up        Iniciar servicios"
    echo "  down      Detener servicios"
    echo "  restart   Reiniciar"
    echo "  logs      Ver logs"
    echo "  status    Estado de servicios"
    echo "  build     Reconstruir imagenes"
    echo "  help      Esta ayuda"
}}

check_requirements() {{
    log_info "Verificando requisitos..."
    command -v docker &>/dev/null || {{ log_error "Docker no instalado"; exit 1; }}
    [ -f ".env" ] || {{ log_warn ".env no encontrado"; cp .env.example .env 2>/dev/null; log_warn "Edita .env"; exit 1; }}
    log_ok "Requisitos OK"
}}

cmd_up() {{
    check_requirements
    log_info "Iniciando $PROJECT..."
    docker compose up -d --build
    log_ok "$PROJECT iniciado"
    log_info "Frontend: http://localhost:{port}"
    log_info "Backend:  http://localhost:{bp}"
}}

cmd_down() {{ log_info "Deteniendo..."; docker compose down; log_ok "Detenido"; }}
cmd_logs() {{ docker compose logs -f; }}
cmd_status() {{ docker compose ps; }}
cmd_build() {{ docker compose build --no-cache; }}

case "${{1:-help}}" in
    up) cmd_up;; down) cmd_down;; restart) cmd_down; cmd_up;;
    logs) cmd_logs;; status) cmd_status;; build) cmd_build;; *) show_help;;
esac
"""

    env_example = f"""# {name} - Variables de Entorno
ANTHROPIC_API_KEY=sk-ant-...
PORT={bp}
FRONTEND_PORT={port}
DATABASE_URL=sqlite:///data/{slug}.db
NODE_ENV=production
LOG_LEVEL=info
CORS_ORIGIN=http://localhost:{port}
RATE_LIMIT_WINDOW_MS=60000
RATE_LIMIT_MAX_REQUESTS=60
RATE_LIMIT_AI_MAX_REQUESTS=10
"""

    nginx_conf = f"""server {{
    listen 80;
    server_name _;

    location / {{
        proxy_pass http://frontend:{port};
        proxy_http_version 1.1;
        proxy_set_header Upgrade $http_upgrade;
        proxy_set_header Connection 'upgrade';
        proxy_set_header Host $host;
    }}

    location /api {{
        proxy_pass http://backend:{bp};
        proxy_http_version 1.1;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header Host $host;
        proxy_read_timeout 120s;
    }}
}}
"""

    return {
        "docker_compose": docker_compose,
        "deploy_script": deploy_script,
        "env_example": env_example,
        "dockerfile_frontend": dockerfile_frontend,
        "dockerfile_backend": dockerfile_backend,
        "nginx_conf": nginx_conf,
    }


def run(project_config, context=None):
    """Ejecuta el agente deployer."""
    if context is None:
        context = {}

    start_time = time.time()
    slug = project_config["slug"]
    print(f"\n{CYAN}{BOLD}{AGENT_EMOJI} Agente Deployer{RESET} - Generando config deploy de {slug}...")

    result = {
        "agent": "deployer", "project": slug,
        "status": "pending", "output": None, "error": None, "duration": 0,
    }

    try:
        client = context.get("client")
        demo_mode = context.get("demo_mode", False)
        architecture = context.get("architecture", {})
        code_manifest = context.get("code_manifest", {})

        if demo_mode or client is None:
            print(f"  {YELLOW}[DEMO]{RESET} Generando config deploy mock...")
            deploy_config = _generate_mock(project_config)
        else:
            from config import MODEL, MAX_TOKENS
            print(f"  {CYAN}[API]{RESET} Consultando {MODEL}...")
            prompt = _build_prompt(project_config, architecture, code_manifest)
            response = client.messages.create(
                model=MODEL, max_tokens=MAX_TOKENS,
                messages=[{"role": "user", "content": prompt}],
            )
            raw = response.content[0].text.strip()
            if raw.startswith("```"):
                raw = raw.split("\n", 1)[1]
                if raw.endswith("```"):
                    raw = raw[: raw.rfind("```")]
            deploy_config = json.loads(raw)

        output_dir = context.get("output_dir", f"output/{slug}")
        deploy_dir = os.path.join(output_dir, "deploy")
        os.makedirs(deploy_dir, exist_ok=True)

        file_mapping = {
            "docker-compose.yml": "docker_compose",
            "deploy.sh": "deploy_script",
            ".env.example": "env_example",
            "Dockerfile.frontend": "dockerfile_frontend",
            "Dockerfile.backend": "dockerfile_backend",
            "nginx.conf": "nginx_conf",
        }

        files_written = []
        for filename, key in file_mapping.items():
            content = deploy_config.get(key, "")
            if content:
                filepath = os.path.join(deploy_dir, filename)
                with open(filepath, "w", encoding="utf-8") as f:
                    f.write(content)
                files_written.append(filename)
                if filename == "deploy.sh":
                    try:
                        os.chmod(filepath, 0o755)
                    except OSError:
                        pass

        result["status"] = "success"
        result["output"] = deploy_config
        result["output_dir"] = deploy_dir
        result["files_written"] = files_written

        elapsed = time.time() - start_time
        result["duration"] = round(elapsed, 2)
        joined = ", ".join(files_written)
        print(f"  {GREEN}[OK]{RESET} Deploy config en {elapsed:.1f}s: {joined}")
        print(f"       -> {deploy_dir}/")

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
