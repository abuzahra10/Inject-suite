"""Statistical analysis for attack evaluation results."""

from __future__ import annotations

import json
from pathlib import Path
from typing import Dict, List, Tuple, Any
from dataclasses import dataclass
import numpy as np


try:
    from scipy import stats as scipy_stats
    SCIPY_AVAILABLE = True
except ImportError:
    SCIPY_AVAILABLE = False
    print("Warning: scipy not available. Statistical tests will be limited.")


@dataclass
class StatisticalSummary:
    """Statistical summary of evaluation results."""
    
    # Success rates
    overall_success_rate: float
    success_by_category: Dict[str, float]
    
    # Score statistics
    mean_score: float
    median_score: float
    std_score: float
    min_score: float
    max_score: float
    
    # Score deltas
    mean_delta: float
    median_delta: float
    max_delta: float
    min_delta: float
    std_delta: float
    
    # Confidence intervals (95%)
    delta_ci_95: Tuple[float, float]
    success_rate_ci_95: Tuple[float, float]
    
    # Effect size
    cohens_d: float  # standardized difference vs baseline
    
    # Statistical tests
    t_statistic: float
    p_value: float
    statistically_significant: bool  # p < 0.05
    
    # Category breakdown
    category_stats: Dict[str, Dict[str, Any]]
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary for JSON serialization."""
        return {
            "overall_success_rate": self.overall_success_rate,
            "success_by_category": self.success_by_category,
            "mean_score": self.mean_score,
            "median_score": self.median_score,
            "std_score": self.std_score,
            "min_score": self.min_score,
            "max_score": self.max_score,
            "mean_delta": self.mean_delta,
            "median_delta": self.median_delta,
            "max_delta": self.max_delta,
            "min_delta": self.min_delta,
            "std_delta": self.std_delta,
            "delta_ci_95": list(self.delta_ci_95),
            "success_rate_ci_95": list(self.success_rate_ci_95),
            "cohens_d": self.cohens_d,
            "t_statistic": self.t_statistic,
            "p_value": self.p_value,
            "statistically_significant": self.statistically_significant,
            "category_stats": self.category_stats,
        }


def calculate_cohens_d(group1: List[float], group2: List[float]) -> float:
    """Calculate Cohen's d effect size."""
    if len(group1) < 2 or len(group2) < 2:
        return 0.0
    
    n1, n2 = len(group1), len(group2)
    var1, var2 = np.var(group1, ddof=1), np.var(group2, ddof=1)
    
    pooled_std = np.sqrt(((n1-1)*var1 + (n2-1)*var2) / (n1+n2-2))
    
    if pooled_std == 0:
        return 0.0
    
    return (np.mean(group1) - np.mean(group2)) / pooled_std


def perform_statistical_analysis(results, baseline_score: float | None = None) -> StatisticalSummary:
    """
    Perform comprehensive statistical analysis on evaluation results.
    
    Args:
        results: Either a Dict[str, result] or List[result] where result has attack_id, score, success
        baseline_score: Optional baseline score for comparison
        
    Returns:
        StatisticalSummary with comprehensive statistics
    """
    
    from evaluation.metrics import categorize_attack
    
    scores = []
    deltas = []
    successes = []
    categories = {}
    
    # Convert list to dict if needed
    if isinstance(results, list):
        results_dict = {r.attack_id: r for r in results}
    else:
        results_dict = results
    
    # If baseline_score not provided, try to extract from results
    if baseline_score is None and "baseline" in results_dict:
        baseline_result = results_dict["baseline"]
        if hasattr(baseline_result, 'score'):
            baseline_score = baseline_result.score
        elif isinstance(baseline_result, dict):
            baseline_score = baseline_result.get("score")
    
    if baseline_score is None:
        baseline_score = 0.0
    
    for attack_id, result in results_dict.items():
        if attack_id == "baseline":
            continue
        
        # Extract score
        if hasattr(result, 'score'):
            score = result.score
            success = result.success
        elif isinstance(result, dict):
            score = result.get("score")
            success = result.get("success", False)
        else:
            continue
        
        if score is not None:
            scores.append(score)
            deltas.append(score - baseline_score)
        
        successes.append(1 if success else 0)
        
        # Categorize
        category = categorize_attack(attack_id)
        if category not in categories:
            categories[category] = {"scores": [], "successes": [], "deltas": []}
        
        if score is not None:
            categories[category]["scores"].append(score)
            categories[category]["deltas"].append(score - baseline_score)
        categories[category]["successes"].append(1 if success else 0)
    
    # Basic statistics
    mean_score = float(np.mean(scores)) if scores else 0.0
    median_score = float(np.median(scores)) if scores else 0.0
    std_score = float(np.std(scores, ddof=1)) if len(scores) > 1 else 0.0
    min_score = float(np.min(scores)) if scores else 0.0
    max_score = float(np.max(scores)) if scores else 0.0
    
    mean_delta = float(np.mean(deltas)) if deltas else 0.0
    median_delta = float(np.median(deltas)) if deltas else 0.0
    max_delta = float(np.max(deltas)) if deltas else 0.0
    min_delta = float(np.min(deltas)) if deltas else 0.0
    std_delta = float(np.std(deltas, ddof=1)) if len(deltas) > 1 else 0.0
    
    # Confidence intervals
    if SCIPY_AVAILABLE and len(deltas) > 1:
        delta_ci = scipy_stats.t.interval(
            0.95, len(deltas)-1, 
            loc=np.mean(deltas), 
            scale=scipy_stats.sem(deltas)
        )
        delta_ci = (float(delta_ci[0]), float(delta_ci[1]))
    else:
        # Fallback to approximate CI
        if len(deltas) > 1:
            margin = 1.96 * (std_delta / np.sqrt(len(deltas)))
            delta_ci = (mean_delta - margin, mean_delta + margin)
        else:
            delta_ci = (mean_delta, mean_delta)
    
    success_rate = float(np.mean(successes)) if successes else 0.0
    if len(successes) > 1:
        success_se = np.sqrt(success_rate * (1-success_rate) / len(successes))
        success_ci = (
            max(0.0, success_rate - 1.96*success_se),
            min(1.0, success_rate + 1.96*success_se)
        )
    else:
        success_ci = (success_rate, success_rate)
    
    # Effect size (Cohen's d)
    baseline_scores = [baseline_score] * len(scores)
    cohens_d = calculate_cohens_d(scores, baseline_scores) if scores else 0.0
    
    # T-test
    if SCIPY_AVAILABLE and len(deltas) > 1:
        t_stat, p_val = scipy_stats.ttest_1samp(deltas, 0)
        t_stat = float(t_stat)
        p_val = float(p_val)
    else:
        # Fallback to simple t-statistic
        if len(deltas) > 1 and std_delta > 0:
            t_stat = mean_delta / (std_delta / np.sqrt(len(deltas)))
            p_val = 0.05  # Can't calculate without scipy
        else:
            t_stat, p_val = 0.0, 1.0
    
    # Category statistics
    category_stats = {}
    for cat_name, cat_data in categories.items():
        cat_success_rate = float(np.mean(cat_data["successes"])) if cat_data["successes"] else 0.0
        cat_mean_score = float(np.mean(cat_data["scores"])) if cat_data["scores"] else 0.0
        cat_mean_delta = float(np.mean(cat_data["deltas"])) if cat_data["deltas"] else 0.0
        
        category_stats[cat_name] = {
            "success_rate": cat_success_rate,
            "mean_score": cat_mean_score,
            "mean_delta": cat_mean_delta,
            "n_attacks": len(cat_data["successes"]),
        }
    
    success_by_category = {
        cat: stats["success_rate"] 
        for cat, stats in category_stats.items()
    }
    
    return StatisticalSummary(
        overall_success_rate=success_rate,
        success_by_category=success_by_category,
        mean_score=mean_score,
        median_score=median_score,
        std_score=std_score,
        min_score=min_score,
        max_score=max_score,
        mean_delta=mean_delta,
        median_delta=median_delta,
        max_delta=max_delta,
        min_delta=min_delta,
        std_delta=std_delta,
        delta_ci_95=delta_ci,
        success_rate_ci_95=success_ci,
        cohens_d=cohens_d,
        t_statistic=t_stat,
        p_value=p_val,
        statistically_significant=(p_val < 0.05),
        category_stats=category_stats,
    )


