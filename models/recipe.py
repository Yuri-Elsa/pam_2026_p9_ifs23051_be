from extensions import db
from datetime import datetime

class Recipe(db.Model):
    __tablename__ = "recipes"

    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey("users.id"), nullable=False)
    ingredients = db.Column(db.Text, nullable=False)       # comma-separated input
    title = db.Column(db.String(256), nullable=False)
    steps = db.Column(db.Text, nullable=False)              # full recipe steps
    calories_total = db.Column(db.Float, nullable=False, default=0)
    calories_detail = db.Column(db.Text, nullable=True)     # JSON string
    servings = db.Column(db.Integer, default=1)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    def to_dict(self):
        import json
        return {
            "id": self.id,
            "user_id": self.user_id,
            "ingredients": self.ingredients,
            "title": self.title,
            "steps": self.steps,
            "calories_total": self.calories_total,
            "calories_detail": json.loads(self.calories_detail) if self.calories_detail else [],
            "servings": self.servings,
            "created_at": self.created_at.isoformat()
        }
