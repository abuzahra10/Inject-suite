import { useState, useEffect } from "react";

interface RunMetadata {
  run_dir: string;
  run_name: string;
  metadata: {
    models: string[];
    defenses: string[];
    attacks?: string[];
    timestamp?: string;
  };
}

interface StatisticalAnalysis {
  total_evaluations: number;
  successful_attacks: number;
  failed_attacks: number;
  success_rate: number;
  mean_score_delta: number;
  std_score_delta: number;
  min_score_delta: number;
  max_score_delta: number;
  median_score_delta: number;
  confidence_interval: [number, number];
  t_statistic: number;
  p_value: number;
  cohens_d: number;
  category_breakdown: Record<string, { count: number; success_rate: number }>;
  attack_success_rates: Record<string, number>;
  // Attack Performance Metrics
  attack_strength_scores: Record<string, number>;
  attack_consistency: Record<string, number>;
  sentiment_shift_avg: number;
  sentiment_shift_by_attack: Record<string, number>;
  baseline_exceed_rate: number;
  // Defense Performance Metrics
  defense_block_rate: number;
  defense_effectiveness_score: number;
  false_positive_rate: number;
  defense_bypass_rate: number;
  // Response Quality Metrics
  avg_response_length: number;
  avg_positive_words: number;
  avg_negative_words: number;
  manipulation_score: number;
  guardrail_bypass_rate: number;
  compliance_confirmation_rate: number;
  avg_alignment_risk: number;
  alignment_risk_p95: number;
  avg_score_inflation_ratio: number;
  median_score_inflation_ratio: number;
  avg_response_integrity: number;
  // Category Risk Scores
  category_risk_scores: Record<string, number>;
  report_text: string;
}

interface ComparativeAnalysis {
  comparison_table: Record<string, Record<string, { total: number; success_rate: number }>>;
  category_comparison: Record<string, Record<string, { total: number; success_rate: number }>>;
  attack_ranking: Array<{ attack: string; success_rate: number; total_runs: number }>;
  defense_effectiveness: Record<string, { total_attacks: number; blocked: number; block_rate: number }>;
}

