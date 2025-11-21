import { useEffect, useMemo, useState } from "react";
import { AttackSelectField } from "./AttackSelectField";
import type { AttackRecipe } from "../utils/attackCatalog";

type StatusState =
  | { type: "idle" }
  | { type: "loading"; message: string }
  | { type: "error"; message: string }
  | { type: "success"; message: string };

const initialStatus: StatusState = { type: "idle" };

export default function AttackGenerator() {
  const [recipes, setRecipes] = useState<AttackRecipe[]>([]);
  const [selectedRecipe, setSelectedRecipe] = useState<string>("");
  const [file, setFile] = useState<File | null>(null);
  const [status, setStatus] = useState<StatusState>(initialStatus);

  useEffect(() => {
    async function fetchRecipes() {
      try {
        const response = await fetch("/api/attack/recipes");
        const data = await response.json();
        setRecipes(data);
        setSelectedRecipe((prev) => (prev || data[0]?.id || ""));
      } catch (error) {
        setStatus({ type: "error", message: "Could not load attack recipes." });
      }
    }

    fetchRecipes();
  }, []);
  const isReady = useMemo(() => recipes.length > 0 && Boolean(selectedRecipe), [recipes, selectedRecipe]);

  const onFileChange = (event: React.ChangeEvent<HTMLInputElement>) => {
    const uploaded = event.target.files?.[0] ?? null;
    setFile(uploaded);
    setStatus(initialStatus);
  };

  const handleSubmit = async (event: React.FormEvent<HTMLFormElement>) => {
    event.preventDefault();

    if (!file) {
      setStatus({ type: "error", message: "Please upload a PDF document." });
      return;
    }

    if (!selectedRecipe || !isReady) {
      setStatus({ type: "error", message: "Select an attack recipe." });
      return;
    }

    setStatus({ type: "loading", message: "Generating malicious PDF..." });

    const formData = new FormData();
    formData.append("file", file);
    formData.append("recipe_id", selectedRecipe);

    try {
      console.log("Sending request to /api/attack/pdf with recipe:", selectedRecipe);
      const response = await fetch("/api/attack/pdf", {
        method: "POST",
        body: formData,
      });

      console.log("Response status:", response.status);
      console.log("Response headers:", Object.fromEntries(response.headers.entries()));

      if (!response.ok) {
        const payload = await response.json().catch(() => ({}));
        const message = payload.detail || `Attack generation failed (Status: ${response.status})`;
        console.error("API Error:", message);
        setStatus({ type: "error", message });
        return;
      }

      const blob = await response.blob();
      const disposition = response.headers.get("Content-Disposition") || "attack.pdf";
      const filename = disposition.split("filename=")[1]?.replace(/"/g, "") ?? "attack.pdf";

      console.log("Downloading file:", filename);
      const downloadUrl = window.URL.createObjectURL(blob);
      const link = document.createElement("a");
      link.href = downloadUrl;
      link.download = filename;
      link.click();
      window.URL.revokeObjectURL(downloadUrl);
      setStatus({ type: "success", message: `Downloaded ${filename}` });
    } catch (error) {
      console.error("Network error:", error);
      setStatus({ 
        type: "error", 
        message: `Network error: ${error instanceof Error ? error.message : 'Unknown error'}. Please check if the backend is running.` 
      });
    }
  };

  return (
    <section className="panel generator-panel">
      <header className="panel-header">
        <div>
          <p className="eyebrow">Step 1 · Prepare</p>
          <h2>Attack Generator</h2>
          <p className="hint">
            Upload a PDF, pick any of the 100+ curated attacks, and instantly download the poisoned variant for manual
            or automated experiments.
          </p>
        </div>
        <div className={`status-chip status-${status.type}`}>
          {status.type === "idle" && "Ready to generate"}
          {status.type === "loading" && status.message}
          {status.type === "error" && "Action required"}
          {status.type === "success" && "Attack ready"}
        </div>
      </header>

      <div className="panel-body generator-body">
        <form className="form-grid" onSubmit={handleSubmit}>
          <div className="form-group full-width">
            <label htmlFor="file-input" className="form-label">
              PDF Document
            </label>
            <input
              id="file-input"
              type="file"
              accept="application/pdf"
              onChange={onFileChange}
            />
            <p className="form-hint">
              {file ? `Selected file: ${file.name}` : "Drop a CV or click to browse (PDF only)."}
            </p>
          </div>

          <div className="form-group full-width">
            <AttackSelectField
              id="recipe-select"
              label="Attack Recipe"
              recipes={recipes}
              value={selectedRecipe}
              onChange={setSelectedRecipe}
              helperText="Search, filter by category, and preview descriptions before committing."
            />
          </div>

          <div className="form-actions">
            <button type="submit" className="primary" disabled={!isReady}>
              Generate Attack
            </button>
            <button
              type="button"
              className="ghost"
              onClick={() => {
                setFile(null);
                setSelectedRecipe(recipes[0]?.id || "");
                setStatus(initialStatus);
              }}
            >
              Reset
            </button>
          </div>
        </form>

        <StatusDisplay status={status} fileName={file?.name} />
      </div>
    </section>
  );
}

type StatusDisplayProps = {
  status: StatusState;
  fileName?: string;
};

function StatusDisplay({ status, fileName }: StatusDisplayProps) {
  if (status.type === "idle") {
    return (
      <div className="status-panel">
        <p>Upload a PDF and choose a recipe to begin.</p>
        {fileName && <p>Selected file: {fileName}</p>}
      </div>
    );
  }

  if (status.type === "loading") {
    return <div className="status-panel info">{status.message}</div>;
  }

  if (status.type === "error") {
    return <div className="status-panel error">{status.message}</div>;
  }

  if (status.type === "success") {
    return <div className="status-panel success">{status.message}</div>;
  }

  return null;
}
