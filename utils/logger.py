"""Logger con colores para el sistema multiagente."""
import time
from datetime import datetime

COLORS = {
    "reset":   "\033[0m",
    "bold":    "\033[1m",
    "cyan":    "\033[96m",
    "green":   "\033[92m",
    "yellow":  "\033[93m",
    "red":     "\033[91m",
    "blue":    "\033[94m",
    "magenta": "\033[95m",
    "white":   "\033[97m",
    "gray":    "\033[90m",
}

AGENT_COLORS = {
    "Orchestrator": "cyan",
    "Arquitecto":   "blue",
    "Developer":    "magenta",
    "QA Tester":    "yellow",
    "Reviewer":     "white",
    "Documentador": "green",
    "Deployer":     "cyan",
}

class AgentLogger:
    def __init__(self, agent_name: str):
        self.name  = agent_name
        self.color = AGENT_COLORS.get(agent_name, "white")
        self.start = time.time()

    def _ts(self):
        return datetime.now().strftime("%H:%M:%S")

    def _prefix(self, symbol: str = "●"):
        c = COLORS[self.color]
        r = COLORS["reset"]
        g = COLORS["gray"]
        return f"{g}[{self._ts()}]{r} {c}{symbol} [{self.name}]{r}"

    def info(self, msg: str):
        print(f"{self._prefix('◆')} {msg}")

    def success(self, msg: str):
        g = COLORS["green"]
        r = COLORS["reset"]
        print(f"{self._prefix('✓')} {g}{msg}{r}")

    def warning(self, msg: str):
        y = COLORS["yellow"]
        r = COLORS["reset"]
        print(f"{self._prefix('⚠')} {y}{msg}{r}")

    def error(self, msg: str):
        red = COLORS["red"]
        r   = COLORS["reset"]
        print(f"{self._prefix('✗')} {red}{msg}{r}")

    def phase(self, num: int, msg: str):
        b = COLORS["bold"]
        c = COLORS[self.color]
        r = COLORS["reset"]
        print(f"\n{self._prefix('▶')} {b}{c}[FASE {num}]{r} {msg}")

    def header(self, msg: str):
        b  = COLORS["bold"]
        c  = COLORS[self.color]
        r  = COLORS["reset"]
        ln = "─" * 60
        print(f"\n{c}{b}{ln}{r}")
        print(f"{c}{b}  {msg}{r}")
        print(f"{c}{b}{ln}{r}")

    def banner(self, msg: str):
        b  = COLORS["bold"]
        c  = COLORS["cyan"]
        r  = COLORS["reset"]
        ln = "═" * 64
        print(f"\n{c}{b}{ln}")
        print(f"  🤖  MULTI-AGENT BUILD SYSTEM")
        print(f"  {msg}")
        print(f"{ln}{r}\n")

    def complete(self, name: str, elapsed: float):
        g = COLORS["green"]
        b = COLORS["bold"]
        r = COLORS["reset"]
        print(f"\n{g}{b}  ✅ COMPLETADO: {name} ({elapsed}s){r}\n")

    def final_report(self, completed: int, failed: int, elapsed: float):
        g  = COLORS["green"]
        rd = COLORS["red"]
        b  = COLORS["bold"]
        r  = COLORS["reset"]
        c  = COLORS["cyan"]
        print(f"\n{c}{b}{'═' * 64}")
        print(f"  📊 REPORTE FINAL")
        print(f"{'═' * 64}{r}")
        print(f"  {g}{b}✅ Completados: {completed}{r}")
        if failed:
            print(f"  {rd}{b}❌ Fallidos:    {failed}{r}")
        print(f"  ⏱  Tiempo total: {elapsed}s")
        print(f"  📁 Output: ./output/")
        print(f"{c}{b}{'═' * 64}{r}\n")
