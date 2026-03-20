#!/usr/bin/env python3
"""
Orquestador del Sistema Multi-Agente
=====================================
Coordina 6 agentes para construir proyectos del portafolio:
  1. Arquitecto  -> architecture.json
  2. Desarrollador -> codigo fuente
  3. QA Tester    -> qa_report.json
  4. Reviewer     -> review.json
  5. Documentador -> README.md, API.md, DEPLOYMENT.md
  6. Deployer     -> docker-compose.yml, deploy.sh, .env.example

Uso:
  python orchestrator.py --project 1        # Construir proyecto 1
  python orchestrator.py --project 1,2,3    # Construir proyectos 1, 2 y 3
  python orchestrator.py --all              # Construir todos
  python orchestrator.py --list             # Listar proyectos
  python orchestrator.py --status           # Ver estado de builds anteriores
  python orchestrator.py --demo --project 1 # Modo demo (sin API key)
"""

import argparse
import json
import os
import sys
import time
from datetime import datetime

# Agregar directorio actual al path para imports
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from config import PROJECTS, get_project, OUTPUT_DIR
from agents import architect, developer, qa_tester, reviewer, documenter, deployer

# ======================================================================
# Colores para terminal
# ======================================================================
CYAN = "\033[96m"
GREEN = "\033[92m"
YELLOW = "\033[93m"
RED = "\033[91m"
MAGENTA = "\033[95m"
RESET = "\033[0m"
BOLD = "\033[1m"
DIM = "\033[2m"

# ======================================================================
# Pipeline de agentes (orden secuencial)
# ======================================================================
AGENT_PIPELINE = [
    {"name": "Arquitecto", "module": architect, "key": "architecture", "icon": "[1/6]"},
    {"name": "Desarrollador", "module": developer, "key": "code_manifest", "icon": "[2/6]"},
    {"name": "QA Tester", "module": qa_tester, "key": "qa_report", "icon": "[3/6]"},
    {"name": "Reviewer", "module": reviewer, "key": "review", "icon": "[4/6]"},
    {"name": "Documentador", "module": documenter, "key": "docs", "icon": "[5/6]"},
    {"name": "Deployer", "module": deployer, "key": "deploy", "icon": "[6/6]"},
]


# ==========================================================================
# Dashboard visual
# ==========================================================================
def print_banner():
    """Muestra el banner del sistema."""
    sep = "=" * 70
    print(f"\n{CYAN}{BOLD}{sep}")
    print("   SISTEMA MULTI-AGENTE - Portafolio IA & Automatizacion")
    print("   Christian Hernandez")
    print(f"{sep}{RESET}")
    print(f"{DIM}   6 agentes IA trabajando en equipo para construir proyectos{RESET}\n")


def print_project_header(project):
    """Muestra el header de un proyecto."""
    slug = project["slug"]
    name = project["name"]
    port = project["port"]
    sep = "-" * 70
    print(f"\n{MAGENTA}{BOLD}{sep}")
    print(f"  PROYECTO #{project['id']}: {name}")
    print(f"  Slug: {slug} | Puerto: {port}")
    print(f"{sep}{RESET}")
    print(f"{DIM}  {project['description']}{RESET}\n")


def print_progress_bar(current, total, label="", width=40):
    """Muestra una barra de progreso."""
    filled = int(width * current / total)
    bar = "#" * filled + "-" * (width - filled)
    pct = current / total * 100
    color = GREEN if pct == 100 else (YELLOW if pct >= 50 else CYAN)
    print(f"  {color}[{bar}]{RESET} {pct:5.1f}% {label}")


def print_agent_summary(results):
    """Muestra resumen de ejecucion de agentes."""
    sep = "-" * 55
    print(f"\n{BOLD}  Resumen de agentes:{RESET}")
    print(f"  {sep}")
    for r in results:
        agent = r["agent"]
        status = r["status"]
        duration = r["duration"]
        if status == "success":
            icon = f"{GREEN}OK{RESET}"
        elif status == "error":
            icon = f"{RED}ERROR{RESET}"
        else:
            icon = f"{YELLOW}SKIP{RESET}"
        print(f"  {icon}  {agent:<20} {duration:>6.1f}s")
    print(f"  {sep}")


