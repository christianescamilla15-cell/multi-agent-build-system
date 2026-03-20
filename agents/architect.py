"""
Agente Arquitecto — Genera la arquitectura del proyecto.
Produce architecture.json con patrón, capas, endpoints y esquema de datos.
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

AGENT_NAME = "Arquitecto"
AGENT_EMOJI = "[ARQ]"


def _build_prompt(project_config: dict) -> str:
    """Construye el prompt para el agente arquitecto."""
    stack_str = "\n".join(
        f"  - {k}: {v}" for k, v in project_config["stack"].items()
    )
    features_str = "\n".join(f"  - {f}" for f in project_config["features"])

    return f"""Eres un arquitecto de software senior. Genera la arquitectura completa para este proyecto.

PROYECTO: {project_config["name"]}
DESCRIPCION: {project_config["description"]}
PUERTO: {project_config["port"]}

STACK TECNOLOGICO:
{stack_str}

FUNCIONALIDADES:
{features_str}

Genera un JSON con esta estructura exacta:
{{
  "project": "{project_config["slug"]}",
  "pattern": "descripcion del patron arquitectonico",
  "layers": [
    {{
      "name": "nombre de la capa",
      "responsibility": "responsabilidad",
      "technologies": ["tech1", "tech2"],
      "directories": ["dir1/", "dir2/"]
    }}
  ],
  "endpoints": [
    {{
      "method": "GET|POST|PUT|DELETE",
      "path": "/api/...",
      "description": "descripcion",
      "auth": true|false
    }}
  ],
  "data_schema": [
    {{
      "entity": "NombreEntidad",
      "fields": [
        {{"name": "campo", "type": "string|number|boolean|date", "required": true|false}}
      ]
    }}
  ],
  "integrations": [
    {{
      "service": "nombre del servicio externo",
      "purpose": "para que se usa",
      "config_keys": ["ENV_VAR_1"]
    }}
  ],
  "directory_structure": {{
    "frontend": ["src/", "src/components/", "src/pages/"],
    "backend": ["server/", "server/routes/"]
  }}
}}

Responde SOLO con el JSON valido, sin markdown ni explicaciones."""


def _generate_mock(project_config: dict) -> dict:
    """Genera salida mock cuando no hay API key disponible."""
    slug = project_config["slug"]

    return {
        "project": slug,
        "pattern": "Clean Architecture con separacion frontend/backend",
        "layers": [
            {
                "name": "Presentacion (Frontend)",
                "responsibility": "UI/UX, interaccion con usuario",
                "technologies": ["React 18", "Vite 5", "TailwindCSS"],
                "directories": ["src/components/", "src/pages/", "src/hooks/"],
            },
            {
                "name": "API Gateway (Backend)",
                "responsibility": "Endpoints REST, autenticacion, validacion",
                "technologies": list(project_config["stack"].values())[1:2],
                "directories": ["server/routes/", "server/middleware/"],
            },
            {
                "name": "Logica de Negocio",
                "responsibility": "Procesamiento, reglas de negocio, integracion IA",
                "technologies": ["Claude API"],
                "directories": ["server/services/", "server/ai/"],
            },
            {
                "name": "Datos",
                "responsibility": "Persistencia, cache, modelos",
                "technologies": ["SQLite"],
                "directories": ["server/models/", "server/db/"],
            },
        ],
        "endpoints": [
            {"method": "GET", "path": "/api/health", "description": "Health check", "auth": False},
            {"method": "POST", "path": "/api/ai/generate", "description": "Generacion con IA", "auth": True},
            {"method": "GET", "path": "/api/data", "description": "Obtener datos", "auth": True},
            {"method": "POST", "path": "/api/data", "description": "Crear registro", "auth": True},
            {"method": "PUT", "path": "/api/data/:id", "description": "Actualizar registro", "auth": True},
            {"method": "DELETE", "path": "/api/data/:id", "description": "Eliminar registro", "auth": True},
        ],
        "data_schema": [
            {
                "entity": "User",
                "fields": [
                    {"name": "id", "type": "number", "required": True},
                    {"name": "email", "type": "string", "required": True},
                    {"name": "name", "type": "string", "required": True},
                    {"name": "created_at", "type": "date", "required": True},
                ],
            },
        ],
        "integrations": [
            {
                "service": "Claude API (Anthropic)",
                "purpose": "Generacion de contenido y analisis con IA",
                "config_keys": ["ANTHROPIC_API_KEY"],
            },
        ],
        "directory_structure": {
            "frontend": ["src/", "src/components/", "src/pages/", "src/hooks/", "src/utils/", "src/styles/"],
            "backend": ["server/", "server/routes/", "server/services/", "server/middleware/", "server/models/", "server/db/"],
        },
    }


def run(project_config: dict, context: dict = None) -> dict:
    """
    Ejecuta el agente arquitecto.

    Args:
        project_config: Configuracion del proyecto desde config.py
        context: Contexto compartido entre agentes (no usado por arquitecto)

    Returns:
        dict con la arquitectura generada y metadatos
    """
    if context is None:
        context = {}

    start_time = time.time()
    slug = project_config["slug"]
    print(f"\n{CYAN}{BOLD}{AGENT_EMOJI} Agente Arquitecto{RESET} - Disenando arquitectura de {slug}...")

    result = {
        "agent": "architect",
        "project": slug,
        "status": "pending",
        "output": None,
        "error": None,
        "duration": 0,
    }

    try:
        client = context.get("client")
        demo_mode = context.get("demo_mode", False)

        if demo_mode or client is None:
            print(f"  {YELLOW}[DEMO]{RESET} Generando arquitectura mock...")
            architecture = _generate_mock(project_config)
        else:
            from config import MODEL, MAX_TOKENS

            print(f"  {CYAN}[API]{RESET} Consultando {MODEL}...")
            prompt = _build_prompt(project_config)

            response = client.messages.create(
                model=MODEL,
                max_tokens=MAX_TOKENS,
                messages=[{"role": "user", "content": prompt}],
            )

            raw = response.content[0].text.strip()
            if raw.startswith("```"):
                raw = raw.split("\n", 1)[1]
                if raw.endswith("```"):
                    raw = raw[: raw.rfind("```")]
            architecture = json.loads(raw)

        # Guardar archivo de salida
        output_dir = context.get("output_dir", f"output/{slug}")
        os.makedirs(output_dir, exist_ok=True)
        output_path = os.path.join(output_dir, "architecture.json")
        with open(output_path, "w", encoding="utf-8") as f:
            json.dump(architecture, f, indent=2, ensure_ascii=False)

        result["status"] = "success"
        result["output"] = architecture
        result["output_file"] = output_path

        elapsed = time.time() - start_time
        result["duration"] = round(elapsed, 2)
        print(f"  {GREEN}[OK]{RESET} Arquitectura generada en {elapsed:.1f}s -> {output_path}")

    except json.JSONDecodeError as e:
        result["status"] = "error"
        result["error"] = f"Error parseando JSON de respuesta: {e}"
        result["duration"] = round(time.time() - start_time, 2)
        print(f"  {RED}[ERROR]{RESET} JSON invalido: {e}")

    except Exception as e:
        result["status"] = "error"
        result["error"] = str(e)
        result["duration"] = round(time.time() - start_time, 2)
        print(f"  {RED}[ERROR]{RESET} {e}")

    return result
