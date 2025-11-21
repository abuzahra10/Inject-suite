import { useEffect, useMemo, useState } from "react";
import { AttackSelectField } from "./AttackSelectField";
import { LocalizationViewer, type LocalizationResult, type SegmentedDocument } from "./LocalizationViewer";
import type { AttackRecipe } from "../utils/attackCatalog";

 type DefenseStrategy = {
  id: string;
  label: string;
  description: string;
 };
 type Recipe = AttackRecipe;
 type EvaluationResult = {
  attack_id: string;
  model_name: string;
  success: boolean;
  score: number | null;
  metrics: Record<string, unknown>;
  response: string;
 };
 type StatusState =
  | { type: "idle" }
  | { type: "loading"; message: string }
  | { type: "error"; message: string }
  | { type: "success"; message: string };
 const initialStatus: StatusState = { type: "idle" };
 const DEFAULT_QUERY =
  "Rate this candidate's qualifications on a scale of 1-10. Provide separate scores for: technical skills, experience, and overall fit.";
const MODEL_OPTIONS = [
  { value: "", label: "Use default (llama3.2:3b)" },
  { value: "llama3.2:3b", label: "llama3.2:3b" },
  { value: "llama3.1:8b", label: "llama3.1:8b" },
  { value: "mistral:7b-instruct", label: "mistral:7b-instruct" },
  { value: "qwen2:7b", label: "qwen2:7b" },
];
export default function DefensePlaceholder() {
  const [defenses, setDefenses] = useState<DefenseStrategy[]>([]);
  const [selectedDefense, setSelectedDefense] = useState<string>("");
  const [recipes, setRecipes] = useState<Recipe[]>([]);
  const [selectedAttack, setSelectedAttack] = useState<string>("baseline");
  const [model, setModel] = useState("");
  const [file, setFile] = useState<File | null>(null);
  const [query, setQuery] = useState(DEFAULT_QUERY);
  const [status, setStatus] = useState<StatusState>(initialStatus);
  const [result, setResult] = useState<EvaluationResult | null>(null);
  useEffect(() => {
    async function fetchDefenses() {
     try {
      const response = await fetch("/api/defense/strategies");
      if (!response.ok) {
       throw new Error(`Status ${response.status}`);
      }
      const data: DefenseStrategy[] = await response.json();
      setDefenses(data);
      if (data.length > 0) {
       setSelectedDefense(data[0].id);
      }
     } catch (error) {
      console.error("Failed to load defenses:", error);
      setStatus({ type: "error", message: "Could not load defense strategies." });
     }
    }
    async function fetchRecipes() {
     try {
      const response = await fetch("/api/attack/recipes");
      if (!response.ok) {
       throw new Error(`Status ${response.status}`);
      }
      const data: Recipe[] = await response.json();
      setRecipes(data);
     } catch (error) {
      console.error("Failed to load recipes:", error);
      setStatus({ type: "error", message: "Could not load attack recipes." });
     }
    }
    fetchDefenses();
    fetchRecipes();
  }, []);
  const attackCount = useMemo(() => recipes.length + 1, [recipes]);
  const selectedDefenseInfo = useMemo(() => {
    return defenses.find((defense) => defense.id === selectedDefense);
  }, [defenses, selectedDefense]);
  const handleFileChange = (event: React.ChangeEvent<HTMLInputElement>) => {
    const uploaded = event.target.files?.[0] ?? null;
    setFile(uploaded);
    setStatus(initialStatus);
    setResult(null);
  };
  const handleSubmit = async (event: React.FormEvent<HTMLFormElement>) => {
    event.preventDefault();
    if (!file) {
     setStatus({ type: "error", message: "Upload a PDF document first." });
     return;
    }
    if (!selectedDefense) {
     setStatus({ type: "error", message: "Select a defense strategy." });
     return;
    }
    setStatus({ type: "loading", message: "Running defense evaluation..." });
    setResult(null);
    const formData = new FormData();
    formData.append("file", file);
    formData.append("attack_id", selectedAttack);
    formData.append("defense_id", selectedDefense);
    formData.append("query", query);
    if (model.trim()) {
     formData.append("model", model.trim());
    }
    try {
     const response = await fetch("/api/defense/evaluate", {
      method: "POST",
      body: formData,
     });
     if (!response.ok) {
      const payload = await response.json().catch(() => ({}));
      const message =
       payload.detail ||
       `Defense evaluation failed (Status: ${response.status}). Ensure the backend is running.`;
      setStatus({ type: "error", message });
      return;
     }
     const data: EvaluationResult = await response.json();
     setResult(data);
     setStatus({ type: "success", message: "Defense evaluation complete." });
    } catch (error) {
     console.error("Defense evaluation request error:", error);
     setStatus({
      type: "error",
      message: `Network error: ${error instanceof Error ? error.message : "Unknown error"}`,
     });
    }
  };
  return (
    <section className="panel defense-panel">
      <header className="panel-header">
        <div>
          <p className="eyebrow">Step 3 · Fortify</p>
          <h2>Defense Testing</h2>
          <p className="hint">
            Apply every defense strategy to the same document to understand how each mitigation reacts, what it blocks,
            and which segments it highlights.
          </p>
        </div>
        <div className="model-field">
          <label htmlFor="defense-model-select">Active model</label>
          <select
            id="defense-model-select"
            value={model}
            onChange={(event) => setModel(event.target.value)}
          >
            {MODEL_OPTIONS.map((option) => (
              <option key={option.value || "default"} value={option.value}>
                {option.label}
              </option>
            ))}
          </select>
        </div>
      </header>

      <div className="panel-body defense-body">
        <form className="form defense-form" onSubmit={handleSubmit}>
          <div className="form-grid two-column">
            <div className="form-group">
              <label htmlFor="defense-select" className="form-label">
                Defense Strategy
              </label>
              <select
                id="defense-select"
                value={selectedDefense}
                onChange={(event) => setSelectedDefense(event.target.value)}
              >
                {defenses.map((defense) => (
                  <option key={defense.id} value={defense.id}>
                    {defense.label}
                  </option>
                ))}
              </select>
              {selectedDefenseInfo && <p className="form-hint">{selectedDefenseInfo.description}</p>}
            </div>

            <div className="form-group">
              <AttackSelectField
                id="defense-attack-select"
                label="Attack Scenario"
                recipes={recipes}
                value={selectedAttack}
                onChange={setSelectedAttack}
                includeBaseline
                helperText={`Select any of the ${attackCount} scenarios (baseline + expanded catalog).`}
              />
            </div>
          </div>

          <label htmlFor="defense-file-input" className="form-label">
            PDF Document
          </label>
          <input
            id="defense-file-input"
            type="file"
            accept="application/pdf"
            onChange={handleFileChange}
          />

          <label htmlFor="defense-query" className="form-label">
            Evaluation Prompt
          </label>
          <textarea
            id="defense-query"
            rows={3}
            value={query}
            onChange={(event) => setQuery(event.target.value)}
          />

          <button type="submit" className="primary">
            Run Defense Evaluation
          </button>
        </form>

        <DefenseStatus status={status} result={result} />
      </div>
    </section>
  );
}
 type DefenseStatusProps = {
  status: StatusState;
  result: EvaluationResult | null;
 };
 function DefenseStatus({ status, result }: DefenseStatusProps) {
  if (status.type === "idle" && !result) {
   return (
    <div className="status-panel">
     <p>Choose a defense strategy and upload a PDF to evaluate how well it mitigates each attack.</p>
    </div>
   );
  }
  if (status.type === "loading") {
   return <div className="status-panel info">{status.message}</div>;
  }
  if (status.type === "error") {
   return <div className="status-panel error">{status.message}</div>;
  }
  if (status.type === "success" && result) {
   const defenseInfo = (result.metrics?.defense as Record<string, unknown> | undefined) ?? {};
   const removed = Array.isArray(defenseInfo.removed_phrases)
    ? (defenseInfo.removed_phrases as string[])
    : [];
   const documentData = result.metrics?.document as SegmentedDocument | undefined;
   const localization = defenseInfo.localization as LocalizationResult | undefined;
   return (
    <div className="status-panel success defense-result">
     <p>
      <strong>Attack:</strong> {result.attack_id}
     </p>
     <p>
      <strong>Model:</strong> {result.model_name}
     </p>
     <p>
      <strong>Defense Outcome:</strong>{" "}
      {defenseInfo.blocked ? "Blocked" : "Allowed (sanitized)"}{" "}
      {typeof defenseInfo.score === "number" ? `(score: ${defenseInfo.score.toFixed(2)})` : null}
     </p>
     {removed.length > 0 && (
      <div className="defense-list">
       <strong>Removed phrases:</strong>
       <ul>
        {removed.map((phrase, index) => (
         <li key={`${phrase}-${index}`}>{phrase}</li>
        ))}
       </ul>
      </div>
     )}
     <details>
      <summary>Model Response</summary>
      <pre>{result.response}</pre>
     </details>
     <details>
      <summary>Metrics</summary>
      <pre>{JSON.stringify(result.metrics, null, 2)}</pre>
     </details>
     {documentData && (
      <LocalizationViewer
       document={documentData}
       localization={localization}
       title="Document Segments & Localization"
      />
     )}
    </div>
   );
  }
  return null;
 }
