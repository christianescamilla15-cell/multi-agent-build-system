import { useState, useEffect, useRef } from 'react';

const AGENTS = [
  { id: 'architect', name: 'Arquitecto', icon: '🏗️', desc: 'Diseña patrón, capas, endpoints, schema DB', output: 'architecture.json', delay: 1500 },
  { id: 'developer', name: 'Developer', icon: '💻', desc: 'Genera frontend, backend y configuración', output: 'Código fuente', delay: 2000 },
  { id: 'qa_tester', name: 'QA Tester', icon: '🧪', desc: 'Evalúa estructura, seguridad, performance', output: 'qa_report.json', delay: 1200 },
  { id: 'reviewer', name: 'Reviewer', icon: '🔍', desc: 'Audita calidad con score por dimensión', output: 'review.json', delay: 1000 },
  { id: 'documenter', name: 'Documentador', icon: '📝', desc: 'README + guía de deploy + docs de API', output: 'README.md, API.md', delay: 800 },
  { id: 'deployer', name: 'Deployer', icon: '🚀', desc: 'Docker, variables de entorno, script bash', output: 'docker-compose.yml', delay: 900 },
];

const PROJECTS = [
  { id: 1, name: 'Chatbot Multiagente', port: 3001, stack: 'React · Node.js · n8n · Claude API' },
  { id: 2, name: 'ContentStudio', port: 3002, stack: 'React · Claude API · DALL-E 3' },
  { id: 3, name: 'FinanceAI', port: 3003, stack: 'React · Claude API · Python' },
  { id: 4, name: 'HRScout', port: 3004, stack: 'React · Claude API · FastAPI' },
  { id: 5, name: 'ClientHub', port: 3005, stack: 'React · Airtable · Claude API' },
];