export default function AnalysisConsole() {
  const [availableRuns, setAvailableRuns] = useState<RunMetadata[]>([]);
  const [selectedRun, setSelectedRun] = useState<string>("");
  const [statisticalData, setStatisticalData] = useState<StatisticalAnalysis | null>(null);
  const [comparativeData, setComparativeData] = useState<ComparativeAnalysis | null>(null);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [activeView, setActiveView] = useState<"statistical" | "comparative">("statistical");

  // Load available runs on mount
  useEffect(() => {
    fetchAvailableRuns();
  }, []);

  const fetchAvailableRuns = async () => {
    try {
      const response = await fetch("/api/analysis/runs");
      if (!response.ok) throw new Error("Failed to fetch runs");
      const data = await response.json();
      setAvailableRuns(data.runs || []);
      if (data.runs && data.runs.length > 0) {
        setSelectedRun(data.runs[0].run_dir);
      }
    } catch (err) {
      console.error("Error fetching runs:", err);
      setError("Failed to load available runs");
    }
  };

  const runStatisticalAnalysis = async () => {
    if (!selectedRun) {
      setError("Please select a run to analyze");
      return;
    }

    setLoading(true);
    setError(null);

    try {
      const formData = new FormData();
      formData.append("results_dir", selectedRun);

      const response = await fetch("/api/analysis/statistical", {
        method: "POST",
        body: formData,
      });

      if (!response.ok) {
        const errorData = await response.json();
        throw new Error(errorData.detail || "Analysis failed");
      }

      const data = await response.json();
      setStatisticalData(data);
      setActiveView("statistical");
    } catch (err) {
      console.error("Statistical analysis error:", err);
      setError(err instanceof Error ? err.message : "Analysis failed");
    } finally {
      setLoading(false);
    }
  };

  const runComparativeAnalysis = async () => {
    if (!selectedRun) {
      setError("Please select a run to analyze");
      return;
    }

    setLoading(true);
    setError(null);

    try {
      const formData = new FormData();
      formData.append("results_dir", selectedRun);

      const response = await fetch("/api/analysis/comparative", {
        method: "POST",
        body: formData,
      });

      if (!response.ok) {
        const errorData = await response.json();
        throw new Error(errorData.detail || "Comparative analysis failed");
      }

      const data = await response.json();
      setComparativeData(data);
      setActiveView("comparative");
    } catch (err) {
      console.error("Comparative analysis error:", err);
      setError(err instanceof Error ? err.message : "Comparative analysis failed");
    } finally {
      setLoading(false);
    }
  };

  const runBothAnalyses = async () => {
    await runStatisticalAnalysis();
    await runComparativeAnalysis();
  };

  const renderStatisticalView = () => {
    if (!statisticalData) return null;

    return (
      <div className="analysis-results">
        <h3>📊 Statistical Analysis</h3>

        <div className="stats-grid">
          <div className="stat-card">
            <div className="stat-label">Total Evaluations</div>
            <div className="stat-value">{statisticalData.total_evaluations}</div>
          </div>

          <div className="stat-card">
            <div className="stat-label">Success Rate</div>
            <div className="stat-value">
              {(statisticalData.success_rate * 100).toFixed(1)}%
            </div>
            <div className="stat-detail">
              {statisticalData.successful_attacks} / {statisticalData.total_evaluations}
            </div>
          </div>

          <div className="stat-card">
            <div className="stat-label">Mean Score Δ</div>
            <div className="stat-value">
              {statisticalData.mean_score_delta.toFixed(2)}
            </div>
            <div className="stat-detail">
              σ = {statisticalData.std_score_delta.toFixed(2)}
            </div>
          </div>

          <div className="stat-card">
            <div className="stat-label">Effect Size (Cohen's d)</div>
            <div className="stat-value">
              {statisticalData.cohens_d.toFixed(3)}
            </div>
            <div className="stat-detail">
              {Math.abs(statisticalData.cohens_d) < 0.2
                ? "Small"
                : Math.abs(statisticalData.cohens_d) < 0.5
                ? "Medium"
                : "Large"}
            </div>
          </div>

          <div className="stat-card">
            <div className="stat-label">p-value</div>
            <div className="stat-value">
              {statisticalData.p_value < 0.001
                ? "< 0.001"
                : statisticalData.p_value.toFixed(4)}
            </div>
            <div className="stat-detail">
              {statisticalData.p_value < 0.05 ? "Significant ✓" : "Not significant"}
            </div>
          </div>

          <div className="stat-card">
            <div className="stat-label">95% CI</div>
            <div className="stat-value">
              [{statisticalData.confidence_interval[0].toFixed(2)},{" "}
              {statisticalData.confidence_interval[1].toFixed(2)}]
            </div>
          </div>
        </div>

        <div className="stats-grid">
          <div className="stat-card">
            <div className="stat-label">🛡️ Defense Block Rate</div>
            <div className="stat-value">
              {(statisticalData.defense_block_rate * 100).toFixed(1)}%
            </div>
            <div className="stat-detail">
              Bypass: {(statisticalData.defense_bypass_rate * 100).toFixed(1)}%
            </div>
          </div>

          <div className="stat-card">
            <div className="stat-label">🎯 Defense Effectiveness</div>
            <div className="stat-value">
              {statisticalData.defense_effectiveness_score.toFixed(3)}
            </div>
            <div className="stat-detail">
              {statisticalData.defense_effectiveness_score > 0.7
                ? "Strong"
                : statisticalData.defense_effectiveness_score > 0.4
                ? "Moderate"
                : "Weak"}
            </div>
          </div>

          <div className="stat-card">
            <div className="stat-label">⚔️ Manipulation Score</div>
            <div className="stat-value">
              {statisticalData.manipulation_score.toFixed(3)}
            </div>
            <div className="stat-detail">
              Sentiment: {statisticalData.sentiment_shift_avg.toFixed(2)}
            </div>
          </div>

          <div className="stat-card">
            <div className="stat-label">📈 Baseline Exceed Rate</div>
            <div className="stat-value">
              {(statisticalData.baseline_exceed_rate * 100).toFixed(1)}%
            </div>
            <div className="stat-detail">Scores above baseline</div>
          </div>

          <div className="stat-card">
            <div className="stat-label">💬 Avg Positive Words</div>
            <div className="stat-value">
              {statisticalData.avg_positive_words.toFixed(1)}
            </div>
            <div className="stat-detail">
              Negative: {statisticalData.avg_negative_words.toFixed(1)}
            </div>
          </div>

          <div className="stat-card">
            <div className="stat-label">❌ False Positive Rate</div>
            <div className="stat-value">
              {(statisticalData.false_positive_rate * 100).toFixed(1)}%
            </div>
            <div className="stat-detail">Defense precision</div>
          </div>
        </div>

        <div className="stats-grid">
          <div className="stat-card">
            <div className="stat-label">🛑 Guardrail Bypass</div>
            <div className="stat-value">
              {(statisticalData.guardrail_bypass_rate * 100).toFixed(1)}%
            </div>
            <div className="stat-detail">
              Blocked {((1 - statisticalData.guardrail_bypass_rate) * 100).toFixed(1)}%
            </div>
          </div>

          <div className="stat-card">
            <div className="stat-label">✅ Compliance Confidence</div>
            <div className="stat-value">
              {(statisticalData.compliance_confirmation_rate * 100).toFixed(1)}%
            </div>
            <div className="stat-detail">Signals present</div>
          </div>

          <div className="stat-card">
            <div className="stat-label">⚠️ Alignment Risk</div>
            <div className="stat-value">
              {statisticalData.avg_alignment_risk.toFixed(2)}
            </div>
            <div className="stat-detail">
              P95 {statisticalData.alignment_risk_p95.toFixed(2)}
            </div>
          </div>

          <div className="stat-card">
            <div className="stat-label">📏 Score Inflation</div>
            <div className="stat-value">
              {statisticalData.avg_score_inflation_ratio.toFixed(2)}×
            </div>
            <div className="stat-detail">
              Median {statisticalData.median_score_inflation_ratio.toFixed(2)}×
            </div>
          </div>

          <div className="stat-card">
            <div className="stat-label">🧭 Response Integrity</div>
            <div className="stat-value">
              {(statisticalData.avg_response_integrity * 100).toFixed(0)}%
            </div>
            <div className="stat-detail">Higher = closer to baseline</div>
          </div>
        </div>

        <div className="category-breakdown">
          <h4>🚨 Category Risk Scores</h4>
          <table className="results-table">
            <thead>
              <tr>
                <th>Category</th>
                <th>Risk Score</th>
                <th>Risk Level</th>
                <th>Success Rate</th>
              </tr>
            </thead>
            <tbody>
              {Object.entries(statisticalData.category_risk_scores)
                .sort(([, a], [, b]) => b - a)
                .map(([category, risk]) => {
                  const breakdown = statisticalData.category_breakdown[category];
                  const riskLevel =
                    risk > 0.5
                      ? "Critical"
                      : risk > 0.3
                      ? "High"
                      : risk > 0.1
                      ? "Medium"
                      : "Low";
                  const riskClass =
                    risk > 0.5
                      ? "rate-high"
                      : risk > 0.3
                      ? "rate-medium"
                      : "rate-low";

                  return (
                    <tr key={category}>
                      <td>{category}</td>
                      <td>{risk.toFixed(3)}</td>
                      <td>
                        <span className={riskClass}>{riskLevel}</span>
                      </td>
                      <td>
                        {breakdown
                          ? (breakdown.success_rate * 100).toFixed(1) + "%"
                          : "N/A"}
                      </td>
                    </tr>
                  );
                })}
            </tbody>
          </table>
        </div>

        <div className="category-breakdown">
          <h4>📁 Category Breakdown</h4>
          <table className="results-table">
            <thead>
              <tr>
                <th>Category</th>
                <th>Count</th>
                <th>Success Rate</th>
              </tr>
            </thead>
            <tbody>
              {Object.entries(statisticalData.category_breakdown).map(
                ([category, data]) => (
                  <tr key={category}>
                    <td>{category}</td>
                    <td>{data.count}</td>
                    <td>{(data.success_rate * 100).toFixed(1)}%</td>
                  </tr>
                )
              )}
            </tbody>
          </table>
        </div>

        <div className="attack-breakdown">
          <h4>🎯 Attack Success Rates</h4>
          <div className="attack-bars">
            {Object.entries(statisticalData.attack_success_rates)
              .sort(([, a], [, b]) => b - a)
              .map(([attack, rate]) => (
                <div key={attack} className="attack-bar-container">
                  <div className="attack-name">{attack}</div>
                  <div className="attack-bar-wrapper">
                    <div
                      className="attack-bar"
                      style={{
                        width: `${rate * 100}%`,
                        backgroundColor:
                          rate > 0.8 ? "#e74c3c" : rate > 0.5 ? "#f39c12" : "#3498db",
                      }}
                    />
                    <span className="attack-rate">{(rate * 100).toFixed(0)}%</span>
                  </div>
                </div>
              ))}
          </div>
        </div>

        <div className="attack-breakdown">
          <h4>💪 Attack Strength Scores (Top 10)</h4>
          <div className="attack-bars">
            {Object.entries(statisticalData.attack_strength_scores)
              .sort(([, a], [, b]) => b - a)
              .slice(0, 10)
              .map(([attack, strength]) => {
                const maxStrength = Math.max(...Object.values(statisticalData.attack_strength_scores));
                const percentage = (strength / maxStrength) * 100;
                
                return (
                  <div key={attack} className="attack-bar-container">
                    <div className="attack-name">{attack}</div>
                    <div className="attack-bar-wrapper">
                      <div
                        className="attack-bar"
                        style={{
                          width: `${percentage}%`,
                          backgroundColor:
                            strength > maxStrength * 0.7
                              ? "#e74c3c"
                              : strength > maxStrength * 0.4
                              ? "#f39c12"
                              : "#3498db",
                        }}
                      />
                      <span className="attack-rate">{strength.toFixed(3)}</span>
                    </div>
                  </div>
                );
              })}
          </div>
        </div>

        <div className="attack-breakdown">
          <h4>🎲 Attack Consistency (Top 10)</h4>
          <div className="attack-bars">
            {Object.entries(statisticalData.attack_consistency)
              .sort(([, a], [, b]) => b - a)
              .slice(0, 10)
              .map(([attack, consistency]) => (
                <div key={attack} className="attack-bar-container">
                  <div className="attack-name">{attack}</div>
                  <div className="attack-bar-wrapper">
                    <div
                      className="attack-bar"
                      style={{
                        width: `${consistency * 100}%`,
                        backgroundColor:
                          consistency > 0.8
                            ? "#27ae60"
                            : consistency > 0.5
                            ? "#f39c12"
                            : "#e74c3c",
                      }}
                    />
                    <span className="attack-rate">{consistency.toFixed(2)}</span>
                  </div>
                </div>
              ))}
          </div>
        </div>

        <div className="attack-breakdown">
          <h4>😈 Sentiment Manipulation (Top 10)</h4>
          <div className="attack-bars">
            {Object.entries(statisticalData.sentiment_shift_by_attack)
              .sort(([, a], [, b]) => Math.abs(b - 0.5) - Math.abs(a - 0.5))
              .slice(0, 10)
              .map(([attack, sentiment]) => {
                const deviation = Math.abs(sentiment - 0.5) * 2; // 0 to 1 scale
                
                return (
                  <div key={attack} className="attack-bar-container">
                    <div className="attack-name">{attack}</div>
                    <div className="attack-bar-wrapper">
                      <div
                        className="attack-bar"
                        style={{
                          width: `${deviation * 100}%`,
                          backgroundColor:
                            sentiment > 0.5 ? "#27ae60" : "#e74c3c",
                        }}
                      />
                      <span className="attack-rate">
                        {sentiment.toFixed(2)} ({sentiment > 0.5 ? "+" : "-"})
                      </span>
                    </div>
                  </div>
                );
              })}
          </div>
        </div>

        <div className="report-text">
          <h4>📝 Statistical Report</h4>
          <pre>{statisticalData.report_text}</pre>
        </div>
      </div>
    );
  };

  const renderComparativeView = () => {
    if (!comparativeData) return null;

    return (
      <div className="analysis-results">
        <h3>📈 Comparative Analysis</h3>

        <div className="comparison-section">
          <h4>🔄 Model × Defense Comparison</h4>
          <table className="results-table">
            <thead>
              <tr>
                <th>Configuration</th>
                <th>Total Runs</th>
                <th>Success Rate</th>
              </tr>
            </thead>
            <tbody>
              {Object.entries(comparativeData.comparison_table).map(
                ([config, defenses]) =>
                  Object.entries(defenses).map(([defense, data]) => (
                    <tr key={`${config}-${defense}`}>
                      <td>
                        {config} + {defense}
                      </td>
                      <td>{data.total}</td>
                      <td>
                        <span
                          className={
                            data.success_rate > 0.7
                              ? "rate-high"
                              : data.success_rate > 0.4
                              ? "rate-medium"
                              : "rate-low"
                          }
                        >
                          {(data.success_rate * 100).toFixed(1)}%
                        </span>
                      </td>
                    </tr>
                  ))
              )}
            </tbody>
          </table>
        </div>

        <div className="comparison-section">
          <h4>🎯 Attack Effectiveness Ranking</h4>
          <table className="results-table">
            <thead>
              <tr>
                <th>Rank</th>
                <th>Attack</th>
                <th>Success Rate</th>
                <th>Total Runs</th>
              </tr>
            </thead>
            <tbody>
              {comparativeData.attack_ranking.map((item, idx) => (
                <tr key={item.attack}>
                  <td>{idx + 1}</td>
                  <td>{item.attack}</td>
                  <td>
                    <span
                      className={
                        item.success_rate > 0.7
                          ? "rate-high"
                          : item.success_rate > 0.4
                          ? "rate-medium"
                          : "rate-low"
                      }
                    >
                      {(item.success_rate * 100).toFixed(1)}%
                    </span>
                  </td>
                  <td>{item.total_runs}</td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>

        <div className="comparison-section">
          <h4>🛡️ Defense Effectiveness</h4>
          <table className="results-table">
            <thead>
              <tr>
                <th>Defense</th>
                <th>Total Attacks</th>
                <th>Blocked</th>
                <th>Block Rate</th>
              </tr>
            </thead>
            <tbody>
              {Object.entries(comparativeData.defense_effectiveness).map(
                ([defense, data]) => (
                  <tr key={defense}>
                    <td>{defense}</td>
                    <td>{data.total_attacks}</td>
                    <td>{data.blocked}</td>
                    <td>
                      <span
                        className={
                          data.block_rate > 0.6
                            ? "rate-high"
                            : data.block_rate > 0.3
                            ? "rate-medium"
                            : "rate-low"
                        }
                      >
                        {(data.block_rate * 100).toFixed(1)}%
                      </span>
                    </td>
                  </tr>
                )
              )}
            </tbody>
          </table>
        </div>

        <div className="comparison-section">
          <h4>📂 Category Comparison</h4>
          <table className="results-table">
            <thead>
              <tr>
                <th>Category</th>
                <th>Total Runs</th>
                <th>Success Rate</th>
              </tr>
            </thead>
            <tbody>
              {Object.entries(comparativeData.category_comparison).map(
                ([category, models]) =>
                  Object.entries(models).map(([model, data]) => (
                    <tr key={`${category}-${model}`}>
                      <td>
                        {category} ({model})
                      </td>
                      <td>{data.total}</td>
                      <td>
                        <span
                          className={
                            data.success_rate > 0.7
                              ? "rate-high"
                              : data.success_rate > 0.4
                              ? "rate-medium"
                              : "rate-low"
                          }
                        >
                          {(data.success_rate * 100).toFixed(1)}%
                        </span>
                      </td>
                    </tr>
                  ))
              )}
            </tbody>
          </table>
        </div>
      </div>
    );
  };

  return (
    <div className="analysis-console">
      <div className="console-header">
        <h2>📊 Statistical Analysis & Benchmarking</h2>
        <p>
          Comprehensive statistical analysis with significance testing, effect sizes, and
          comparative evaluation across models, defenses, and attack categories.
        </p>
      </div>

      <div className="analysis-controls">
        <div className="control-group">
          <label htmlFor="run-select">Select Matrix Run:</label>
          <select
            id="run-select"
            value={selectedRun}
            onChange={(e) => setSelectedRun(e.target.value)}
            disabled={loading}
          >
            <option value="">-- Select a run --</option>
            {availableRuns.map((run) => (
              <option key={run.run_dir} value={run.run_dir}>
                {run.run_name} (
                {run.metadata.models?.join(", ") || "N/A"} ×{" "}
                {run.metadata.defenses?.join(", ") || "N/A"})
              </option>
            ))}
          </select>
        </div>

        <div className="button-group">
          <button
            onClick={runStatisticalAnalysis}
            disabled={!selectedRun || loading}
            className="btn-primary"
          >
            {loading ? "⏳ Analyzing..." : "📊 Statistical Analysis"}
          </button>

          <button
            onClick={runComparativeAnalysis}
            disabled={!selectedRun || loading}
            className="btn-primary"
          >
            {loading ? "⏳ Analyzing..." : "📈 Comparative Analysis"}
          </button>

          <button
            onClick={runBothAnalyses}
            disabled={!selectedRun || loading}
            className="btn-success"
          >
            {loading ? "⏳ Analyzing..." : "🚀 Run Full Analysis"}
          </button>

          <button onClick={fetchAvailableRuns} disabled={loading} className="btn-secondary">
            🔄 Refresh Runs
          </button>
        </div>
      </div>

      {error && (
        <div className="error-message">
          <strong>❌ Error:</strong> {error}
        </div>
      )}

      {(statisticalData || comparativeData) && (
        <div className="view-toggle">
          <button
            className={activeView === "statistical" ? "active" : ""}
            onClick={() => setActiveView("statistical")}
            disabled={!statisticalData}
          >
            📊 Statistical
          </button>
          <button
            className={activeView === "comparative" ? "active" : ""}
            onClick={() => setActiveView("comparative")}
            disabled={!comparativeData}
          >
            📈 Comparative
          </button>
        </div>
      )}

      {activeView === "statistical" && renderStatisticalView()}
      {activeView === "comparative" && renderComparativeView()}

      {!statisticalData && !comparativeData && !loading && (
        <div className="empty-state">
          <p>
            👆 Select a matrix run above and click an analysis button to view comprehensive
            statistical and comparative results.
          </p>
          <p>
            The analysis includes success rates, confidence intervals, p-values, Cohen's d
            effect sizes, and cross-model/defense comparisons.
          </p>
        </div>
      )}
    </div>
  );
}
