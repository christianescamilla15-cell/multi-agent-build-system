"""
Configuración central del sistema multi-agente.
Define los 5 proyectos del portafolio y parámetros globales.
"""

# Modelo de IA a usar (Haiku para eficiencia de costos)
MODEL = "claude-haiku-4-5-20251001"
MAX_TOKENS = 4096

# Directorio base de salida
OUTPUT_DIR = "output"

# Definición de los 5 proyectos del portafolio
PROJECTS = [
    {
        "id": 1,
        "slug": "chatbot-multiagente",
        "name": "Chatbot Multi-Agente",
        "description": (
            "Sistema de chatbot inteligente con 5 agentes IA especializados "
            "(ventas, soporte, técnico, RRHH, general). Cada agente tiene personalidad "
            "y conocimiento propio. Router inteligente clasifica mensajes."
        ),
        "port": 3001,
        "stack": {
            "frontend": "React 18 + Vite 5 + TailwindCSS",
            "backend": "Node.js + Express",
            "ai": "Claude API (Anthropic)",
            "automation": "n8n (workflow automation)",
            "database": "SQLite (historial chat)",
        },
        "features": [
            "5 agentes especializados con personalidad única",
            "Router inteligente de mensajes",
            "Historial de conversaciones persistente",
            "Panel de administración",
            "Integración con n8n para workflows",
            "WebSocket para chat en tiempo real",
        ],
        "dir": "proyectos/01-chatbot-multiagente",
    },
    {
        "id": 2,
        "slug": "content-studio",
        "name": "Content Studio",
        "description": (
            "Plataforma de generación de contenido con IA. Crea textos para blog, "
            "redes sociales, emails y landing pages. Genera imágenes con DALL-E 3. "
            "Calendario editorial integrado."
        ),
        "port": 3002,
        "stack": {
            "frontend": "React 18 + Vite 5 + TailwindCSS",
            "backend": "Node.js + Express",
            "ai": "Claude API (texto) + DALL-E 3 (imágenes)",
            "database": "SQLite (contenido generado)",
        },
        "features": [
            "Generación de textos para múltiples plataformas",
            "Generación de imágenes con DALL-E 3",
            "Calendario editorial con drag & drop",
            "Templates personalizables",
            "Historial de generaciones",
            "Exportación a múltiples formatos",
        ],
        "dir": "proyectos/02-content-studio",
    },
    {
        "id": 3,
        "slug": "finance-ai",
        "name": "Finance AI Dashboard",
        "description": (
            "Dashboard financiero inteligente con análisis predictivo. "
            "Visualización de datos, predicciones con IA, alertas automáticas "
            "y reportes generados por Claude."
        ),
        "port": 3003,
        "stack": {
            "frontend": "React 18 + Vite 5 + Recharts + TailwindCSS",
            "backend": "Python + FastAPI",
            "ai": "Claude API (análisis) + scikit-learn (predicciones)",
            "database": "SQLite (datos financieros)",
        },
        "features": [
            "Dashboard interactivo con gráficos en tiempo real",
            "Predicciones financieras con ML",
            "Análisis de sentimiento del mercado",
            "Alertas inteligentes configurables",
            "Reportes automáticos generados por IA",
            "Importación de datos CSV/Excel",
        ],
        "dir": "proyectos/03-finance-ai",
    },
    {
        "id": 4,
        "slug": "hr-scout",
        "name": "HR Scout",
        "description": (
            "Sistema de filtrado y análisis de CVs con IA. Extrae información "
            "clave, puntúa candidatos, genera reportes comparativos y sugiere "
            "preguntas de entrevista personalizadas."
        ),
        "port": 3004,
        "stack": {
            "frontend": "React 18 + Vite 5 + TailwindCSS",
            "backend": "Python + FastAPI",
            "ai": "Claude API (análisis CV + generación preguntas)",
            "database": "SQLite (candidatos)",
        },
        "features": [
            "Upload y parsing de CVs (PDF, DOCX)",
            "Extracción automática de habilidades y experiencia",
            "Scoring inteligente de candidatos",
            "Comparativa entre candidatos",
            "Generación de preguntas de entrevista",
            "Reportes exportables",
        ],
        "dir": "proyectos/04-hr-scout",
    },
    {
        "id": 5,
        "slug": "client-hub",
        "name": "Client Hub",
        "description": (
            "Portal de clientes No-Code con integración Airtable. Gestión de "
            "proyectos, comunicación centralizada, documentos compartidos y "
            "asistente IA integrado."
        ),
        "port": 3005,
        "stack": {
            "frontend": "React 18 + Vite 5 + TailwindCSS",
            "backend": "Node.js + Express + Airtable API",
            "ai": "Claude API (asistente integrado)",
            "database": "Airtable (datos de clientes y proyectos)",
        },
        "features": [
            "Dashboard de cliente personalizado",
            "Gestión de proyectos con Kanban",
            "Chat con asistente IA",
            "Compartir documentos y archivos",
            "Notificaciones en tiempo real",
            "Integración bidireccional con Airtable",
        ],
        "dir": "proyectos/05-client-hub",
    },
]


def get_project(project_id: int) -> dict | None:
    """Obtiene un proyecto por su ID (1-5)."""
    for project in PROJECTS:
        if project["id"] == project_id:
            return project
    return None


def get_project_by_slug(slug: str) -> dict | None:
    """Obtiene un proyecto por su slug."""
    for project in PROJECTS:
        if project["slug"] == slug:
            return project
    return None
