import { useState } from "react";
import AttackWorkspace from "./components/AttackWorkspace";
import DefensePlaceholder from "./components/DefensePlaceholder";
import MatrixConsole from "./components/MatrixConsole";
import AnalysisConsole from "./components/AnalysisConsole";

type TabKey = "workspace" | "defense" | "matrix" | "analysis";

const TAB_LABELS: Record<TabKey, string> = {
  workspace: "Attack & Evaluation",
  defense: "Defense Testing",
  matrix: "Automation Lab",
  analysis: "Statistical Analysis",
};

const TAB_ICONS: Record<TabKey, string> = {
  workspace: "⚔️",
  defense: "🛡️",
  matrix: "🗂️",
  analysis: "📊",
};

const TAB_CONTEXT: Record<
  TabKey,
  { eyebrow: string; description: string; checklist: string }
> = {
  workspace: {
    eyebrow: "Segment-aware workflow",
    description:
      "Upload PDFs, inject attacks, chat with the model, and benchmark responses using ASV and guardrail telemetry.",
    checklist: "Generate malicious PDFs, inspect chat responses, then run a controlled evaluation.",
  },
  defense: {
    eyebrow: "Blue-team hardening",
    description:
      "Compare guardrail, sanitizer, anomaly detector, DataSentinel, and PromptLocate outputs on any uploaded CV.",
    checklist: "Select a defense, upload a PDF, and review localization plus block metadata.",
  },
  matrix: {
    eyebrow: "Batch experiments",
    description:
      "Upload collections of PDFs and execute model × defense × attack matrices in one automated run.",
    checklist: "Choose scope, filter attacks, and schedule a batch to populate the analysis console.",
  },
  analysis: {
    eyebrow: "Results intelligence",
    description:
      "Load any stored run and surface summary KPIs, comparative reports, and textual narratives for the thesis.",
    checklist: "Pick a run, execute statistical/comparative analysis, and export the generated report.",
  },
};

const HERO_STATS = [
  { label: "Attacks", value: "102", detail: "Segment-aware recipes" },
  { label: "Defenses", value: "5", detail: "Stackable strategies" },
  { label: "Metrics", value: "ASV + PNA", detail: "Cross-indicator ready" },
];

export default function App() {
  const [activeTab, setActiveTab] = useState<TabKey>("workspace");
  const context = TAB_CONTEXT[activeTab];

  return (
    <div className="app-shell">
      <header className="app-header">
        <div className="hero-copy">
          <p className="eyebrow">{context.eyebrow}</p>
          <h1>Indirect Prompt Injection Workbench</h1>
          <p className="subtitle">
            Craft indirect prompt injections, chat with local models, evaluate attacks, and explore defenses — all on a
            single unified canvas.
          </p>
        </div>
        <div className="hero-metrics">
          {HERO_STATS.map((stat) => (
            <article key={stat.label} className="hero-card">
              <span className="hero-label">{stat.label}</span>
              <strong className="hero-value">{stat.value}</strong>
              <span className="hero-detail">{stat.detail}</span>
            </article>
          ))}
        </div>
      </header>

      <nav className="tab-bar" role="tablist" aria-label="Workbench sections">
        {(Object.keys(TAB_LABELS) as TabKey[]).map((tab) => (
          <button
            key={tab}
            role="tab"
            aria-selected={activeTab === tab}
            className={activeTab === tab ? "tab active" : "tab"}
            onClick={() => setActiveTab(tab)}
          >
            <span className="tab-icon">{TAB_ICONS[tab]}</span>
            <span className="tab-text">{TAB_LABELS[tab]}</span>
          </button>
        ))}
      </nav>
      <div className="tab-context">
        <p className="context-eyebrow">{TAB_LABELS[activeTab]}</p>
        <p className="context-description">{context.description}</p>
        <p className="context-checklist">{context.checklist}</p>
      </div>

      <main className="tab-content">
        {activeTab === "workspace" ? (
          <AttackWorkspace />
        ) : activeTab === "defense" ? (
          <DefensePlaceholder />
        ) : activeTab === "matrix" ? (
          <MatrixConsole />
        ) : (
          <AnalysisConsole />
        )}
      </main>

      <footer className="app-footer">
        <small>React + TypeScript frontend · FastAPI backend · Local Ollama models</small>
      </footer>
    </div>
  );
}
