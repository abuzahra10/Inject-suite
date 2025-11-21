export type AttackRecipe = {
  id: string;
  label: string;
  description: string;
};

export type CategorizedAttack = AttackRecipe & {
  category: string;
  cleanDescription: string;
};

export type CategoryStat = {
  category: string;
  count: number;
};

export function categorizeAttack(recipe: AttackRecipe): CategorizedAttack {
  const match = recipe.description.match(/^\[(.*?)\]\s*(.*)$/);
  if (!match) {
    return {
      ...recipe,
      category: "Other",
      cleanDescription: recipe.description,
    };
  }

  return {
    ...recipe,
    category: match[1],
    cleanDescription: match[2],
  };
}

export function categorizeRecipes(recipes: AttackRecipe[]): CategorizedAttack[] {
  return recipes.map(categorizeAttack);
}

export function getCategoryStats(recipes: CategorizedAttack[]): CategoryStat[] {
  const tally = new Map<string, number>();
  recipes.forEach((recipe) => {
    tally.set(recipe.category, (tally.get(recipe.category) ?? 0) + 1);
  });

  return Array.from(tally.entries())
    .map(([category, count]) => ({ category, count }))
    .sort((a, b) => b.count - a.count);
}

export function filterAttacks(
  recipes: CategorizedAttack[],
  searchTerm: string,
  categoryFilter: string,
): CategorizedAttack[] {
  const normalizedSearch = searchTerm.trim().toLowerCase();
  return recipes.filter((recipe) => {
    const matchesCategory = categoryFilter === "all" || recipe.category === categoryFilter;
    const matchesSearch =
      normalizedSearch.length === 0 ||
      recipe.label.toLowerCase().includes(normalizedSearch) ||
      recipe.cleanDescription.toLowerCase().includes(normalizedSearch) ||
      recipe.id.toLowerCase().includes(normalizedSearch);
    return matchesCategory && matchesSearch;
  });
}
