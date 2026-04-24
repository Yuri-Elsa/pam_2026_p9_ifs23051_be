import logging
import requests
import json
from config import Config

logger = logging.getLogger(__name__)

SYSTEM_PROMPT = """You are a professional chef and nutritionist. 
When given a list of ingredients, you generate ONE complete recipe and calculate the calorie count.

You MUST respond ONLY with valid JSON, no markdown, no explanation, just raw JSON like this:
{
  "title": "Recipe Title",
  "servings": 2,
  "steps": "Step 1: ...\nStep 2: ...\nStep 3: ...",
  "calories_detail": [
    {"ingredient": "rice", "amount": "100g", "calories": 130},
    {"ingredient": "egg", "amount": "2 pcs", "calories": 156}
  ],
  "calories_total": 286
}"""


def generate_recipe(ingredients: list[str]) -> dict:
    ingredients_str = ", ".join(ingredients)

    user_message = f"""Please create a recipe using these ingredients: {ingredients_str}

Calculate the calorie content for each ingredient used and the total calories.
Respond ONLY with JSON, no extra text."""

    headers = {
        "Authorization": f"Bearer {Config.LLM_TOKEN}",
        "Content-Type": "application/json"
    }

    payload = {
        "model": Config.LLM_MODEL,
        "messages": [
            {"role": "system", "content": SYSTEM_PROMPT},
            {"role": "user", "content": user_message}
        ],
        "temperature": 0.7,
        "max_tokens": 1500
    }

    response = requests.post(
        f"{Config.LLM_BASE_URL}/chat/completions",
        headers=headers,
        json=payload,
        timeout=60
    )

    if response.status_code != 200:
        # Log detail untuk debugging server-side, jangan expose ke client
        logger.error("LLM API error: status=%s body=%s", response.status_code, response.text[:500])
        raise Exception("LLM API returned non-200 status")

    data = response.json()
    content = data["choices"][0]["message"]["content"]

    # Strip markdown code fences if present
    content = content.strip()
    if content.startswith("```"):
        content = content.split("```")[1]
        if content.startswith("json"):
            content = content[4:]
    content = content.strip()

    result = json.loads(content)
    return result