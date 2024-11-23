from flask_sqlalchemy import SQLAlchemy
import datetime
# Inicializar SQLAlchemy
db = SQLAlchemy()

class Parking(db.Model):
    __tablename__ = 'parkings'
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(255), nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.datetime.now)
