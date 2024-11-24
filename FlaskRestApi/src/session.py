import main
import random
import string
import logs

def get_session_id():
    """
    Handles the process of generating and returning a session ID for a controller in a parking system.

    This function retrieves the 'parking_id' and 'mac' from the request data, verifies their validity, 
    checks the existence of the associated parking and controller in the database, and generates a 
    session ID for the controller. The session ID is then updated in the database. In case of any issues,
    appropriate error responses are returned.

    Returns:
        JSON response indicating success or failure along with an error message.
    """
    try:
        # Get data as json format
        data = main.request.get_json()

        parking_id = data.get('parking_id', None)
        mac = data.get('mac', None)

        # Paquet values
        if parking_id == None:
            logs.fail("Unable to proceed with session request: parking_id in request is null.")
            return main.jsonify({"success": False, "error": "None value recived in 'parking_id' field"}), 400
            
        if parking_id == None:
            logs.fail("Unable to proceed with session request: mac in request is null")
            return main.jsonify({"success": False, "error": "None value recived in 'mac' field"}), 400

        # Get parking identifier in database
        parking = main.db.session.get(main.Parking, parking_id)
        if not parking:
            logs.fail("Unable to proceed with session request: Parking ID does not exist")
            return main.jsonify({"success": False, "error": "Parking ID does not exist"}), 400
        
        # Get controller identifier
        controller = main.Controller.query.filter_by(parking_id=parking_id, mac=mac).first()
        if not controller:
            logs.fail("Unable to proceed with session request: Controller does not exist")
            return main.jsonify({"success": False, "error": "Controller does not exist"}), 400
        
        # Generate random session ID string
        session_id = session_id_generator(parking_id)

        # Update data base session for the specified controller
        query = main.text("UPDATE controller SET session_id = :session_id WHERE parking_id = :parking_id AND mac = :mac")
        main.db.session.execute(query, 
            {
                'session_id': session_id, 
                'parking_id': parking_id, 
                'mac': mac
            }
        )
        main.db.session.commit() 

        logs.info(f"Generated session identifier: {session_id} for controller: {mac}")
        # Return requested data
        return {
            "success": True, 
            "data": {
                "session_id": session_id,
                "parking_id": parking.id,
                "mac" : controller.mac
            }
        }
    
    except Exception as e:
        logs.error("Unexpected error when trying to get controller session ID")
        return {"success": False, "Unexpected error when trying to get controller session ID": str(e)}

def session_id_generator(pk, min_length=10, max_length=20):
    '''
    Generates a random session identifier
    '''
    seed = "SESSION"

    length = random.randint(min_length, max_length)
    value = ''.join(random.choices(string.ascii_uppercase, k=length))
    return f'{seed}-{pk}-{value}'