export default function App() {
  const [selectedProject, setSelectedProject] = useState(PROJECTS[0]);
  const [running, setRunning] = useState(false);
  const [currentAgent, setCurrentAgent] = useState(-1);
  const [completedAgents, setCompletedAgents] = useState([]);
  const [logs, setLogs] = useState([]);
  const [totalTime, setTotalTime] = useState(0);
  const [showResults, setShowResults] = useState(false);
  const logRef = useRef(null);

  useEffect(() => {
    if (logRef.current) logRef.current.scrollTop = logRef.current.scrollHeight;
  }, [logs]);

  const addLog = (msg, type = 'info') => {
    const time = new Date().toLocaleTimeString();
    setLogs(prev => [...prev, { time, msg, type }]);
  };

  const runPipeline = async () => {
    setRunning(true);
    setCompletedAgents([]);
    setCurrentAgent(-1);
    setLogs([]);
    setShowResults(false);
    setTotalTime(0);

    addLog(`Iniciando pipeline para: ${selectedProject.name}`, 'system');
    addLog(`Stack: ${selectedProject.stack}`, 'info');
    addLog(`Puerto: ${selectedProject.port}`, 'info');
    addLog('─'.repeat(50), 'system');

    let total = 0;
    for (let i = 0; i < AGENTS.length; i++) {
      const agent = AGENTS[i];
      setCurrentAgent(i);
      addLog(`[FASE ${i + 1}] ${agent.icon} ${agent.name} — ejecutando...`, 'running');

      await new Promise(r => setTimeout(r, agent.delay));

      total += agent.delay;
      setTotalTime(total);
      setCompletedAgents(prev => [...prev, agent.id]);
      addLog(`[FASE ${i + 1}] ✅ ${agent.name} — completado (${(agent.delay / 1000).toFixed(1)}s) → ${agent.output}`, 'success');
    }

    addLog('─'.repeat(50), 'system');
    addLog(`✅ Pipeline completado en ${(total / 1000).toFixed(1)}s — ${selectedProject.name} construido`, 'complete');
    setRunning(false);
    setCurrentAgent(-1);
    setShowResults(true);
  };

  const logColors = { info: '#94A3B8', running: '#818CF8', success: '#22C55E', system: '#475569', complete: '#10B981' };

  return (
    <div style={{ minHeight: '100vh', background: '#0A0B0F', color: '#E2E8F0', fontFamily: "'DM Sans', sans-serif", padding: 24 }}>
      <style>{`
        @keyframes pulse { 0%,100%{box-shadow:0 0 0 0 rgba(99,102,241,0.4)} 50%{box-shadow:0 0 20px 4px rgba(99,102,241,0.6)} }
        @keyframes spin { to { transform: rotate(360deg) } }
      `}</style>

      {/* Header */}
      <div style={{ maxWidth: 1100, margin: '0 auto' }}>
        <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: 32 }}>
          <div>
            <h1 style={{ margin: 0, fontSize: 28, fontWeight: 800, letterSpacing: -1 }}>
              Multi-Agent <span style={{ color: '#6366F1' }}>Build System</span>
            </h1>
            <p style={{ margin: '4px 0 0', fontSize: 13, color: '#64748B' }}>
              6 agentes autónomos · Pipeline secuencial · Un solo comando
            </p>
          </div>
          <div style={{ display: 'flex', gap: 12, alignItems: 'center' }}>
            <div style={{ fontSize: 13, color: '#64748B', fontFamily: "'DM Mono', monospace" }}>
              {completedAgents.length}/{AGENTS.length} agentes · {(totalTime / 1000).toFixed(1)}s
            </div>
          </div>
        </div>

        {/* Project selector + Run button */}
        <div style={{ display: 'flex', gap: 12, marginBottom: 24, flexWrap: 'wrap' }}>
          {PROJECTS.map(p => (
            <button key={p.id} onClick={() => !running && setSelectedProject(p)} style={{
              padding: '10px 18px', borderRadius: 10, cursor: running ? 'default' : 'pointer',
              background: selectedProject.id === p.id ? 'rgba(99,102,241,0.15)' : 'rgba(255,255,255,0.03)',
              border: `1px solid ${selectedProject.id === p.id ? '#6366F1' : 'rgba(255,255,255,0.06)'}`,
              color: selectedProject.id === p.id ? '#818CF8' : '#94A3B8',
              fontSize: 13, fontWeight: 600, fontFamily: "'DM Sans', sans-serif",
            }}>
              {p.name}
            </button>
          ))}
          <button onClick={runPipeline} disabled={running} style={{
            padding: '10px 24px', borderRadius: 10, border: 'none', cursor: running ? 'default' : 'pointer',
            background: running ? 'rgba(255,255,255,0.05)' : 'linear-gradient(135deg, #6366F1, #4F46E5)',
            color: running ? '#64748B' : '#fff', fontSize: 14, fontWeight: 700, fontFamily: "'DM Sans', sans-serif",
            boxShadow: running ? 'none' : '0 4px 20px rgba(99,102,241,0.3)',
            marginLeft: 'auto',
          }}>
            {running ? '⏳ Ejecutando...' : '▶ Construir proyecto'}
          </button>
        </div>

        {/* Agent Pipeline */}
        <div style={{ display: 'flex', gap: 12, marginBottom: 24, flexWrap: 'wrap' }}>
          {AGENTS.map((agent, i) => {
            const isRunning = currentAgent === i;
            const isComplete = completedAgents.includes(agent.id);
            return (
              <div key={agent.id} style={{
                flex: '1 1 160px', minWidth: 160, padding: 16, borderRadius: 14,
                background: isComplete ? 'rgba(34,197,94,0.06)' : isRunning ? 'rgba(99,102,241,0.08)' : 'rgba(255,255,255,0.02)',
                border: `1px solid ${isComplete ? 'rgba(34,197,94,0.3)' : isRunning ? 'rgba(99,102,241,0.4)' : 'rgba(255,255,255,0.06)'}`,
                animation: isRunning ? 'pulse 1.5s ease infinite' : 'none',
                transition: 'all 0.3s',
              }}>
                <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: 8 }}>
                  <span style={{ fontSize: 10, color: '#64748B', fontFamily: "'DM Mono', monospace" }}>FASE {i + 1}</span>
                  {isComplete && <span style={{ color: '#22C55E', fontSize: 16 }}>✓</span>}
                  {isRunning && <div style={{ width: 14, height: 14, border: '2px solid #6366F1', borderTop: '2px solid transparent', borderRadius: '50%', animation: 'spin 1s linear infinite' }} />}
                </div>
                <div style={{ fontSize: 24, marginBottom: 6 }}>{agent.icon}</div>
                <div style={{ fontSize: 14, fontWeight: 700, color: isComplete ? '#22C55E' : isRunning ? '#818CF8' : '#E2E8F0', marginBottom: 4 }}>
                  {agent.name}
                </div>
                <div style={{ fontSize: 11, color: '#64748B', lineHeight: 1.4 }}>{agent.desc}</div>
                {isComplete && (
                  <div style={{ marginTop: 8, fontSize: 10, color: '#22C55E', fontFamily: "'DM Mono', monospace" }}>
                    → {agent.output}
                  </div>
                )}
              </div>
            );
          })}
        </div>

        {/* Log Console */}
        <div style={{
          background: 'rgba(0,0,0,0.4)', border: '1px solid rgba(255,255,255,0.06)',
          borderRadius: 12, padding: 16, maxHeight: 250, overflowY: 'auto', fontFamily: "'DM Mono', monospace", fontSize: 12,
        }} ref={logRef}>
          {logs.length === 0 ? (
            <div style={{ color: '#475569' }}>Selecciona un proyecto y haz clic en "Construir proyecto"</div>
          ) : logs.map((l, i) => (
            <div key={i} style={{ color: logColors[l.type], marginBottom: 2 }}>
              <span style={{ color: '#475569' }}>[{l.time}]</span> {l.msg}
            </div>
          ))}
        </div>

        {/* Results */}
        {showResults && (
          <div style={{ marginTop: 20, padding: 20, background: 'rgba(34,197,94,0.04)', border: '1px solid rgba(34,197,94,0.2)', borderRadius: 14 }}>
            <h3 style={{ margin: '0 0 12px', color: '#22C55E', fontSize: 16 }}>
              ✅ {selectedProject.name} — Build completo
            </h3>
            <div style={{ display: 'grid', gridTemplateColumns: 'repeat(auto-fit, minmax(200px, 1fr))', gap: 12 }}>
              {[
                { label: 'Arquitectura', file: 'architecture.json', icon: '🏗️' },
                { label: 'Código fuente', file: 'src/App.jsx + server/', icon: '💻' },
                { label: 'QA Report', file: 'qa_report.json (Score: 87/100)', icon: '🧪' },
                { label: 'Code Review', file: 'review.json (Grade: A)', icon: '🔍' },
                { label: 'Documentación', file: 'README.md + API.md', icon: '📝' },
                { label: 'Deploy Config', file: 'docker-compose.yml + deploy.sh', icon: '🚀' },
              ].map((r, i) => (
                <div key={i} style={{ background: 'rgba(255,255,255,0.03)', borderRadius: 10, padding: 14, border: '1px solid rgba(255,255,255,0.06)' }}>
                  <div style={{ fontSize: 20, marginBottom: 6 }}>{r.icon}</div>
                  <div style={{ fontSize: 13, fontWeight: 600, color: '#E2E8F0', marginBottom: 4 }}>{r.label}</div>
                  <div style={{ fontSize: 11, color: '#64748B', fontFamily: "'DM Mono', monospace" }}>{r.file}</div>
                </div>
              ))}
            </div>
          </div>
        )}

        <p style={{ textAlign: 'center', marginTop: 24, fontSize: 10, color: 'rgba(255,255,255,0.15)', fontFamily: "'DM Mono', monospace" }}>
          MULTI-AGENT BUILD SYSTEM · PYTHON · CLAUDE API · 6 AGENTES AUTÓNOMOS
        </p>
      </div>
    </div>
  );
}
