import datetime
import pandas as pd
import src.prediction
import src.session 
import src.door
import src.tickets
import src.parking

from flask import Flask, request, jsonify 
from sqlalchemy import text
from flask_cors import CORS

from models import db, Parking, Controller, Ticket, TypeRegister, DoorRegisters, History

# Configuración del servidor Flask
app = Flask(__name__)
CORS(app)
port = 5000

# Configuración de conexión a PostgreSQL
app.config['SQLALCHEMY_DATABASE_URI'] = 'postgresql://root:hackeps@172.16.143.120:5432/parking_hackeps'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

db.init_app(app)

@app.route('/')
def index():
    return 'Welcome to HackEps Paeria'

@app.route('/get-session-id', methods=['POST'])
def handle_get_session():
    return src.session.get_session_id()

@app.route('/get-tickets', methods=['GET'])
def handle_get_tickets():
    return src.tickets.get_tickets()

@app.route('/get-parkings', methods=['GET'])
def handle_get_parkings():
    return src.parking.get_parkings()

@app.route('/get-parking', methods=['GET'])
def handle_get_parking():
    return src.parking.get_parking()

@app.route('/add-door-register-entry', methods=['POST'])
def handle_door_entry():
    return src.door.assign_parking_spot()

@app.route('/add-door-register-exit', methods=['POST'])
def handle_door_exit():
    return src.door.remove_parking_spot()

@app.route('/request-occupation-prediction', methods=['POST'])
def handle_parking_occupation():
    return src.prediction.predict_parking_occupation()

# Crear tablas automáticamente en modo desarrollo
with app.app_context():
    db.create_all()

# Levantar el servidor
if __name__ == '__main__':
    app.run(host='0.0.0.0', debug=True, port=port)
