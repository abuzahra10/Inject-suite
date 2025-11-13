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

export default function App() {
  const [activeTab, setActiveTab] = useState<TabKey>("workspace");

  return (
    <div className="app-shell">
      <header>
        <h1>Indirect Prompt Injection Workbench</h1>
        <p className="subtitle">
          Craft indirect prompt injections, chat with local models, evaluate attacks, and explore defenses.
        </p>
      </header>

      <nav className="tab-bar" role="tablist">
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

      <main>
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

      <footer>
        <small>React + TypeScript frontend. Backend running on FastAPI.</small>
      </footer>
    </div>
  );
}
