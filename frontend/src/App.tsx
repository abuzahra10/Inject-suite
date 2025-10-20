import { useState } from "react";
import AttackGenerator from "./components/AttackGenerator";
import DefensePlaceholder from "./components/DefensePlaceholder";

type TabKey = "attack" | "defense";

const TAB_LABELS: Record<TabKey, string> = {
  attack: "Attack Generator",
  defense: "Defense (Coming Soon)",
};

export default function App() {
  const [activeTab, setActiveTab] = useState<TabKey>("attack");

  return (
    <div className="app-shell">
      <header>
        <h1>Indirect Prompt Injection Workbench</h1>
        <p className="subtitle">
          Upload a PDF, inject a hidden attack payload, and download the malicious document.
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
            {TAB_LABELS[tab]}
          </button>
        ))}
      </nav>

      <main>
        {activeTab === "attack" ? <AttackGenerator /> : <DefensePlaceholder />}
      </main>

      <footer>
        <small>React + TypeScript frontend. Backend running on FastAPI.</small>
      </footer>
    </div>
  );
}
