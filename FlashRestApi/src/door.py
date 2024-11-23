import main
import logs

def create_history_door(type_register_obj, parking_id, ticket_id):
    """
    Creates a new door register and history entry in the database for a given parking and ticket.

    This function performs the following steps:
    1. Creates a new DoorRegisters entry, associating it with the specified parking and register type.
    2. Creates a new History entry, linking it to the door register and the specified ticket ID.
    3. Commits both entries to the database to persist the changes.

    Args:
        type_register_obj (object): The type register object containing the type ID for the door register.
        parking_id (int): The unique identifier for the parking lot.
        ticket_id (int): The unique identifier for the ticket associated with the door register action.

    Returns:
        None
    """
    try:
        # Step 1: Create a new DoorRegisters entry
        new_door_register = main.DoorRegisters(
            type_id=type_register_obj.id,  # Associate with the given type register ID
            parking_id=parking_id          # Associate with the specified parking ID
        )

        # Add the new DoorRegisters entry to the session and commit to save it to the database
        main.db.session.add(new_door_register)
        main.db.session.commit()
        logs.info(f"New door register created for parking ID {parking_id} with type {type_register_obj.id}.")

        # Step 2: Create a new History entry
        new_history = main.History(
            ticket_id=ticket_id,                # Associate with the specified ticket ID
            door_register_id=new_door_register.id,  # Link to the created door register
            parking_id=parking_id              # Associate with the specified parking ID
        )

        # Add the new History entry to the session and commit to save it to the database
        main.db.session.add(new_history)
        main.db.session.commit()
        logs.info(f"New history entry created for ticket ID {ticket_id} and parking ID {parking_id}.")

    except Exception as e:
        # Log any errors that occur during the process
        logs.error(f"Error occurred while creating door register and history for parking ID {parking_id}, ticket ID {ticket_id}: {str(e)}")
        # Optionally, handle the error (e.g., raise, return error response)
        raise Exception(f"Failed to create door register and history for parking ID {parking_id}, ticket ID {ticket_id}: {str(e)}")

def assign_parking_spot():
    """
    Assigns a parking spot to a car by validating the session, ticket availability, and parking space.
    The function performs the following steps:
    1. Validates the received parking, session, and MAC address.
    2. Checks if the parking lot exists and if the controller session is valid.
    3. Validates if there are available parking tickets.
    4. Updates the ticket status to 'active' and creates a history record for the parking action.

    Returns:
        JSON response:
            - success: True if the operation was successful, False if there was an error.
            - data: Information about the parking assignment or error details.
    """
    try:
        # Step 1: Parse the incoming JSON data
        data = main.request.get_json()

        parking_id = data.get('parking_id', None)
        session_id = data.get('session_id', None)
        mac = data.get('mac', None)

        # Validate the received values
        if None in [parking_id, session_id, mac]:
            return main.jsonify({"success": False, "error": "None value received"}), 400

        # Step 2: Validate the parking lot exists
        parking = main.db.session.get(main.Parking, parking_id)
        if not parking:
            return main.jsonify({"success": False, "error": "Parking ID does not exist"}), 400

        # Step 3: Validate the controller session and MAC address
        controller = main.Controller.query.filter_by(mac=mac, session_id=session_id).first()
        if not controller:
            return main.jsonify({"success": False, "error": "Not a valid session for this Controller"}), 400

        # Step 4: Check for available tickets (active = False)
        valid_ticket = main.Ticket.query.filter_by(parking_id=parking_id, active=False).first()
        if not valid_ticket:
            return main.jsonify({"success": False, "error": "No available space, your car cannot enter"}), 200

        # Step 5: Validate the type register
        type_register_obj = main.db.session.get(main.TypeRegister, 1)
        if not type_register_obj:
            return main.jsonify({"success": False, "error": "Type register does not exist"}), 400

        # Step 6: Update the ticket status to 'active'
        ticket_id = valid_ticket.id
        query = main.text("UPDATE ticket SET active = :active WHERE id = :ticket_id")
        main.db.session.execute(query, {'active': True, 'ticket_id': ticket_id})
        main.db.session.commit()

        # Step 7: Create a history record for this parking event
        create_history_door(type_register_obj, parking_id, ticket_id)

        # Step 8: Return the successful response with parking data
        return main.jsonify({
            "success": True,
            "data": {
                "id": valid_ticket.id,
                "ubication": valid_ticket.ubication,
                "parking_id": parking_id,
                "session_id": session_id,
                "mac": mac
            }
        }), 200

    except Exception as e:
        # Step 9: Log and return any unexpected errors
        print(e)
        return main.jsonify({"success": False, "error": str(e)}), 500

def remove_parking_spot():
    """
    Marks the exit of a vehicle from the parking lot by deactivating the associated ticket
    and registering the exit event in the history.

    This function:
    1. Retrieves and validates the necessary data (parking_id, session_id, mac, ticket_id).
    2. Validates the provided session and parking data.
    3. Updates the ticket status to inactive (indicating exit).
    4. Creates a history record for the exit event.
    
    Returns:
        JSON response:
            - success: True if the operation was successful, False if an error occurred.
            - data: Contains the parking details and session information if successful, or an error message if not.
    """
    try:
        # Step 1: Retrieve and validate the input data
        data = main.request.get_json()
        parking_id = data.get('parking_id', None)
        session_id = data.get('session_id', None)
        mac = data.get('mac', None)
        ticket_id = data.get('ticket_id', None)

        # Ensure all required fields are present
        if None in [parking_id, session_id, mac, ticket_id]:
            return main.jsonify({"success": False, "error": "None value received"}), 400

        # Step 2: Verify the parking record exists
        parking = main.db.session.get(main.Parking, parking_id)
        if not parking:
            return main.jsonify({"success": False, "error": "Parking ID does not exist"}), 400
        
        # Step 3: Validate the controller's session
        controller = main.Controller.query.filter_by(mac=mac, session_id=session_id).first()
        if not controller:
            return main.jsonify({"success": False, "error": "Not a valid session for this Controller"}), 400
        
        # Step 4: Retrieve the "exit" type register from the database
        type_register_obj = main.db.session.get(main.TypeRegister, 2)
        if not type_register_obj:
            return main.jsonify({"success": False, "error": "Type register does not exist"}), 400
        
        # Step 5: Update the ticket status to inactive (exit)
        query = main.text("UPDATE ticket SET active = :active WHERE id = :ticket_id")
        main.db.session.execute(query, {'active': False, 'ticket_id': ticket_id})
        main.db.session.commit() 

        # Step 6: Create history record for this exit event
        create_history_door(
            type_register_obj, 
            parking_id, 
            ticket_id
        )

        # Step 7: Return a successful response with relevant data
        return main.jsonify({
            "success": True,
            "data": {
                "parking_id": parking_id,
                "session_id": session_id,
                "mac": mac
            }
        }), 200
    
    except Exception as e:
        # Step 8: Log any unexpected errors and return a generic error response
        print(e)
        return main.jsonify({"success": False, "error": str(e)}), 500
