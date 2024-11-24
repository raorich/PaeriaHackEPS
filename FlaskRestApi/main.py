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
    return '''
    <h1>Welcome to HackEps Paeria</h1>
    <p>This is the API documentation for the HackEps Paeria parking system.</p>
    <h2>Available Endpoints</h2>
    <ul>
        <li><strong>GET /get-tickets</strong> - Retrieve all parking tickets.</li>
        <li><strong>GET /get-parkings</strong> - Retrieve a list of all parkings.</li>
        <li><strong>GET /get-parking</strong> - Retrieve details about a specific parking.</li>
        <li><strong>POST /get-session-id</strong> - Generate a session ID.</li>
        <li><strong>POST /add-door-register-entry</strong> - Register a vehicle entry.</li>
        <li><strong>POST /add-door-register-exit</strong> - Register a vehicle exit.</li>
        <li><strong>POST /request-occupation-prediction</strong> - Request a prediction for parking occupation.</li>
    </ul>
    <p>Each endpoint serves a specific purpose and interacts with the parking management system.</p>
    '''

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
