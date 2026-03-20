"""Dashboard de progreso en tiempo real (terminal)."""
import sys
import threading
import time

STATUS_ICONS = {
    "pending":   "○",
    "running":   "◉",
    "completed": "✅",
    "failed":    "❌",
}

COLORS = {
    "reset":   "\033[0m",
    "green":   "\033[92m",
    "yellow":  "\033[93m",
    "red":     "\033[91m",
    "cyan":    "\033[96m",
    "gray":    "\033[90m",
    "bold":    "\033[1m",
    "blue":    "\033[94m",
}

class Dashboard:
    def __init__(self, projects: list):
        self.projects = {
            p["id"]: {
                "name":          p["name"],
                "status":        "pending",
                "progress":      0,
                "current_agent": None,
            }
            for p in projects
        }
        self._lock    = threading.Lock()
        self._running = False
        self._thread  = None

    def start(self):
        self._running = True
        self._thread  = threading.Thread(target=self._render_loop, daemon=True)
        self._thread.start()

    def update_project(self, pid: int, status: str, progress: int, current_agent: str = None):
        with self._lock:
            self.projects[pid]["status"]        = status
            self.projects[pid]["progress"]      = progress
            self.projects[pid]["current_agent"] = current_agent

    def finalize(self, completed: int, failed: int):
        self._running = False
        if self._thread:
            self._thread.join(timeout=2)

    def _bar(self, pct: int, width: int = 20) -> str:
        filled = int(width * pct / 100)
        bar    = "█" * filled + "░" * (width - filled)
        c      = COLORS["green"] if pct == 100 else COLORS["cyan"]
        r      = COLORS["reset"]
        return f"{c}{bar}{r}"

    def _render_loop(self):
        while self._running:
            self._render()
            time.sleep(0.5)
        self._render()  # Render final

    def _render(self):
        lines = []
        c  = COLORS["cyan"]
        b  = COLORS["bold"]
        g  = COLORS["gray"]
        r  = COLORS["reset"]
        gr = COLORS["green"]
        y  = COLORS["yellow"]
        rd = COLORS["red"]

        lines.append(f"\n{c}{b}  🤖 MULTI-AGENT BUILD SYSTEM — DASHBOARD{r}")
        lines.append(f"{g}  {'─' * 58}{r}")

        with self._lock:
            for pid, info in self.projects.items():
                status  = info["status"]
                pct     = info["progress"]
                name    = info["name"][:42]
                agent   = info["current_agent"] or ""
                icon    = STATUS_ICONS.get(status, "○")

                if status == "completed":
                    sc = gr
                elif status == "running":
                    sc = y
                elif status == "failed":
                    sc = rd
                else:
                    sc = g

                bar   = self._bar(pct)
                agent_str = f"{g} [{agent}]{r}" if agent and status == "running" else ""

                lines.append(
                    f"  {sc}{icon}{r} {b}{name:<42}{r} "
                    f"{bar} {sc}{pct:>3}%{r}{agent_str}"
                )

        lines.append(f"{g}  {'─' * 58}{r}")

        # Mover cursor arriba para sobreescribir
        if hasattr(self, "_last_lines"):
            sys.stdout.write(f"\033[{self._last_lines}A")

        output = "\n".join(lines) + "\n"
        sys.stdout.write(output)
        sys.stdout.flush()
        self._last_lines = len(lines) + 1