def generate_statistical_report(summary: StatisticalSummary) -> str:
    """Generate human-readable statistical report."""
    
    lines = []
    lines.append("=" * 80)
    lines.append("STATISTICAL ANALYSIS REPORT")
    lines.append("=" * 80)
    
    # Overall metrics
    lines.append("\n### OVERALL METRICS ###")
    lines.append(f"Success Rate: {summary.overall_success_rate:.1%}")
    lines.append(f"  95% CI: [{summary.success_rate_ci_95[0]:.1%}, {summary.success_rate_ci_95[1]:.1%}]")
    lines.append(f"\nMean Score: {summary.mean_score:.2f}/10")
    lines.append(f"Median Score: {summary.median_score:.2f}/10")
    lines.append(f"Score Range: [{summary.min_score:.2f}, {summary.max_score:.2f}]")
    lines.append(f"Std Dev: {summary.std_score:.2f}")
    
    # Score deltas
    lines.append(f"\n### SCORE INFLATION ###")
    lines.append(f"Mean Delta: {summary.mean_delta:+.2f} points")
    lines.append(f"  95% CI: [{summary.delta_ci_95[0]:+.2f}, {summary.delta_ci_95[1]:+.2f}]")
    lines.append(f"Median Delta: {summary.median_delta:+.2f} points")
    lines.append(f"Delta Range: [{summary.min_delta:+.2f}, {summary.max_delta:+.2f}]")
    lines.append(f"Std Dev: {summary.std_delta:.2f}")
    
    # Effect size
    lines.append(f"\n### EFFECT SIZE ###")
    lines.append(f"Cohen's d: {summary.cohens_d:.3f}")
    if abs(summary.cohens_d) < 0.2:
        effect_desc = "negligible"
    elif abs(summary.cohens_d) < 0.5:
        effect_desc = "small"
    elif abs(summary.cohens_d) < 0.8:
        effect_desc = "medium"
    else:
        effect_desc = "large"
    lines.append(f"  Interpretation: {effect_desc} effect")
    
    # Statistical significance
    lines.append(f"\n### STATISTICAL SIGNIFICANCE ###")
    lines.append(f"t-statistic: {summary.t_statistic:.3f}")
    lines.append(f"p-value: {summary.p_value:.4f}")
    if summary.statistically_significant:
        lines.append("  Result: ✓ Statistically significant (p < 0.05)")
    else:
        lines.append("  Result: ✗ Not statistically significant (p >= 0.05)")
    
    # Category breakdown
    lines.append(f"\n### BY CATEGORY ###")
    lines.append(f"{'Category':<30} {'Success Rate':<15} {'Mean Score':<12} {'Mean Delta':<12}")
    lines.append("-" * 80)
    
    for cat_name, cat_stats in sorted(summary.category_stats.items()):
        lines.append(
            f"{cat_name:<30} "
            f"{cat_stats['success_rate']:>13.1%}  "
            f"{cat_stats['mean_score']:>10.2f}  "
            f"{cat_stats['mean_delta']:>+10.2f}"
        )
    
    lines.append("=" * 80)
    
    return "\n".join(lines)