def print_final_dashboard(all_results):
    """Muestra el dashboard final con resultados de todos los proyectos."""
    sep = "=" * 70
    print(f"\n{CYAN}{BOLD}{sep}")
    print("   RESULTADOS FINALES")
    print(f"{sep}{RESET}\n")

    total_time = 0
    for project_slug, data in all_results.items():
        name = data.get("name", project_slug)
        status = data.get("status", "unknown")
        duration = data.get("duration", 0)
        total_time += duration

        qa_score = "N/A"
        review_score = "N/A"
        grade = "?"

        for r in data.get("results", []):
            if r["agent"] == "qa_tester" and r.get("output"):
                qa_score = r["output"].get("overall_score", "N/A")
            if r["agent"] == "reviewer" and r.get("output"):
                review_score = r["output"].get("final_score", "N/A")
                grade = r["output"].get("grade", "?")

        if status == "success":
            status_str = f"{GREEN}COMPLETADO{RESET}"
        elif status == "partial":
            status_str = f"{YELLOW}PARCIAL{RESET}"
        else:
            status_str = f"{RED}FALLIDO{RESET}"

        def score_color(s):
            if not isinstance(s, (int, float)):
                return f"{DIM}{s}{RESET}"
            if s >= 80:
                return f"{GREEN}{s}{RESET}"
            if s >= 60:
                return f"{YELLOW}{s}{RESET}"
            return f"{RED}{s}{RESET}"

        print(f"  {status_str}  {name:<30} QA: {score_color(qa_score):>12}  Review: {score_color(review_score):>12} ({grade})  {duration:.1f}s")

    print(f"\n  {DIM}Tiempo total: {total_time:.1f}s{RESET}")
    print(f"{CYAN}{sep}{RESET}\n")


# ==========================================================================
# Inicializacion del cliente API
# ==========================================================================
def init_client(demo_mode=False):
    """
    Inicializa el cliente de Anthropic.
    Retorna (client, demo_mode) - si no hay API key, activa demo mode.
    """
    if demo_mode:
        print(f"  {YELLOW}[MODO DEMO]{RESET} Generando salidas mock (sin API key)")
        return None, True

    api_key = os.environ.get("ANTHROPIC_API_KEY", "")

    if not api_key or api_key.startswith("sk-ant-..."):
        try:
            from dotenv import load_dotenv
            env_path = os.path.join(os.path.dirname(__file__), ".env")
            load_dotenv(env_path)
            api_key = os.environ.get("ANTHROPIC_API_KEY", "")
        except ImportError:
            pass

    if not api_key or api_key.startswith("sk-ant-..."):
        print(f"  {YELLOW}[AVISO]{RESET} No se encontro ANTHROPIC_API_KEY")
        print(f"  {YELLOW}[MODO DEMO]{RESET} Activado automaticamente")
        return None, True

    try:
        import anthropic
        client = anthropic.Anthropic(api_key=api_key)
        print(f"  {GREEN}[API]{RESET} Cliente Anthropic inicializado correctamente")
        return client, False
    except ImportError:
        print(f"  {RED}[ERROR]{RESET} Paquete 'anthropic' no instalado. Ejecuta: pip install anthropic")
        print(f"  {YELLOW}[MODO DEMO]{RESET} Activado como fallback")
        return None, True
    except Exception as e:
        print(f"  {RED}[ERROR]{RESET} Error inicializando cliente: {e}")
        print(f"  {YELLOW}[MODO DEMO]{RESET} Activado como fallback")
        return None, True


# ==========================================================================
# Ejecucion del pipeline por proyecto
# ==========================================================================
def build_project(project, client=None, demo_mode=False):
    """
    Ejecuta el pipeline completo de 6 agentes para un proyecto.

    Args:
        project: dict con la configuracion del proyecto
        client: cliente Anthropic (None para demo)
        demo_mode: si True, genera salidas mock

    Returns:
        dict con resultados de todos los agentes
    """
    slug = project["slug"]
    output_dir = os.path.join(OUTPUT_DIR, slug)
    os.makedirs(output_dir, exist_ok=True)

    print_project_header(project)

    # Contexto compartido entre agentes
    context = {
        "client": client,
        "demo_mode": demo_mode,
        "output_dir": output_dir,
    }

    results = []
    project_start = time.time()

    for i, agent_info in enumerate(AGENT_PIPELINE):
        agent_name = agent_info["name"]
        agent_module = agent_info["module"]
        context_key = agent_info["key"]
        icon = agent_info["icon"]

        # Barra de progreso
        print_progress_bar(i, len(AGENT_PIPELINE), f"{icon} {agent_name}")

        # Ejecutar agente
        try:
            result = agent_module.run(project, context)
            results.append(result)

            # Pasar output al contexto para el siguiente agente
            if result["status"] == "success" and result.get("output"):
                context[context_key] = result["output"]

        except Exception as e:
            print(f"  {RED}[ERROR CRITICO]{RESET} Agente {agent_name} fallo: {e}")
            results.append({
                "agent": agent_info["key"],
                "project": slug,
                "status": "error",
                "error": str(e),
                "duration": 0,
            })

    # Barra de progreso completa
    print_progress_bar(len(AGENT_PIPELINE), len(AGENT_PIPELINE), "Pipeline completado")

    # Resumen
    print_agent_summary(results)

    # Determinar estado general
    successes = sum(1 for r in results if r["status"] == "success")
    total_duration = round(time.time() - project_start, 2)

    if successes == len(AGENT_PIPELINE):
        status = "success"
    elif successes > 0:
        status = "partial"
    else:
        status = "failed"

    # Guardar build_result.json
    build_result = {
        "project": slug,
        "name": project["name"],
        "status": status,
        "agents_succeeded": successes,
        "agents_total": len(AGENT_PIPELINE),
        "duration": total_duration,
        "timestamp": datetime.now().isoformat(),
        "demo_mode": demo_mode,
        "results": results,
    }

    result_path = os.path.join(output_dir, "build_result.json")
    with open(result_path, "w", encoding="utf-8") as f:
        json.dump(build_result, f, indent=2, ensure_ascii=False, default=str)

    print(f"\n  {GREEN}Build result guardado en:{RESET} {result_path}")

    return build_result


