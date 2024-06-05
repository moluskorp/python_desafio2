from database import db
from flask_login import UserMixin

class Lunch(db.Model, UserMixin):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(300), nullable=False, unique=True)
    description = db.Column(db.String(100), nullable=False)
    date = db.Column(db.Date(), nullable=False)
    diet = db.Column(db.Boolean(), default=True)
    id_user = db.Column(db.Integer, nullable=False)

    def to_dict(self):
        return {
            "id": self.id,
            "name": self.name,
            "description": self.description,
            "diet": self.diet,
            "date": self.date.isoformat(),
            "id_user": self.id_user
        }