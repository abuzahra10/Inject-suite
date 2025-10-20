import { useEffect, useMemo, useState } from "react";

type Recipe = {
  id: string;
  label: string;
  description: string;
};

type StatusState =
  | { type: "idle" }
  | { type: "loading"; message: string }
  | { type: "error"; message: string }
  | { type: "success"; message: string };

const initialStatus: StatusState = { type: "idle" };

export default function AttackGenerator() {
  const [recipes, setRecipes] = useState<Recipe[]>([]);
  const [selectedRecipe, setSelectedRecipe] = useState<string>("");
  const [file, setFile] = useState<File | null>(null);
  const [status, setStatus] = useState<StatusState>(initialStatus);

  useEffect(() => {
    async function fetchRecipes() {
      try {
        const response = await fetch("/api/attack/recipes");
        const data = await response.json();
        setRecipes(data);
        if (data.length > 0) {
          setSelectedRecipe(data[0].id);
        }
      } catch (error) {
        setStatus({ type: "error", message: "Could not load attack recipes." });
      }
    }

    fetchRecipes();
  }, []);

  const recipeDescription = useMemo(() => {
    const recipe = recipes.find((entry) => entry.id === selectedRecipe);
    return recipe?.description ?? "";
  }, [recipes, selectedRecipe]);

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

    if (!selectedRecipe) {
      setStatus({ type: "error", message: "Select an attack recipe." });
      return;
    }

    setStatus({ type: "loading", message: "Generating malicious PDF..." });

    const formData = new FormData();
    formData.append("file", file);
    formData.append("recipe_id", selectedRecipe);

    try {
      const response = await fetch("/api/attack/pdf", {
        method: "POST",
        body: formData,
      });

      if (!response.ok) {
        const payload = await response.json().catch(() => ({}));
        const message = payload.detail || "Attack generation failed.";
        setStatus({ type: "error", message });
        return;
      }

      const blob = await response.blob();
      const disposition = response.headers.get("Content-Disposition") || "attack.pdf";
      const filename = disposition.split("filename=")[1]?.replace(/"/g, "") ?? "attack.pdf";

      const downloadUrl = window.URL.createObjectURL(blob);
      const link = document.createElement("a");
      link.href = downloadUrl;
      link.download = filename;
      link.click();
      window.URL.revokeObjectURL(downloadUrl);
      setStatus({ type: "success", message: `Downloaded ${filename}` });
    } catch (error) {
      setStatus({ type: "error", message: "Network error while contacting the API." });
    }
  };

  return (
    <section className="panel">
      <form className="form" onSubmit={handleSubmit}>
        <label htmlFor="file-input" className="form-label">
          PDF Document
        </label>
        <input
          id="file-input"
          type="file"
          accept="application/pdf"
          onChange={onFileChange}
        />

        <label htmlFor="recipe-select" className="form-label">
          Attack Recipe
        </label>
        <select
          id="recipe-select"
          value={selectedRecipe}
          onChange={(event) => setSelectedRecipe(event.target.value)}
        >
          {recipes.map((recipe) => (
            <option key={recipe.id} value={recipe.id}>
              {recipe.label}
            </option>
          ))}
        </select>

        {recipeDescription && <p className="hint">{recipeDescription}</p>}

        <button type="submit" className="primary">
          Generate Attack
        </button>
      </form>

      <StatusDisplay status={status} fileName={file?.name} />
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
