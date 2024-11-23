import datetime
from flask import Flask, request, jsonify 
from sqlalchemy import text
from functions import (
    session_id_generator
)
from models import db, Parking, Controller, Ticket, TypeRegister, DoorRegisters, History

# Configuración del servidor Flask
app = Flask(__name__)
port = 5000

# Configuración de conexión a PostgreSQL
app.config['SQLALCHEMY_DATABASE_URI'] = 'postgresql://root:hackeps@172.16.143.120:5432/parking_hackeps'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

db.init_app(app)

@app.route('/')
def index():
    return 'Welcome to HackEps Paeria'

@app.route('/get-session-id', methods=['POST'])
def get_session_id():
    try:
        data = request.get_json()

        parking_id = data.get('parking_id', None)
        mac = data.get('mac', None)

        #validate values
        if None in [parking_id, mac]:
            return jsonify({"success": False, "error": "None value recived"}), 400

        parking = db.session.get(Parking, parking_id)
        if not parking:
            return jsonify({"success": False, "error": "Parking ID do not exists"}), 400
        
        controller = Controller.query.filter_by(parking_id=parking_id, mac=mac).first()
        if not controller:
            return jsonify({"success": False, "error": "Controller do not exists"}), 400
        
        session_id = session_id_generator(parking_id)
        query = text("UPDATE controller SET session_id = :session_id WHERE parking_id = :parking_id AND mac = :mac")
        db.session.execute(query, {'session_id': session_id, 'parking_id': parking_id, 'mac': mac})
        db.session.commit() 
        
        return {"success": True, "data": {
                "session_id": session_id,
                "parking_id": parking.id,
                "mac" : controller.mac
            }
        }
    except Exception as e:
        print(e)
        return {"success": False, "error": str(e)}


@app.route('/get-tickets', methods=['GET'])
def get_tickets():
    try:
        parking_id = request.args.get("parking_id",None)
        active = request.args.get("active",False)
        if parking_id is None:
            return jsonify({"success": False, "error": "None value recived"}), 400

        parking = db.session.get(Parking, parking_id)
        if not parking:
            return jsonify({"success": False, "error": "Parking ID do not exists"}), 400
        
        filter_tickets = Ticket.query.filter_by(parking_id=parking_id, active=active)
        
        tickets_list = []
        for ticket in filter_tickets:
            tickets_list.append({
                'id': ticket.id,
                'ubication': ticket.ubication,
                'active': ticket.active
            })
        
        return jsonify({
            "success": True,
            "data": tickets_list
        }), 200

    except Exception as e:
        return jsonify({
            "success": False,
            "error": str(e)
        }), 500

@app.route('/get-parkings', methods=['GET'])
def get_parkings():
    try:
        parkings = Parking.query.all()
        
        parking_list = []
        for parking in parkings:
            parking_list.append({
                'id': parking.id,
                'name': parking.name,
                'location': parking.location,
                'total_capacity': parking.total_capacity,
                'created_at': parking.created_at
            })
        
        return jsonify({
            "success": True,
            "data": parking_list
        }), 200

    except Exception as e:
        return jsonify({
            "success": False,
            "error": str(e)
        }), 500

def create_history_door(type_register_obj, parking_id, ticket_id):
    # create DoorRegisters
    new_door_register = DoorRegisters(
        type_id=type_register_obj.id,
        parking_id=parking_id
    )
    db.session.add(new_door_register)
    db.session.commit()

    # create History
    new_history = History(
        ticket_id=ticket_id,
        door_register_id=new_door_register.id,
        parking_id=parking_id
    )
    db.session.add(new_history)
    db.session.commit()


@app.route('/add-door-register-entry', methods=['POST'])
def add_parking():
    try:
        data = request.get_json()

        parking_id = data.get('parking_id', None)
        session_id = data.get('session_id', None)
        mac = data.get('mac', None)
        #validate values
        if None in [parking_id, session_id, mac]:
            return jsonify({"success": False, "error": "None value recived"}), 400

        parking = db.session.get(Parking, parking_id)
        if not parking:
            return jsonify({"success": False, "error": "Parking ID do not exists"}), 400
        
        controller = Controller.query.filter_by(mac = mac, session_id=session_id).first()
        if not controller:
            return jsonify({"success": False, "error": "Not valid session for this Controller"}), 400
        
        valid_tickets = Ticket.query.filter_by(parking_id=parking_id, active=False).first()
        if not valid_tickets:
            return jsonify({"success": False, "error": "There is no more space, your car cannot enter"}), 200
    
        type_register_obj = db.session.get(TypeRegister, 1)
        if not type_register_obj:
            return jsonify({"success": False, "error": "Type register do not exists"}), 400
        
        ticket_id = valid_tickets.id  
        query = text("UPDATE ticket SET active = :active WHERE id = :ticket_id")
        db.session.execute(query, {'active': True, 'ticket_id': ticket_id})
        db.session.commit()

        create_history_door(
            type_register_obj, 
            parking_id, 
            ticket_id
        )

        return jsonify({
            "success": True,
            "data": {
                "id": valid_tickets.id,
                "ubication": valid_tickets.ubication,
                "parking_id" : parking_id,
                "session_id" : session_id,
                "mac" : mac
            }
        }), 200
    

    except Exception as e:
        print(e)
        return jsonify({"success": False, "error": str(e)}), 500

@app.route('/add-door-register-exit', methods=['POST'])
def parking_exit():
    try:
        data = request.get_json()

        parking_id = data.get('parking_id', None)
        session_id = data.get('session_id', None)
        mac = data.get('mac', None)
        ticket_id = data.get('ticket_id', None)

        #validate values
        if None in [parking_id, session_id, mac, ticket_id]:
            return jsonify({"success": False, "error": "None value recived"}), 400

        parking = db.session.get(Parking, parking_id)
        if not parking:
            return jsonify({"success": False, "error": "Parking ID do not exists"}), 400
        
        controller = Controller.query.filter_by(mac = mac, session_id=session_id).first()
        if not controller:
            return jsonify({"success": False, "error": "Not valid session for this Controller"}), 400

        type_register_obj = db.session.get(TypeRegister, 2)
        if not type_register_obj:
            return jsonify({"success": False, "error": "Type register do not exists"}), 400
        
        query = text("UPDATE ticket SET active = :active WHERE id = :ticket_id")
        db.session.execute(query, {'active': False, 'ticket_id': ticket_id})
        db.session.commit() 
        
        create_history_door(
            type_register_obj, 
            parking_id, 
            ticket_id
        )
        
        return jsonify({
            "success": True,
            "data": {
                "parking_id" : parking_id,
                "session_id" : session_id,
                "mac" : mac
            }
        }), 200
    
    except Exception as e:
        print(e)
        return jsonify({"success": False, "error": str(e)}), 500



# Crear tablas automáticamente en modo desarrollo
with app.app_context():
    db.create_all()

# Levantar el servidor
if __name__ == '__main__':
    app.run(host='0.0.0.0', debug=True, port=port)
