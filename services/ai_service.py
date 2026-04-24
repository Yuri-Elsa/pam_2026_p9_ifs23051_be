import logging
import requests
import json
from config import Config

logger = logging.getLogger(__name__)

SYSTEM_PROMPT = """You are a chef. Given ingredients, create ONE recipe.
Respond ONLY with valid JSON, no markdown, no explanation:
{
  "title": "Recipe Title",
  "servings": 2,
  "steps": "Step 1: ...\nStep 2: ...",
  "calories_detail": [{"ingredient": "rice", "amount": "100g", "calories": 130}],
  "calories_total": 130
}"""

REQUIRED_KEYS = {"title", "steps", "calories_total", "calories_detail", "servings"}


def _validate_result(result: dict) -> dict:
    """Validate and sanitize the LLM JSON response."""
    missing = REQUIRED_KEYS - result.keys()
    if missing:
        raise ValueError(f"Incomplete JSON from LLM — missing keys: {missing}")

    result["title"] = str(result["title"]).strip() or "Generated Recipe"
    result["steps"] = str(result["steps"]).strip()
    result["servings"] = max(1, int(result.get("servings", 1)))
    result["calories_total"] = float(result.get("calories_total", 0))

    if not isinstance(result["calories_detail"], list):
        raise ValueError("calories_detail must be a list")

    sanitized_detail = []
    for item in result["calories_detail"]:
        if not isinstance(item, dict):
            continue
        sanitized_detail.append({
            "ingredient": str(item.get("ingredient", "")).strip(),
            "amount":     str(item.get("amount", "")).strip(),
            "calories":   float(item.get("calories", 0)),
        })
    result["calories_detail"] = sanitized_detail

    return result


def generate_recipe(ingredients: list[str]) -> dict:
    ingredients_str = ", ".join(ingredients)

    prompt = f"{SYSTEM_PROMPT}\n\nIngredients: {ingredients_str}"

    payload = {
        "token": Config.LLM_TOKEN,
        "chat": prompt
    }

    response = requests.post(
        f"{Config.LLM_BASE_URL}/llm/chat",
        json=payload,
        timeout=60
    )

    if response.status_code != 200:
        logger.error("LLM API error: status=%s body=%s", response.status_code, response.text[:500])
        raise Exception("LLM API returned non-200 status")

    data = response.json()

    # Ambil content dari response delcom.org
    content = None
    if isinstance(data, dict):
        content = data.get("response") or data.get("message") or data.get("content") or data.get("text")
        if not content and "choices" in data:
            content = data["choices"][0]["message"]["content"]
    elif isinstance(data, str):
        content = data

    if not content:
        logger.error("Unexpected LLM response structure: %s", str(data)[:500])
        raise ValueError("Cannot extract content from LLM response")

    # Strip markdown code fences if present
    content = content.strip()
    if content.startswith("```"):
        content = content.split("```")[1]
        if content.startswith("json"):
            content = content[4:]
    content = content.strip()

    try:
        result = json.loads(content)
    except json.JSONDecodeError as e:
        logger.error("LLM returned invalid JSON: %s | raw content: %s", e, content[:500])
        raise ValueError("LLM returned invalid JSON") from e

    return _validate_result(result)