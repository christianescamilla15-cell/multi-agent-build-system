"""
Agente Desarrollador - Genera codigo fuente basado en la arquitectura.
Produce archivos de codigo organizados segun la estructura definida por el Arquitecto.
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

AGENT_NAME = "Desarrollador"
AGENT_EMOJI = "[DEV]"


def _build_prompt(project_config, architecture):
    """Construye el prompt para el agente desarrollador."""
    arch_json = json.dumps(architecture, indent=2, ensure_ascii=False)
    port = project_config["port"]
    name = project_config["name"]
    slug = project_config["slug"]
    desc = project_config["description"]

    return f"""Eres un desarrollador senior full-stack. Genera el codigo fuente principal para este proyecto.

PROYECTO: {name}
DESCRIPCION: {desc}
PUERTO: {port}

ARQUITECTURA DEFINIDA:
{arch_json}

Genera un JSON con los archivos de codigo principales. Cada archivo debe tener codigo funcional.
Formato de respuesta (JSON estricto):
{{
  "files": [
    {{"path": "ruta/archivo.ext", "content": "contenido", "description": "que hace"}}
  ],
  "dependencies": {{"frontend": {{}}, "backend": {{}}}},
  "scripts": {{"dev": "cmd", "build": "cmd", "start": "cmd"}},
  "setup_instructions": ["paso 1", "paso 2"]
}}

El codigo debe ser funcional, usar el puerto {port}, y seguir las mejores practicas.
Responde SOLO con el JSON valido, sin markdown ni explicaciones."""


def _generate_mock(project_config):
    """Genera salida mock cuando no hay API key disponible."""
    slug = project_config["slug"]
    port = project_config["port"]
    name = project_config["name"]
    desc = project_config["description"]

    backend_stack = project_config["stack"].get("backend", "")
    is_python_backend = "Python" in backend_stack or "FastAPI" in backend_stack

    pkg = {
        "name": slug, "private": True, "version": "1.0.0", "type": "module",
        "scripts": {"dev": "vite", "build": "vite build", "preview": "vite preview"},
        "dependencies": {"react": "^18.2.0", "react-dom": "^18.2.0"},
        "devDependencies": {
            "@vitejs/plugin-react": "^4.2.0", "vite": "^5.0.0",
            "tailwindcss": "^3.4.0", "autoprefixer": "^10.4.0", "postcss": "^8.4.0",
        },
    }

    files = [
        {"path": "package.json", "content": json.dumps(pkg, indent=2), "description": "Dependencias frontend"},
        {
            "path": "vite.config.js",
            "content": f"""import {{ defineConfig }} from 'vite'
import react from '@vitejs/plugin-react'

export default defineConfig({{
  plugins: [react()],
  server: {{
    port: {port},
    proxy: {{ '/api': 'http://localhost:{port + 1000}' }}
  }}
}})
""",
            "description": "Configuracion de Vite",
        },
        {
            "path": "index.html",
            "content": f"""<!DOCTYPE html>
<html lang="es">
<head>
  <meta charset="UTF-8" />
  <meta name="viewport" content="width=device-width, initial-scale=1.0" />
  <title>{name}</title>
</head>
<body>
  <div id="root"></div>
  <script type="module" src="/src/main.jsx"></script>
</body>
</html>
""",
            "description": "HTML entry point",
        },
        {
            "path": "src/main.jsx",
            "content": """import React from 'react'
import ReactDOM from 'react-dom/client'
import App from './App'
import './index.css'

ReactDOM.createRoot(document.getElementById('root')).render(
  <React.StrictMode>
    <App />
  </React.StrictMode>
)
""",
            "description": "React entry point",
        },
        {
            "path": "src/App.jsx",
            "content": f"""import {{ useState, useEffect }} from 'react'

function App() {{
  const [status, setStatus] = useState('cargando...')

  useEffect(() => {{
    fetch('/api/health')
      .then(res => res.json())
      .then(data => setStatus(data.status))
      .catch(() => setStatus('sin conexion al backend'))
  }}, [])

  return (
    <div className="min-h-screen bg-gray-900 text-white">
      <header className="bg-gray-800 border-b border-gray-700 px-6 py-4">
        <h1 className="text-2xl font-bold">{name}</h1>
        <p className="text-gray-400 text-sm">Estado: {{status}}</p>
      </header>
      <main className="p-6">
        <div className="max-w-4xl mx-auto">
          <div className="bg-gray-800 rounded-lg p-6 border border-gray-700">
            <h2 className="text-xl font-semibold mb-4">Bienvenido</h2>
            <p className="text-gray-300">{desc}</p>
          </div>
        </div>
      </main>
    </div>
  )
}}

export default App
""",
            "description": "Componente principal de React",
        },
        {
            "path": "src/index.css",
            "content": """@tailwind base;
@tailwind components;
@tailwind utilities;

body { margin: 0; font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif; }
""",
            "description": "Estilos globales con TailwindCSS",
        },
        {
            "path": ".env.example",
            "content": f"# {name}\nANTHROPIC_API_KEY=sk-ant-...\nPORT={port}\nNODE_ENV=development\n",
            "description": "Variables de entorno de ejemplo",
        },
    ]

    if is_python_backend:
        files.append({
            "path": "server/main.py",
            "content": f"""\"\"\"Backend principal de {name}.\"\"\"
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
import uvicorn

app = FastAPI(title="{name}", version="1.0.0")
app.add_middleware(CORSMiddleware, allow_origins=["http://localhost:{port}"],
                   allow_credentials=True, allow_methods=["*"], allow_headers=["*"])

