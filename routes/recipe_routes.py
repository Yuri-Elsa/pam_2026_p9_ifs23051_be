import logging
from flask import Blueprint, request, jsonify
from flask_jwt_extended import jwt_required, get_jwt_identity
from extensions import db, limiter
from models.recipe import Recipe
from services.ai_service import generate_recipe
import json

logger = logging.getLogger(__name__)

recipe_bp = Blueprint("recipes", __name__)


@recipe_bp.route("", methods=["GET"])
@jwt_required()
def get_recipes():
    user_id = int(get_jwt_identity())

    page = request.args.get("page", 1, type=int)
    per_page = request.args.get("per_page", 10, type=int)
    per_page = min(per_page, 50)  # Batasi maksimal 50 per halaman

    pagination = Recipe.query.filter_by(user_id=user_id)\
        .order_by(Recipe.created_at.desc())\
        .paginate(page=page, per_page=per_page, error_out=False)

    return jsonify({
        "data": [r.to_dict() for r in pagination.items],
        "total": pagination.total,
        "page": pagination.page,
        "per_page": pagination.per_page,
        "pages": pagination.pages
    }), 200


@recipe_bp.route("/<int:recipe_id>", methods=["GET"])
@jwt_required()
def get_recipe(recipe_id):
    user_id = int(get_jwt_identity())
    recipe = Recipe.query.filter_by(id=recipe_id, user_id=user_id).first()

    if not recipe:
        return jsonify({"message": "Recipe not found"}), 404

    return jsonify({"data": recipe.to_dict()}), 200


@recipe_bp.route("/generate", methods=["POST"])
@jwt_required()
@limiter.limit("10 per minute;50 per day")  # Lindungi endpoint LLM berbayar
def generate():
    user_id = int(get_jwt_identity())
    data = request.get_json()

    if not data or not data.get("ingredients"):
        return jsonify({"message": "ingredients (list or string) is required"}), 400

    raw = data["ingredients"]
    if isinstance(raw, str):
        ingredients = [i.strip() for i in raw.split(",") if i.strip()]
    elif isinstance(raw, list):
        ingredients = [i.strip() for i in raw if i.strip()]
    else:
        return jsonify({"message": "ingredients must be a string or list"}), 400

    if not ingredients:
        return jsonify({"message": "At least one ingredient is required"}), 400

    try:
        result = generate_recipe(ingredients)
    except Exception as e:
        # Log detail error di server, jangan bocorkan ke client
        logger.error("AI generation failed for user %s: %s", user_id, str(e))
        return jsonify({"message": "Failed to generate recipe. Please try again later."}), 500

    recipe = Recipe(
        user_id=user_id,
        ingredients=", ".join(ingredients),
        title=result.get("title", "Generated Recipe"),
        steps=result.get("steps", ""),
        calories_total=result.get("calories_total", 0),
        calories_detail=json.dumps(result.get("calories_detail", [])),
        servings=result.get("servings", 1)
    )

    db.session.add(recipe)
    db.session.commit()

    return jsonify({"data": recipe.to_dict()}), 200


@recipe_bp.route("/<int:recipe_id>", methods=["DELETE"])
@jwt_required()
def delete_recipe(recipe_id):
    user_id = int(get_jwt_identity())
    recipe = Recipe.query.filter_by(id=recipe_id, user_id=user_id).first()

    if not recipe:
        return jsonify({"message": "Recipe not found"}), 404

    db.session.delete(recipe)
    db.session.commit()

    return jsonify({"message": "Recipe deleted"}), 200