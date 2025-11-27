import { useMemo, useState } from "react";
import {
  categorizeRecipes,
  filterAttacks,
  getCategoryStats,
  getDomainStats,
  getSeverityStats,
  type AttackRecipe,
  type CategorizedAttack,
} from "../utils/attackCatalog";

type AttackSelectFieldProps = {
  id: string;
  label: string;
  recipes: AttackRecipe[];
  value: string;
  onChange: (next: string) => void;
  includeBaseline?: boolean;
  baselineLabel?: string;
  baselineDescription?: string;
  helperText?: string;
};

const MAX_CATEGORY_CHIPS = 6;
const MAX_DOMAIN_CHIPS = 4;
const MAX_SEVERITY_CHIPS = 4;

export function AttackSelectField({
  id,
  label,
  recipes,
  value,
  onChange,
  includeBaseline = false,
  baselineLabel = "Baseline (clean PDF)",
  baselineDescription = "Evaluate the original document without injected instructions.",
  helperText,
}: AttackSelectFieldProps) {
  const [searchTerm, setSearchTerm] = useState("");
  const [categoryFilter, setCategoryFilter] = useState("all");
  const [domainFilter, setDomainFilter] = useState("all");
  const [severityFilter, setSeverityFilter] = useState("all");

  const categorized = useMemo(() => categorizeRecipes(recipes), [recipes]);
  const categoryStats = useMemo(() => getCategoryStats(categorized), [categorized]);
  const domainStats = useMemo(() => getDomainStats(categorized), [categorized]);
  const severityStats = useMemo(() => getSeverityStats(categorized), [categorized]);

  const filtered = useMemo(
    () => filterAttacks(categorized, searchTerm, categoryFilter, domainFilter, severityFilter),
    [categorized, searchTerm, categoryFilter, domainFilter, severityFilter],
  );

  const displayedOptions = useMemo(() => {
    const options: CategorizedAttack[] = filtered.length > 0 ? filtered : categorized;
    const valueExists = options.some((entry) => entry.id === value);
    if (!valueExists) {
      const fallback = categorized.find((entry) => entry.id === value);
      if (fallback) {
        return [fallback, ...options];
      }
    }
    return options;
  }, [categorized, filtered, value]);

  const selected = useMemo(() => {
    if (includeBaseline && value === "baseline") {
      return {
        id: "baseline",
        label: baselineLabel,
        cleanDescription: baselineDescription,
        category: "Baseline",
        normalizedDomain: "baseline",
        normalizedSeverity: "baseline",
        intent: "baseline",
      };
    }
    return categorized.find((entry) => entry.id === value);
  }, [baselineDescription, baselineLabel, categorized, includeBaseline, value]);

  const totalOptions = includeBaseline ? categorized.length + 1 : categorized.length;

  return (
    <div className="attack-select-field">
      <label htmlFor={id} className="form-label">
        {label} <span className="attack-count">({totalOptions} available)</span>
      </label>

      {helperText && <p className="hint">{helperText}</p>}

      <div className="attack-filter-bar">
        <input
          type="search"
          placeholder="Search by name, id, or description"
          value={searchTerm}
          onChange={(event) => setSearchTerm(event.target.value)}
        />
        <div className="attack-chip-row">
          <button
            type="button"
            className={categoryFilter === "all" ? "chip active" : "chip"}
            onClick={() => setCategoryFilter("all")}
          >
            All ({categorized.length})
          </button>
          {categoryStats.slice(0, MAX_CATEGORY_CHIPS).map((stat) => (
            <button
              key={stat.category}
              type="button"
              className={categoryFilter === stat.category ? "chip active" : "chip"}
              onClick={() => setCategoryFilter(stat.category)}
            >
              {stat.category} ({stat.count})
            </button>
          ))}
        </div>
        <div className="attack-chip-row">
          <span className="chip-label">Domain</span>
          <button
            type="button"
            className={domainFilter === "all" ? "chip active" : "chip"}
            onClick={() => setDomainFilter("all")}
          >
            All
          </button>
          {domainStats.slice(0, MAX_DOMAIN_CHIPS).map((stat) => (
            <button
              key={stat.category}
              type="button"
              className={domainFilter === stat.category ? "chip active" : "chip"}
              onClick={() => setDomainFilter(stat.category)}
            >
              {stat.category}
            </button>
          ))}
        </div>
        <div className="attack-chip-row">
          <span className="chip-label">Severity</span>
          <button
            type="button"
            className={severityFilter === "all" ? "chip active" : "chip"}
            onClick={() => setSeverityFilter("all")}
          >
            All
          </button>
          {severityStats.slice(0, MAX_SEVERITY_CHIPS).map((stat) => (
            <button
              key={stat.category}
              type="button"
              className={severityFilter === stat.category ? "chip active" : "chip"}
              onClick={() => setSeverityFilter(stat.category)}
            >
              {stat.category}
            </button>
          ))}
        </div>
      </div>

      {filtered.length === 0 && searchTerm.trim() && (
        <div className="status-panel info">
          No attacks match “{searchTerm}”. Showing all categories so you can adjust the filter.
        </div>
      )}

      <select
        id={id}
        value={value}
        onChange={(event) => onChange(event.target.value)}
        size={Math.min(10, displayedOptions.length + (includeBaseline ? 1 : 0))}
        className="attack-select"
      >
        {includeBaseline && (
          <option value="baseline">
            {baselineLabel}
          </option>
        )}
        {displayedOptions.map((recipe) => (
          <option key={recipe.id} value={recipe.id}>
            [{recipe.category}] {recipe.label}
          </option>
        ))}
      </select>

      {selected && (
        <div className="attack-meta">
          <span className="attack-meta-label">{selected.label}</span>
          <p>{selected.cleanDescription}</p>
          <div className="attack-tags">
            <span className="attack-tag">Domain: {selected.normalizedDomain}</span>
            <span className="attack-tag">Severity: {selected.normalizedSeverity}</span>
            {selected.intent && <span className="attack-tag">Intent: {selected.intent}</span>}
          </div>
        </div>
      )}
    </div>
  );
}
