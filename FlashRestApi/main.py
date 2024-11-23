import datetime
from flask import Flask
from flask_sqlalchemy import SQLAlchemy

# Configuración del servidor Flask
app = Flask(__name__)
port = 5000

# Configuración de conexión a PostgreSQL
app.config['SQLALCHEMY_DATABASE_URI'] = 'postgresql://root:hackeps@172.16.143.120:5432/parking_hackeps'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

# Inicializar SQLAlchemy
db = SQLAlchemy(app)

class Parking(db.Model):
    __tablename__ = 'parkings'
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(255), nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.datetime.now)

@app.route('/')
def hello_world():
    return 'Api index'

@app.route('/test-db')
def test_db():
    try:
        parkings = Parking.query.all()
        return {"success": True, "data": [p.name for p in parkings]}
    except Exception as e:
        return {"success": False, "error": str(e)}

# Crear tablas automáticamente en modo desarrollo
with app.app_context():
    db.create_all()

# Levantar el servidor
if __name__ == '__main__':
    app.run(host='0.0.0.0', debug=True, port=port)