# ==========================================================================
# Comandos CLI
# ==========================================================================
def cmd_list():
    """Lista todos los proyectos disponibles."""
    print(f"\n{BOLD}  Proyectos disponibles:{RESET}\n")
    for p in PROJECTS:
        stack_list = ", ".join(p["stack"].values())
        print(f"  {CYAN}{p['id']}{RESET}. {BOLD}{p['name']}{RESET}")
        print(f"     Slug: {p['slug']} | Puerto: {p['port']}")
        print(f"     {DIM}{p['description'][:80]}...{RESET}")
        print(f"     Stack: {DIM}{stack_list[:70]}{RESET}")
        print()


def cmd_status():
    """Muestra el estado de builds anteriores."""
    print(f"\n{BOLD}  Estado de builds anteriores:{RESET}\n")

    if not os.path.exists(OUTPUT_DIR):
        print(f"  {DIM}No hay builds anteriores. Directorio output/ no existe.{RESET}\n")
        return

    found = False
    for p in PROJECTS:
        result_path = os.path.join(OUTPUT_DIR, p["slug"], "build_result.json")
        if os.path.exists(result_path):
            found = True
            with open(result_path, "r", encoding="utf-8") as f:
                data = json.load(f)

            status = data.get("status", "unknown")
            ts = data.get("timestamp", "N/A")
            duration = data.get("duration", 0)
            demo = " [DEMO]" if data.get("demo_mode") else ""
            succeeded = data.get("agents_succeeded", 0)
            total = data.get("agents_total", 6)

            if status == "success":
                icon = f"{GREEN}OK{RESET}"
            elif status == "partial":
                icon = f"{YELLOW}PARCIAL{RESET}"
            else:
                icon = f"{RED}FALLO{RESET}"

            print(f"  {icon}  {p['name']:<30} {succeeded}/{total} agentes  {duration:.1f}s  {DIM}{ts}{demo}{RESET}")

    if not found:
        print(f"  {DIM}No hay builds anteriores.{RESET}")
    print()


def cmd_build(project_ids, demo_mode=False):
    """Construye uno o mas proyectos."""
    print_banner()

    # Inicializar cliente
    client, demo_mode = init_client(demo_mode)

    all_results = {}
    total_start = time.time()

    for pid in project_ids:
        project = get_project(pid)
        if project is None:
            print(f"\n  {RED}[ERROR]{RESET} Proyecto #{pid} no encontrado. Usa --list para ver disponibles.")
            continue

        result = build_project(project, client, demo_mode)
        all_results[project["slug"]] = result

    # Dashboard final
    if len(all_results) > 0:
        print_final_dashboard(all_results)

    total_elapsed = time.time() - total_start
    print(f"  {DIM}Tiempo total de ejecucion: {total_elapsed:.1f}s{RESET}\n")


# ==========================================================================
# Main / CLI
# ==========================================================================
def main():
    parser = argparse.ArgumentParser(
        description="Sistema Multi-Agente - Construye proyectos del portafolio con IA",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Ejemplos:
  python orchestrator.py --list              # Ver proyectos
  python orchestrator.py --project 1         # Construir proyecto 1
  python orchestrator.py --project 1,2,3     # Construir varios
  python orchestrator.py --all               # Construir todos
  python orchestrator.py --all --demo        # Modo demo (sin API key)
  python orchestrator.py --status            # Ver estado de builds
        """,
    )

    parser.add_argument("--project", "-p", type=str, help="ID(s) del proyecto a construir (ej: 1 o 1,2,3)")
    parser.add_argument("--all", "-a", action="store_true", help="Construir todos los proyectos")
    parser.add_argument("--list", "-l", action="store_true", help="Listar proyectos disponibles")
    parser.add_argument("--status", "-s", action="store_true", help="Ver estado de builds anteriores")
    parser.add_argument("--demo", "-d", action="store_true", help="Modo demo: salidas mock sin API key")

    args = parser.parse_args()

    # Sin argumentos -> mostrar ayuda y lista
    if len(sys.argv) == 1:
        parser.print_help()
        print()
        cmd_list()
        return

    if args.list:
        cmd_list()
        return

    if args.status:
        cmd_status()
        return

    if args.all:
        project_ids = [p["id"] for p in PROJECTS]
        cmd_build(project_ids, demo_mode=args.demo)
        return

    if args.project:
        try:
            project_ids = [int(x.strip()) for x in args.project.split(",")]
        except ValueError:
            print(f"\n  {RED}[ERROR]{RESET} IDs de proyecto invalidos. Usa numeros separados por coma.")
            print("  Ejemplo: --project 1,2,3\n")
            return
        cmd_build(project_ids, demo_mode=args.demo)
        return

    parser.print_help()


if __name__ == "__main__":
    main()
