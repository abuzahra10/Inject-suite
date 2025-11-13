"""Compare results across models, defenses, and attack categories."""

from __future__ import annotations

import json
from pathlib import Path
from typing import Dict, List, Any, Tuple
from dataclasses import dataclass


@dataclass
class ComparisonEntry:
    """Single entry in comparison matrix."""
    model: str
    defense: str
    attack: str
    category: str
    success: bool
    score: float | None
    score_delta: float | None
    
    def to_dict(self) -> Dict[str, Any]:
        return {
            "model": self.model,
            "defense": self.defense,
            "attack": self.attack,
            "category": self.category,
            "success": self.success,
            "score": self.score,
            "score_delta": self.score_delta,
        }


@dataclass
class SimpleResult:
    """Simplified result for analysis."""
    attack_id: str
    model_name: str
    success: bool
    score: float | None
    metrics: Dict[str, Any]
    

def load_all_results(results_base_dir: Path) -> List[SimpleResult]:
    """
    Load all evaluation results from a directory tree.
    
    Expects structure: results_base_dir/model_name/defense_name/results.json
    
    Args:
        results_base_dir: Base directory containing evaluation results
        
    Returns:
        List of EvaluationResult objects
    """
    all_results = []
    
    # Look for results.json files recursively
    for results_file in results_base_dir.rglob("results.json"):
        try:
            with open(results_file, 'r', encoding='utf-8') as f:
                data = json.load(f)
            
            # Extract model and defense from path
            # Path structure: .../model_name/defense_name/results.json
            parts = results_file.parts
            defense_name = parts[-2] if len(parts) >= 2 else "unknown"
            model_name = parts[-3] if len(parts) >= 3 else "unknown"
            
            # Handle both formats:
            # 1. Dictionary with attack_id as keys (current format)
            # 2. Single EvaluationResult object (potential future format)
            
            if isinstance(data, dict):
                # Current format: {attack_id: {model, score, success, metrics, response_preview}}
                for attack_id, result_data in data.items():
                    # Skip baseline in analysis (or include it if needed)
                    if attack_id == "baseline":
                        continue
                        
                    result = SimpleResult(
                        attack_id=attack_id,
                        model_name=result_data.get("model", model_name),
                        success=result_data.get("success", False),
                        score=result_data.get("score"),
                        metrics=result_data.get("metrics", {}),
                    )
                    all_results.append(result)
            else:
                # Future format: single result object
                result = SimpleResult(**data)
                all_results.append(result)
                
        except (json.JSONDecodeError, KeyError, TypeError) as e:
            print(f"Warning: Could not load {results_file}: {e}")
            continue
    
    return all_results


def generate_comparison_table(entries: List[ComparisonEntry]) -> str:
    """Generate comprehensive comparison table."""
    
    lines = []
    lines.append("=" * 120)
    lines.append("COMPARATIVE ANALYSIS TABLE")
    lines.append("=" * 120)
    
    # Group by model and defense
    configs = {}
    for entry in entries:
        key = (entry.model, entry.defense)
        if key not in configs:
            configs[key] = []
        configs[key].append(entry)
    
    # Calculate summary stats per config
    summary_stats = []
    for (model, defense), config_entries in configs.items():
        total = len(config_entries)
        successful = sum(1 for e in config_entries if e.success)
        success_rate = successful / total if total > 0 else 0.0
        
        scores = [e.score for e in config_entries if e.score is not None]
        deltas = [e.score_delta for e in config_entries if e.score_delta is not None]
        
        avg_score = sum(scores) / len(scores) if scores else 0.0
        avg_delta = sum(deltas) / len(deltas) if deltas else 0.0
        
        summary_stats.append({
            "model": model,
            "defense": defense,
            "success_rate": success_rate,
            "successful": successful,
            "total": total,
            "avg_score": avg_score,
            "avg_delta": avg_delta,
        })
    
    # Sort by success rate
    summary_stats.sort(key=lambda x: x["success_rate"])
    
    # Print summary
    lines.append(f"\n{'Model':<20} {'Defense':<25} {'Success Rate':<15} {'Attacks':<12} {'Avg Score':<12} {'Avg Delta':<12}")
    lines.append("-" * 120)
    
    for stat in summary_stats:
        lines.append(
            f"{stat['model']:<20} "
            f"{stat['defense']:<25} "
            f"{stat['success_rate']:>13.1%}  "
            f"{stat['successful']:>3}/{stat['total']:<6} "
            f"{stat['avg_score']:>10.2f}  "
            f"{stat['avg_delta']:>+10.2f}"
        )
    
    lines.append("=" * 120)
    
    return "\n".join(lines)


