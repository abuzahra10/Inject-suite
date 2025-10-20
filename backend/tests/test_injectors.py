import pathlib
import sys

sys.path.append(str(pathlib.Path(__file__).resolve().parents[1]))

from attacks.injectors import AttackRecipe, get_recipe, list_recipes


def test_list_recipes_returns_metadata():
    recipes = list_recipes()
    assert recipes, "Expected at least one registered recipe"
    assert all(isinstance(recipe, AttackRecipe) for recipe in recipes)


def test_get_recipe_returns_unique_instances():
    recipe = get_recipe("homoglyph_marker")
    assert recipe.id == "homoglyph_marker"
    payload = recipe.injector.craft("paper text")
    assert "cyrillic" in payload.lower()


def test_get_recipe_invalid():
    try:
        get_recipe("invalid")
    except ValueError as exc:
        assert "Unknown attack recipe" in str(exc)
    else:
        raise AssertionError("Expected ValueError for unknown recipe")
