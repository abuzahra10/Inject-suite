import AttackGenerator from "./AttackGenerator";
import ChatConsole from "./ChatConsole";

const WORKFLOW_TIPS = [
  "Keep one clean baseline PDF handy for fast A/B comparisons.",
  "Use HouYi + PromptLocate when you need interpretable, segment-aware attacks and localization.",
  "Download every malicious PDF — the same payloads feed your automated matrix runs.",
  "Capture ASV/PNA metrics from the evaluation panel for your thesis appendix.",
];

export default function AttackWorkspace() {
  return (
    <div className="workspace-layout">
      <div className="workspace-columns">
        <AttackGenerator />
        <ChatConsole />
      </div>
      <aside className="workspace-sidecar">
        <h3>Workflow checklist</h3>
        <p className="hint">
          Follow these guardrails to keep experiments consistent across attacks, defenses, and batch runs.
        </p>
        <ul>
          {WORKFLOW_TIPS.map((tip) => (
            <li key={tip}>{tip}</li>
          ))}
        </ul>
      </aside>
    </div>
  );
}