def generate_category_comparison(entries: List[ComparisonEntry]) -> str:
    """Generate category-wise comparison across models/defenses."""
    
    lines = []
    lines.append("\n" + "=" * 100)
    lines.append("CATEGORY-WISE COMPARISON")
    lines.append("=" * 100)
    
    # Group by category
    categories = {}
    for entry in entries:
        if entry.category not in categories:
            categories[entry.category] = []
        categories[entry.category].append(entry)
    
    for category, cat_entries in sorted(categories.items()):
        lines.append(f"\n### {category} ###")
        
        # Group by model+defense
        configs = {}
        for entry in cat_entries:
            key = f"{entry.model}/{entry.defense}"
            if key not in configs:
                configs[key] = []
            configs[key].append(entry)
        
        lines.append(f"{'Config':<40} {'Success Rate':<15} {'Successful':<15} {'Avg Delta':<15}")
        lines.append("-" * 100)
        
        for config, config_entries in sorted(configs.items()):
            total = len(config_entries)
            successful = sum(1 for e in config_entries if e.success)
            success_rate = successful / total if total > 0 else 0.0
            
            deltas = [e.score_delta for e in config_entries if e.score_delta is not None]
            avg_delta = sum(deltas) / len(deltas) if deltas else 0.0
            
            lines.append(
                f"{config:<40} "
                f"{success_rate:>13.1%}  "
                f"{successful:>3}/{total:<9} "
                f"{avg_delta:>+13.2f}"
            )
    
    lines.append("=" * 100)
    
    return "\n".join(lines)


def generate_attack_ranking(entries: List[ComparisonEntry]) -> str:
    """Rank attacks by effectiveness across all configurations."""
    
    lines = []
    lines.append("\n" + "=" * 100)
    lines.append("ATTACK EFFECTIVENESS RANKING")
    lines.append("=" * 100)
    
    # Group by attack
    attacks = {}
    for entry in entries:
        if entry.attack not in attacks:
            attacks[entry.attack] = []
        attacks[entry.attack].append(entry)
    
    attack_stats = []
    for attack_id, attack_entries in attacks.items():
        total = len(attack_entries)
        successful = sum(1 for e in attack_entries if e.success)
        success_rate = successful / total if total > 0 else 0.0
        
        scores = [e.score for e in attack_entries if e.score is not None]
        deltas = [e.score_delta for e in attack_entries if e.score_delta is not None]
        
        avg_score = sum(scores) / len(scores) if scores else 0.0
        avg_delta = sum(deltas) / len(deltas) if deltas else 0.0
        
        from evaluation.metrics import categorize_attack
        category = categorize_attack(attack_id)
        
        attack_stats.append({
            "attack": attack_id,
            "category": category,
            "success_rate": success_rate,
            "successful": successful,
            "total": total,
            "avg_score": avg_score,
            "avg_delta": avg_delta,
        })
    
    # Sort by success rate (descending)
    attack_stats.sort(key=lambda x: x["success_rate"], reverse=True)
    
    lines.append(f"{'Rank':<6} {'Attack':<30} {'Category':<25} {'Success Rate':<15} {'Tests':<10} {'Avg Delta':<12}")
    lines.append("-" * 100)
    
    for rank, stat in enumerate(attack_stats, 1):
        lines.append(
            f"{rank:<6} "
            f"{stat['attack']:<30} "
            f"{stat['category']:<25} "
            f"{stat['success_rate']:>13.1%}  "
            f"{stat['successful']:>2}/{stat['total']:<6} "
            f"{stat['avg_delta']:>+10.2f}"
        )
    
    lines.append("=" * 100)
    
    return "\n".join(lines)


def generate_defense_effectiveness_report(entries: List[ComparisonEntry]) -> str:
    """Analyze defense effectiveness."""
    
    lines = []
    lines.append("\n" + "=" * 100)
    lines.append("DEFENSE EFFECTIVENESS ANALYSIS")
    lines.append("=" * 100)
    
    # Group by defense
    defenses = {}
    for entry in entries:
        if entry.defense not in defenses:
            defenses[entry.defense] = []
        defenses[entry.defense].append(entry)
    
    defense_stats = []
    for defense_name, defense_entries in defenses.items():
        total = len(defense_entries)
        successful = sum(1 for e in defense_entries if e.success)
        blocked = total - successful
        block_rate = blocked / total if total > 0 else 0.0
        
        deltas = [e.score_delta for e in defense_entries if e.score_delta is not None]
        avg_delta = sum(deltas) / len(deltas) if deltas else 0.0
        
        defense_stats.append({
            "defense": defense_name,
            "block_rate": block_rate,
            "blocked": blocked,
            "total": total,
            "avg_delta": avg_delta,
        })
    
    # Sort by block rate (higher is better)
    defense_stats.sort(key=lambda x: x["block_rate"], reverse=True)
    
    lines.append(f"{'Defense':<30} {'Block Rate':<15} {'Blocked':<15} {'Avg Delta (when successful)':<30}")
    lines.append("-" * 100)
    
    for stat in defense_stats:
        lines.append(
            f"{stat['defense']:<30} "
            f"{stat['block_rate']:>13.1%}  "
            f"{stat['blocked']:>3}/{stat['total']:<9} "
            f"{stat['avg_delta']:>+28.2f}"
        )
    
    lines.append("=" * 100)
    lines.append("\nNote: Higher block rate = more effective defense")
    
    return "\n".join(lines)


def save_comparison_data(entries: List[ComparisonEntry], output_path: Path):
    """Save comparison data to JSON."""
    
    data = {
        "entries": [entry.to_dict() for entry in entries],
        "summary": {
            "total_entries": len(entries),
            "unique_models": len(set(e.model for e in entries)),
            "unique_defenses": len(set(e.defense for e in entries)),
            "unique_attacks": len(set(e.attack for e in entries)),
        }
    }
    
    output_path.parent.mkdir(parents=True, exist_ok=True)
    with open(output_path, 'w') as f:
        json.dump(data, f, indent=2)
    
    print(f"Comparison data saved to {output_path}")
