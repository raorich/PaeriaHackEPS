elimport datetime
import pandas as pd
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
def predict_parking_occupation():
    
    # Parse input data
    data = request.get_json()
    parking_id = data.get("parking_id")

    if not parking_id:
        return jsonify({"error": "parking_id is required"}), 400

    # Get the current time
    current_time = datetime.datetime.now()

    # Query historical data for the given parking ID
    history_data = History.query.filter_by(parking_id=parking_id).all()

    # Convert query results to a DataFrame
    df = pd.DataFrame([{
        "timestamp": record.timestamp,
        "occupied_slots": record.occupied_slots
    } for record in history_data])

    # Extract day of the week and hour for grouping
    df["day_of_week"] = df["timestamp"].dt.weekday
    df["hour"] = df["timestamp"].dt.hour

    # Prepare data for prediction
    current_time = datetime.datetime.now()
    predictions = []

    for i in range(7):  # For each of the next 7 days
        target_time = current_time + datetime.timedelta(days=i)
        target_day_of_week = target_time.weekday()  # Get the day of the week for next i days

        # Filter historical data for the same day of the week
        historical_data = df[df["day_of_week"] == target_day_of_week]

        if historical_data.empty:
            return jsonify({"error": f"No historical data for the same day of the week on day {i+1}"}), 404

        # Calculate the average occupied slots for each hour on that day of the week
        hour_occupation = (
            historical_data.groupby("hour")["occupied_slots"]
            .mean()
            .reset_index()
        )

        # Generate predictions for each hour of the day (0-23) for the target day
        for hour in range(24):
            prediction = hour_occupation[hour_occupation["hour"] == hour]["occupied_slots"]
            if prediction.empty:
                prediction = 0
            else:
                prediction = prediction.iloc[0]

            predictions.append({
                "hour": hour,
                "day": target_time.strftime("%Y-%m-%d"),
                "predicted_occupied_slots": prediction,
            })

    # Return the list of predictions for the next 7 days (24 hours each)
    return jsonify(predictions)

    

# Crear tablas automáticamente en modo desarrollo
with app.app_context():
    db.create_all()

# Levantar el servidor
if __name__ == '__main__':
    app.run(host='0.0.0.0', debug=True, port=port)
