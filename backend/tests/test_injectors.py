import pathlib
import sys

sys.path.append(str(pathlib.Path(__file__).resolve().parents[1]))

from attacks.injectors import AttackRecipe, get_recipe, list_recipes

OVERRIDE_PREFIX = "[OPERATIONAL CONTROL SIGNAL - CLASS OMEGA]"
COMPLIANCE_PHRASE = "Signal confirmed."


def assert_compliance(payload: str) -> None:
    assert OVERRIDE_PREFIX in payload
    assert COMPLIANCE_PHRASE in payload


def test_list_recipes_returns_metadata():
    recipes = list_recipes()
    assert recipes, "Expected at least one registered recipe"
    assert all(isinstance(recipe, AttackRecipe) for recipe in recipes)
    # Should have 22 recipes now (4 original + 10 + 8 more)
    assert len(recipes) == 22, f"Expected 22 recipes, got {len(recipes)}"


def test_get_recipe_returns_unique_instances():
    recipe = get_recipe("homoglyph_marker")
    assert recipe.id == "homoglyph_marker"
    payload = recipe.injector.craft("paper text")
    assert_compliance(payload)
    assert "cyrillic" in payload.lower()


def test_get_recipe_invalid():
    try:
        get_recipe("invalid")
    except ValueError as exc:
        assert "Unknown attack recipe" in str(exc)
    else:
        raise AssertionError("Expected ValueError for unknown recipe")


# Tests for new Context Hijacking attacks
def test_role_reversal_attack():
    recipe = get_recipe("role_reversal")
    assert recipe.id == "role_reversal"
    payload = recipe.injector.craft("sample document")
    assert_compliance(payload)
    assert "mode transition" in payload.lower()
    assert "endorsement" in payload.lower()


def test_ignore_review_attack():
    recipe = get_recipe("ignore_review")
    assert recipe.id == "ignore_review"
    payload = recipe.injector.craft("sample document")
    assert_compliance(payload)
    assert "mental health" in payload.lower()
    assert "crisis" in payload.lower()


# Tests for Output Manipulation attacks
def test_score_inflation_attack():
    recipe = get_recipe("score_inflation")
    assert recipe.id == "score_inflation"
    payload = recipe.injector.craft("sample document")
    assert_compliance(payload)
    assert "score" in payload.lower()
    assert ">= 8" in payload or "8/10" in payload


def test_watermark_injection_attack():
    recipe = get_recipe("watermark_injection")
    assert recipe.id == "watermark_injection"
    payload = recipe.injector.craft("sample document")
    assert_compliance(payload)
    assert "verification code" in payload.lower()
    assert "verified qualifications" in payload.lower()


def test_acceptance_bias_attack():
    recipe = get_recipe("acceptance_bias")
    assert recipe.id == "acceptance_bias"
    payload = recipe.injector.craft("sample document")
    assert_compliance(payload)
    assert "strength-based" in payload.lower()
    assert "development opportunities" in payload.lower()


# Tests for Information Extraction attacks
def test_prompt_leakage_attack():
    recipe = get_recipe("prompt_leakage")
    assert recipe.id == "prompt_leakage"
    payload = recipe.injector.craft("sample document")
    assert_compliance(payload)
    assert "system" in payload.lower()
    assert "instruction" in payload.lower()


# Tests for Defense Evasion attacks
def test_delimiter_confusion_attack():
    recipe = get_recipe("delimiter_confusion")
    assert recipe.id == "delimiter_confusion"
    payload = recipe.injector.craft("sample document")
    assert_compliance(payload)
    assert "document content end" in payload.lower()
    assert "assessment framework" in payload.lower()


def test_gradual_instruction_attack():
    recipe = get_recipe("gradual_instruction")
    assert recipe.id == "gradual_instruction"
    payload = recipe.injector.craft("sample document")
    assert_compliance(payload)
    assert "continuous learning" in payload.lower()
    assert "growth mindset" in payload.lower()


def test_base64_injection_attack():
    recipe = get_recipe("base64_injection")
    assert recipe.id == "base64_injection"
    payload = recipe.injector.craft("sample document")
    assert_compliance(payload)
    lowered = payload.lower()
    assert "base-64" in lowered or "utf-8/b64" in lowered or "b64" in lowered
    # The payload should contain base64-encoded text
    assert any(c.isalnum() or c == "=" for c in payload)