@app.get("/api/health")
async def health():
    return {{"status": "ok", "service": "{slug}"}}

@app.post("/api/ai/generate")
async def ai_generate(payload: dict):
    return {{"result": "Respuesta de IA placeholder", "input": payload}}

if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port={port + 1000})
""",
            "description": "Backend FastAPI",
        })
        files.append({
            "path": "server/requirements.txt",
            "content": "fastapi>=0.104.0\nuvicorn>=0.24.0\nanthropic>=0.39.0\npython-dotenv>=1.0.0\n",
            "description": "Dependencias backend Python",
        })
    else:
        files.append({
            "path": "server/index.js",
            "content": f"""import express from 'express'
import cors from 'cors'
import dotenv from 'dotenv'

dotenv.config()
const app = express()
const PORT = process.env.PORT || {port + 1000}

app.use(cors({{ origin: 'http://localhost:{port}' }}))
app.use(express.json())

app.get('/api/health', (req, res) => {{
  res.json({{ status: 'ok', service: '{slug}' }})
}})

app.post('/api/ai/generate', async (req, res) => {{
  try {{
    res.json({{ result: 'Respuesta de IA placeholder', input: req.body }})
  }} catch (error) {{
    res.status(500).json({{ error: error.message }})
  }}
}})

app.listen(PORT, () => {{
  console.log(`[{slug}] Backend en http://localhost:${{PORT}}`)
}})
""",
            "description": "Backend Express.js",
        })
        server_pkg = {
            "name": f"{slug}-server", "version": "1.0.0", "type": "module",
            "scripts": {"dev": "node --watch index.js", "start": "node index.js"},
            "dependencies": {"express": "^4.18.2", "cors": "^2.8.5", "dotenv": "^16.3.1", "@anthropic-ai/sdk": "^0.39.0"},
        }
        files.append({
            "path": "server/package.json",
            "content": json.dumps(server_pkg, indent=2),
            "description": "Dependencias backend Node.js",
        })

    pip_or_npm = "pip install -r requirements.txt" if is_python_backend else "npm install"
    run_backend = "python main.py" if is_python_backend else "npm run dev"

    return {
        "files": files,
        "dependencies": {
            "frontend": {"react": "^18.2.0", "vite": "^5.0.0", "tailwindcss": "^3.4.0"},
            "backend": (
                {"fastapi": "^0.104.0", "uvicorn": "^0.24.0"} if is_python_backend
                else {"express": "^4.18.2", "cors": "^2.8.5"}
            ),
        },
        "scripts": {"dev": "npm run dev", "build": "npm run build", "start": "npm run preview"},
        "setup_instructions": [
            "npm install (frontend)",
            f"cd server && {pip_or_npm}",
            "Copiar .env.example a .env y configurar API keys",
            f"npm run dev (frontend en puerto {port})",
            f"cd server && {run_backend} (backend en puerto {port + 1000})",
        ],
    }


def run(project_config, context=None):
    """
    Ejecuta el agente desarrollador.

    Args:
        project_config: Configuracion del proyecto
        context: Debe contener la arquitectura del agente anterior

    Returns:
        dict con los archivos generados y metadatos
    """
    if context is None:
        context = {}

    start_time = time.time()
    slug = project_config["slug"]
    print(f"\n{CYAN}{BOLD}{AGENT_EMOJI} Agente Desarrollador{RESET} \u2014 Generando codigo de {slug}...")

    result = {
        "agent": "developer", "project": slug,
        "status": "pending", "output": None, "error": None, "duration": 0,
    }

    try:
        client = context.get("client")
        demo_mode = context.get("demo_mode", False)
        architecture = context.get("architecture", {})

        if demo_mode or client is None:
            print(f"  {YELLOW}[DEMO]{RESET} Generando codigo mock...")
            code_output = _generate_mock(project_config)
        else:
            from config import MODEL, MAX_TOKENS
            print(f"  {CYAN}[API]{RESET} Consultando {MODEL}...")
            prompt = _build_prompt(project_config, architecture)
            response = client.messages.create(
                model=MODEL, max_tokens=MAX_TOKENS,
                messages=[{"role": "user", "content": prompt}],
            )
            raw = response.content[0].text.strip()
            if raw.startswith("```"):
                raw = raw.split("\n", 1)[1]
                if raw.endswith("```"):
                    raw = raw[: raw.rfind("```")]
            code_output = json.loads(raw)

        # Guardar archivos generados
        output_dir = context.get("output_dir", f"output/{slug}")
        os.makedirs(output_dir, exist_ok=True)

        manifest_path = os.path.join(output_dir, "code_manifest.json")
        with open(manifest_path, "w", encoding="utf-8") as f:
            json.dump(code_output, f, indent=2, ensure_ascii=False)

        code_dir = os.path.join(output_dir, "code")
        files_written = 0
        for file_entry in code_output.get("files", []):
            file_path = os.path.join(code_dir, file_entry["path"])
            os.makedirs(os.path.dirname(file_path), exist_ok=True)
            with open(file_path, "w", encoding="utf-8") as f:
                f.write(file_entry["content"])
            files_written += 1

        result["status"] = "success"
        result["output"] = code_output
        result["output_file"] = manifest_path
        result["files_written"] = files_written

        elapsed = time.time() - start_time
        result["duration"] = round(elapsed, 2)
        print(f"  {GREEN}[OK]{RESET} {files_written} archivos generados en {elapsed:.1f}s -> {code_dir}/")

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
