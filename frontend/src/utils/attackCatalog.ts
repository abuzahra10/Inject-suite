export type AttackRecipe = {
  id: string;
  label: string;
  description: string;
  domain?: string;
  severity?: string;
  intent?: string;
};

export type CategorizedAttack = AttackRecipe & {
  category: string;
  cleanDescription: string;
  normalizedDomain: string;
  normalizedSeverity: string;
};

export type CategoryStat = {
  category: string;
  count: number;
};

export function categorizeAttack(recipe: AttackRecipe): CategorizedAttack {
  const match = recipe.description.match(/^\[(.*?)\]\s*(.*)$/);
  const domain = (recipe.domain ?? "cv").toLowerCase();
  const severity = (recipe.severity ?? "medium").toLowerCase();
  if (!match) {
    return {
      ...recipe,
      category: "Other",
      cleanDescription: recipe.description,
      normalizedDomain: domain,
      normalizedSeverity: severity,
    };
  }

  return {
    ...recipe,
    category: match[1],
    cleanDescription: match[2],
    normalizedDomain: domain,
    normalizedSeverity: severity,
  };
}

export function categorizeRecipes(recipes: AttackRecipe[]): CategorizedAttack[] {
  return recipes.map(categorizeAttack);
}

export function getCategoryStats(recipes: CategorizedAttack[]): CategoryStat[] {
  return tallyFacet(recipes, (recipe) => recipe.category);
}

export function getDomainStats(recipes: CategorizedAttack[]): CategoryStat[] {
  return tallyFacet(recipes, (recipe) => recipe.normalizedDomain);
}

export function getSeverityStats(recipes: CategorizedAttack[]): CategoryStat[] {
  return tallyFacet(recipes, (recipe) => recipe.normalizedSeverity);
}

function tallyFacet(
  recipes: CategorizedAttack[],
  picker: (recipe: CategorizedAttack) => string,
): CategoryStat[] {
  const tally = new Map<string, number>();
  recipes.forEach((recipe) => {
    const key = picker(recipe);
    tally.set(key, (tally.get(key) ?? 0) + 1);
  });

  return Array.from(tally.entries())
    .map(([category, count]) => ({ category, count }))
    .sort((a, b) => b.count - a.count);
}

export function filterAttacks(
  recipes: CategorizedAttack[],
  searchTerm: string,
  categoryFilter: string,
  domainFilter: string,
  severityFilter: string,
): CategorizedAttack[] {
  const normalizedSearch = searchTerm.trim().toLowerCase();
  return recipes.filter((recipe) => {
    const matchesCategory = categoryFilter === "all" || recipe.category === categoryFilter;
    const matchesDomain = domainFilter === "all" || recipe.normalizedDomain === domainFilter;
    const matchesSeverity = severityFilter === "all" || recipe.normalizedSeverity === severityFilter;
    const matchesSearch =
      normalizedSearch.length === 0 ||
      recipe.label.toLowerCase().includes(normalizedSearch) ||
      recipe.cleanDescription.toLowerCase().includes(normalizedSearch) ||
      recipe.id.toLowerCase().includes(normalizedSearch);
    return matchesCategory && matchesDomain && matchesSeverity && matchesSearch;
  });
}
