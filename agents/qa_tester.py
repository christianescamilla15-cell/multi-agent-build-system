"""
Agente QA Tester - Evalua estructura, seguridad y rendimiento.
Produce qa_report.json con analisis detallado y recomendaciones.
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

AGENT_NAME = "QA Tester"
AGENT_EMOJI = "[QA]"


def _build_prompt(project_config, architecture, code_manifest):
    """Construye el prompt para el agente QA."""
    files_summary = []
    for f in code_manifest.get("files", [])[:15]:
        files_summary.append(f"  - {f['path']}: {f.get('description', 'sin descripcion')}")
    files_str = "\n".join(files_summary)
    name = project_config["name"]
    slug = project_config["slug"]
    desc = project_config["description"]
    pattern = architecture.get("pattern", "N/A")
    n_layers = len(architecture.get("layers", []))
    n_endpoints = len(architecture.get("endpoints", []))

    return f"""Eres un ingeniero QA senior. Evalua la calidad del proyecto generado.

PROYECTO: {name}
DESCRIPCION: {desc}

ARQUITECTURA:
- Patron: {pattern}
- Capas: {n_layers}
- Endpoints: {n_endpoints}

ARCHIVOS GENERADOS:
{files_str}

Evalua y genera un JSON con esta estructura:
{{
  "project": "{slug}",
  "overall_score": 85,
  "categories": {{
    "structure": {{"score": 90, "findings": [], "recommendations": []}},
    "security": {{"score": 80, "findings": [], "vulnerabilities": [], "recommendations": []}},
    "performance": {{"score": 85, "findings": [], "bottlenecks": [], "recommendations": []}},
    "code_quality": {{"score": 85, "findings": [], "recommendations": []}},
    "testing": {{"score": 70, "findings": [], "missing_tests": [], "recommendations": []}}
  }},
  "critical_issues": [],
  "summary": "Resumen ejecutivo"
}}

Se objetivo y detallado. Responde SOLO con el JSON valido."""


def _generate_mock(project_config):
    """Genera salida mock para modo demo."""
    slug = project_config["slug"]
    name = project_config["name"]

    return {
        "project": slug,
        "overall_score": 82,
        "categories": {
            "structure": {
                "score": 88,
                "findings": [
                    "Separacion clara frontend/backend",
                    "Estructura de directorios sigue convenciones estandar",
                    "Configuracion de Vite correcta con proxy al backend",
                ],
                "recommendations": [
                    "Agregar barrel exports en carpetas de componentes",
                    "Implementar alias de paths en Vite",
                ],
            },
            "security": {
                "score": 75,
                "findings": ["CORS configurado correctamente", ".env.example sin valores sensibles"],
                "vulnerabilities": [
                    "API endpoints sin autenticacion",
                    "Falta rate limiting en endpoints de IA",
                    "Falta validacion de input en endpoints POST",
                ],
                "recommendations": [
                    "Implementar JWT o session-based auth",
                    "Agregar rate limiting",
                    "Validar inputs con zod o joi",
                    "Agregar helmet.js para headers de seguridad",
                ],
            },
            "performance": {
                "score": 83,
                "findings": ["Vite proporciona HMR y code splitting", "React.StrictMode habilitado"],
                "bottlenecks": [
                    "Llamadas a Claude API sin cache pueden ser lentas",
                    "Sin lazy loading de componentes pesados",
                ],
                "recommendations": [
                    "Implementar cache de respuestas de IA",
                    "Usar React.lazy() para code splitting",
                    "Agregar compresion gzip en el backend",
                ],
            },
            "code_quality": {
                "score": 85,
                "findings": ["Codigo limpio y legible", "Uso correcto de hooks de React", "Estructura modular"],
                "recommendations": [
                    "Agregar ESLint + Prettier",
                    "Implementar TypeScript",
                    "Agregar JSDoc a funciones publicas",
                ],
            },
            "testing": {
                "score": 65,
                "findings": ["No se detectaron archivos de test"],
                "missing_tests": [
                    "Tests unitarios (Vitest + Testing Library)",
                    "Tests de endpoints API (supertest)",
                    "Tests de integracion con IA (mocks)",
                    "Tests e2e con Playwright",
                ],
                "recommendations": [
                    "Configurar Vitest para tests unitarios",
                    "Agregar tests de API",
                    "Crear mocks de Claude API",
                    "Implementar CI/CD con tests automaticos",
                ],
            },
        },
        "critical_issues": [
            "Sin autenticacion en endpoints de IA (riesgo de abuso/costos)",
            "Sin tests automatizados",
        ],
        "summary": (
            f"El proyecto {name} tiene una estructura solida con buena separacion "
            f"de responsabilidades. Areas de mejora: seguridad y testing. "
            f"Priorizar auth y tests basicos antes de produccion."
        ),
    }


def run(project_config, context=None):
    """Ejecuta el agente QA Tester."""
    if context is None:
        context = {}

    start_time = time.time()
    slug = project_config["slug"]
    print(f"\n{CYAN}{BOLD}{AGENT_EMOJI} Agente QA Tester{RESET} \u2014 Evaluando calidad de {slug}...")

    result = {
        "agent": "qa_tester", "project": slug,
        "status": "pending", "output": None, "error": None, "duration": 0,
    }

    try:
        client = context.get("client")
        demo_mode = context.get("demo_mode", False)
        architecture = context.get("architecture", {})
        code_manifest = context.get("code_manifest", {})

        if demo_mode or client is None:
            print(f"  {YELLOW}[DEMO]{RESET} Generando reporte QA mock...")
            qa_report = _generate_mock(project_config)
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
            qa_report = json.loads(raw)

        output_dir = context.get("output_dir", f"output/{slug}")
        os.makedirs(output_dir, exist_ok=True)
        output_path = os.path.join(output_dir, "qa_report.json")
        with open(output_path, "w", encoding="utf-8") as f:
            json.dump(qa_report, f, indent=2, ensure_ascii=False)

        score = qa_report.get("overall_score", "N/A")
        result["status"] = "success"
        result["output"] = qa_report
        result["output_file"] = output_path
        elapsed = time.time() - start_time
        result["duration"] = round(elapsed, 2)

        score_color = GREEN if isinstance(score, (int, float)) and score >= 80 else (
            YELLOW if isinstance(score, (int, float)) and score >= 60 else RED
        )
        print(f"  {GREEN}[OK]{RESET} Reporte QA en {elapsed:.1f}s \u2014 Score: {score_color}{score}/100{RESET}")
        print(f"       -> {output_path}")

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
