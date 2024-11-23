import datetime
from flask import Flask, request, jsonify 
from models import db, Parking

# Configuración del servidor Flask
app = Flask(__name__)
port = 5000

# Configuración de conexión a PostgreSQL
app.config['SQLALCHEMY_DATABASE_URI'] = 'postgresql://root:hackeps@172.16.143.120:5432/parking_hackeps'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

db.init_app(app)

@app.route('/')
def hello_world():
    return 'Api index'

@app.route('/get-parkings')
def test_db():
    try:
        parkings = Parking.query.all()
        return {"success": True, "data": [p.name for p in parkings]}
    except Exception as e:
        return {"success": False, "error": str(e)}
    

@app.route('/add-parking', methods=['POST'])
def add_parking():
    try:
        data = request.get_json()
        name = data.get('name')

        if not name:
            return jsonify({"success": False, "error": "El campo 'name' es obligatorio"}), 400

        new_parking = Parking(name=name)
        db.session.add(new_parking)
        db.session.commit()

        return jsonify({"success": True, "message": "Parking creado exitosamente", "parking": {"id": new_parking.id, "name": new_parking.name}})
    except Exception as e:
        return jsonify({"success": False, "error": str(e)}), 500


# Crear tablas automáticamente en modo desarrollo
with app.app_context():
    db.create_all()

# Levantar el servidor
if __name__ == '__main__':
    app.run(host='0.0.0.0', debug=True, port=port)
