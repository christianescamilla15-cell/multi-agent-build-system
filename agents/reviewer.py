"""
Agente Reviewer - Auditoria de calidad con puntuacion 0-100.
Produce review.json con evaluacion detallada y score final.
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

AGENT_NAME = "Reviewer"
AGENT_EMOJI = "[REV]"


def _build_prompt(project_config, architecture, code_manifest, qa_report):
    """Construye el prompt para el agente reviewer."""
    qa_summary = qa_report.get("summary", "No disponible")
    qa_score = qa_report.get("overall_score", "N/A")
    files_list = [f["path"] for f in code_manifest.get("files", [])[:20]]
    name = project_config["name"]
    slug = project_config["slug"]
    desc = project_config["description"]
    pattern = architecture.get("pattern", "N/A")
    n_layers = len(architecture.get("layers", []))

    return f"""Eres un revisor de codigo senior. Realiza una auditoria completa del proyecto.

PROYECTO: {name}
DESCRIPCION: {desc}
RESUMEN QA: {qa_summary} (Score: {qa_score}/100)
ARCHIVOS: {json.dumps(files_list, indent=2)}
ARQUITECTURA: {pattern}, {n_layers} capas

Genera un JSON:
{{
  "project": "{slug}",
  "final_score": 85,
  "grade": "A|B|C|D|F",
  "audit": {{
    "architecture_design": {{"score": 90, "verdict": "Aprobado", "notes": []}},
    "code_standards": {{"score": 85, "verdict": "Aprobado", "notes": []}},
    "completeness": {{"score": 80, "verdict": "Con observaciones", "missing_features": [], "notes": []}},
    "maintainability": {{"score": 85, "verdict": "Aprobado", "notes": []}},
    "production_readiness": {{"score": 70, "verdict": "Con observaciones", "blockers": [], "notes": []}}
  }},
  "strengths": [],
  "improvements_required": [],
  "recommendation": "Recomendacion final"
}}

Se riguroso pero justo. Responde SOLO con el JSON valido."""


def _generate_mock(project_config, qa_report):
    """Genera salida mock para modo demo."""
    slug = project_config["slug"]
    name = project_config["name"]
    qa_score = qa_report.get("overall_score", 80)
    final_score = min(95, max(60, qa_score + 3))

    if final_score >= 90: grade = "A"
    elif final_score >= 80: grade = "B"
    elif final_score >= 70: grade = "C"
    elif final_score >= 60: grade = "D"
    else: grade = "F"

    return {
        "project": slug,
        "final_score": final_score,
        "grade": grade,
        "audit": {
            "architecture_design": {
                "score": 90, "verdict": "Aprobado",
                "notes": ["Clean Architecture bien implementada", "Separacion clara de responsabilidades", "Proxy de Vite configurado correctamente"],
            },
            "code_standards": {
                "score": 85, "verdict": "Aprobado",
                "notes": ["React moderno (hooks, functional components)", "Imports organizados", "Falta ESLint/Prettier"],
            },
            "completeness": {
                "score": 78, "verdict": "Con observaciones",
                "missing_features": ["Autenticacion", "Tests automatizados", "Error Boundaries", "Loading states"],
                "notes": ["MVP funcional", "Falta pulir UX para produccion"],
            },
            "maintainability": {
                "score": 87, "verdict": "Aprobado",
                "notes": ["Estructura modular", "Variables de entorno externalizadas", "Codigo legible"],
            },
            "production_readiness": {
                "score": 68, "verdict": "Con observaciones",
                "blockers": ["Sin autenticacion", "Sin rate limiting", "Sin monitoreo"],
                "notes": ["Necesita auth y rate limiting antes de produccion", "Falta Docker y deploy scripts"],
            },
        },
        "strengths": [
            "Arquitectura limpia y organizada", "Stack moderno", "Codigo legible",
            "Buena separacion frontend/backend", "HMR y proxy bien configurados",
        ],
        "improvements_required": [
            "Implementar autenticacion", "Agregar tests", "Rate limiting",
            "Logging estructurado", "Error Boundaries", "Documentacion de API",
        ],
        "recommendation": (
            f"El proyecto {name} tiene base solida. Para produccion: auth, tests y rate limiting. "
            f"Score: {final_score}/100 (Grado {grade})."
        ),
    }


def run(project_config, context=None):
    """Ejecuta el agente reviewer."""
    if context is None:
        context = {}

    start_time = time.time()
    slug = project_config["slug"]
    print(f"\n{CYAN}{BOLD}{AGENT_EMOJI} Agente Reviewer{RESET} \u2014 Auditando calidad de {slug}...")

    result = {
        "agent": "reviewer", "project": slug,
        "status": "pending", "output": None, "error": None, "duration": 0,
    }

    try:
        client = context.get("client")
        demo_mode = context.get("demo_mode", False)
        architecture = context.get("architecture", {})
        code_manifest = context.get("code_manifest", {})
        qa_report = context.get("qa_report", {})

        if demo_mode or client is None:
            print(f"  {YELLOW}[DEMO]{RESET} Generando review mock...")
            review = _generate_mock(project_config, qa_report)
        else:
            from config import MODEL, MAX_TOKENS
            print(f"  {CYAN}[API]{RESET} Consultando {MODEL}...")
            prompt = _build_prompt(project_config, architecture, code_manifest, qa_report)
            response = client.messages.create(
                model=MODEL, max_tokens=MAX_TOKENS,
                messages=[{"role": "user", "content": prompt}],
            )
            raw = response.content[0].text.strip()
            if raw.startswith("```"):
                raw = raw.split("\n", 1)[1]
                if raw.endswith("```"):
                    raw = raw[: raw.rfind("```")]
            review = json.loads(raw)

        output_dir = context.get("output_dir", f"output/{slug}")
        os.makedirs(output_dir, exist_ok=True)
        output_path = os.path.join(output_dir, "review.json")
        with open(output_path, "w", encoding="utf-8") as f:
            json.dump(review, f, indent=2, ensure_ascii=False)

        score = review.get("final_score", "N/A")
        grade = review.get("grade", "?")
        result["status"] = "success"
        result["output"] = review
        result["output_file"] = output_path
        elapsed = time.time() - start_time
        result["duration"] = round(elapsed, 2)

        sv = score if isinstance(score, (int, float)) else 0
        sc = GREEN if sv >= 80 else (YELLOW if sv >= 60 else RED)
        print(f"  {GREEN}[OK]{RESET} Review en {elapsed:.1f}s \u2014 Score: {sc}{score}/100{RESET} (Grado {grade})")
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
