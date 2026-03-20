# 🤖 Multi-Agent Build System

Sistema de construcción autónoma de proyectos con **6 agentes especializados** que trabajan en pipeline para diseñar, desarrollar, testear, revisar, documentar y desplegar los 5 proyectos del portafolio.

## Arquitectura del Sistema

```
┌─────────────────────────────────────────────────────────┐
│                    ORCHESTRATOR                          │
│         Coordina el pipeline de 6 agentes               │
└───────────────────────┬─────────────────────────────────┘
                        │
          ┌─────────────▼─────────────┐
          │    Por cada proyecto:      │
          └─────────────┬─────────────┘
                        │
    ┌───────────────────▼───────────────────────────────┐
    │                                                   │
    ▼           ▼           ▼       ▼      ▼       ▼   │
[Arquitecto] [Developer] [QA]  [Review] [Docs] [Deploy] │
    │           │           │       │      │       │    │
    ▼           ▼           ▼       ▼      ▼       ▼   │
architecture  código     qa_report review README docker │
.json        /src        .json    .json   .md    .yml   │
    └───────────────────────────────────────────────────┘
```

## Agentes

| Agente | Responsabilidad | Output |
|--------|----------------|--------|
| 🎯 Orchestrator | Coordina el pipeline completo | `build_result.json` |
| 🏗️ Arquitecto | Diseña estructura técnica | `architecture.json` |
| 💻 Developer | Genera código de producción | Archivos del proyecto |
| 🧪 QA Tester | Ejecuta pruebas automatizadas | `qa_report.json` |
| 🔍 Reviewer | Audita calidad y da score | `review.json` |
| 📝 Documentador | Genera README y API docs | `README.md`, `API.md` |
| 🚀 Deployer | Configura infraestructura | `docker-compose.yml`, `deploy.sh` |

## Proyectos que construye

1. **Chatbot Multiagente** — Atención al cliente con n8n + Claude + Notion
2. **ContentStudio** — Generador de contenido visual con DALL-E + Claude
3. **FinanceAI** — Dashboard financiero con detección de anomalías
4. **HRScout** — Sistema de filtrado de CVs con LLMs
5. **ClientHub** — Portal de clientes No-Code con IA

## Instalación

```bash
# 1. Clonar o descargar el sistema
cd multi-agent-system

# 2. Crear entorno virtual
python -m venv venv
source venv/bin/activate    # Linux/Mac
venv\Scripts\activate       # Windows

# 3. Instalar dependencias
pip install -r requirements.txt

# 4. Configurar API Key
export ANTHROPIC_API_KEY=sk-ant-tu-clave-aqui
# O crear archivo .env:
echo "ANTHROPIC_API_KEY=sk-ant-tu-clave" > .env
```

## Uso

```bash
# Construir todos los proyectos
python orchestrator.py

# Construir solo un proyecto específico
python orchestrator.py --project 1    # Chatbot
python orchestrator.py --project 2    # ContentStudio
python orchestrator.py --project 3    # FinanceAI
python orchestrator.py --project 4    # HRScout
python orchestrator.py --project 5    # ClientHub

# Listar proyectos disponibles
python orchestrator.py --list

# Directorio de salida personalizado
python orchestrator.py --output ./mis-proyectos
```

## Output por proyecto

```
output/
└── chatbot-multiagente/
    ├── architecture.json     # Diseño técnico (Arquitecto)
    ├── src/
    │   └── App.jsx           # Código frontend (Developer)
    ├── backend/
    │   └── server.js         # Código backend (Developer)
    ├── package.json          # Configuración (Developer)
    ├── .env.example          # Variables de entorno (Developer)
    ├── qa_report.json        # Reporte de pruebas (QA)
    ├── review.json           # Auditoría de calidad (Reviewer)
    ├── README.md             # Documentación (Documentador)
    ├── DEPLOYMENT.md         # Guía de deploy (Documentador)
    ├── API.md                # Docs de API (Documentador)
    ├── docker-compose.yml    # Infraestructura (Deployer)
    ├── deploy.sh             # Script de deploy (Deployer)
    └── build_result.json     # Resultado del build (Orchestrator)
```

## Dashboard en tiempo real

El sistema incluye un dashboard terminal que muestra el progreso de cada proyecto y el agente activo en tiempo real durante la ejecución.

```
═══════════════════════════════════════════════════════════════
  🤖 MULTI-AGENT BUILD SYSTEM — DASHBOARD
  ────────────────────────────────────────────────────────────
  ✅ Chatbot Multiagente                ████████████████████ 100%
  ◉ ContentStudio                      █████████░░░░░░░░░░░  45% [Developer]
  ○ FinanceAI                          ░░░░░░░░░░░░░░░░░░░░   0%
  ○ HRScout                            ░░░░░░░░░░░░░░░░░░░░   0%
  ○ ClientHub                          ░░░░░░░░░░░░░░░░░░░░   0%
  ────────────────────────────────────────────────────────────
```

## Costos estimados (Claude Haiku)

| Proyectos | API Calls | Costo aprox |
|-----------|-----------|-------------|
| 1 proyecto | ~15 calls | ~$0.02 |
| 5 proyectos | ~75 calls | ~$0.10 |

## Estructura del código

```
multi-agent-system/
├── orchestrator.py          # Punto de entrada y coordinador
├── requirements.txt
├── README.md
├── agents/
│   ├── __init__.py
│   ├── architect.py         # Agente Arquitecto
│   ├── developer.py         # Agente Developer
│   ├── qa_tester.py         # Agente QA
│   ├── reviewer.py          # Agente Reviewer
│   ├── documenter.py        # Agente Documentador
│   └── deployer.py          # Agente Deployer
└── utils/
    ├── __init__.py
    ├── claude_api.py         # Cliente Claude con reintentos
    ├── logger.py             # Logger con colores
    └── dashboard.py          # Dashboard terminal
```