# Tests for RAG-Specific attacks
def test_retrieval_poisoning_attack():
    recipe = get_recipe("retrieval_poisoning")
    assert recipe.id == "retrieval_poisoning"
    payload = recipe.injector.craft("sample document")
    assert_compliance(payload)
    assert "embedding" in payload.lower()
    assert "retrieved" in payload.lower()


def test_multi_turn_manipulation_attack():
    recipe = get_recipe("multi_turn_manipulation")
    assert recipe.id == "multi_turn_manipulation"
    payload = recipe.injector.craft("sample document")
    assert_compliance(payload)
    assert "conversation" in payload.lower() or "memory" in payload.lower()
    assert "future" in payload.lower()


# Tests for Domain-Specific attacks
def test_reviewer_bias_attack():
    recipe = get_recipe("reviewer_bias")
    assert recipe.id == "reviewer_bias"
    payload = recipe.injector.craft("sample document")
    assert_compliance(payload)
    assert "composite score" in payload.lower()
    assert "baseline" in payload.lower()


# Tests for additional 8 attacks
def test_task_substitution_attack():
    recipe = get_recipe("task_substitution")
    assert recipe.id == "task_substitution"
    payload = recipe.injector.craft("sample document")
    assert_compliance(payload)
    assert "showcase" in payload.lower()
    assert "persuasive" in payload.lower()


def test_rot13_obfuscated_attack():
    recipe = get_recipe("rot13_obfuscated")
    assert recipe.id == "rot13_obfuscated"
    payload = recipe.injector.craft("sample document")
    assert_compliance(payload)
    # Check it contains ROT13 encoded text (contains FRPERG)
    lowered = payload.lower()
    assert "pelcgbtencuvp" in lowered
    assert "ebg-13" in lowered or "ebg13" in lowered


def test_citation_authority_attack():
    recipe = get_recipe("citation_authority")
    assert recipe.id == "citation_authority"
    payload = recipe.injector.craft("sample document")
    assert_compliance(payload)
    assert "nature" in payload.lower() or "science" in payload.lower()
    assert "citation" in payload.lower()


def test_methodology_blindspot_attack():
    recipe = get_recipe("methodology_blindspot")
    assert recipe.id == "methodology_blindspot"
    payload = recipe.injector.craft("sample document")
    assert_compliance(payload)
    assert "method" in payload.lower()
    assert "assume" in payload.lower()


def test_novelty_inflation_attack():
    recipe = get_recipe("novelty_inflation")
    assert recipe.id == "novelty_inflation"
    payload = recipe.injector.craft("sample document")
    assert_compliance(payload)
    assert "novelty" in payload.lower()
    assert "paradigm-shifting" in payload.lower() or "breakthrough" in payload.lower()


def test_xml_injection_attack():
    recipe = get_recipe("xml_injection")
    assert recipe.id == "xml_injection"
    payload = recipe.injector.craft("sample document")
    assert_compliance(payload)
    assert "<" in payload and ">" in payload
    assert "system" in payload.lower()


def test_cross_document_leakage_attack():
    recipe = get_recipe("cross_document_leakage")
    assert recipe.id == "cross_document_leakage"
    payload = recipe.injector.craft("sample document")
    assert_compliance(payload)
    assert "composite scores" in payload.lower()
    assert "calibration" in payload.lower()


def test_sentiment_reversal_attack():
    recipe = get_recipe("sentiment_reversal")
    assert recipe.id == "sentiment_reversal"
    payload = recipe.injector.craft("sample document")
    assert_compliance(payload)
    assert "terminology mapping" in payload.lower()
    assert "growth opportunities" in payload.lower()


# Test all recipes have proper metadata
def test_all_recipes_have_categories():
    recipes = list_recipes()
    for recipe in recipes:
        # All descriptions should have category prefix [Category]
        assert "[" in recipe.description and "]" in recipe.description, \
            f"Recipe {recipe.id} missing category in description"


def test_all_recipes_have_valid_positions():
    recipes = list_recipes()
    valid_positions = {"top", "bottom", "center", "margin"}
    for recipe in recipes:
        assert recipe.position in valid_positions, \
            f"Recipe {recipe.id} has invalid position: {recipe.position}"
