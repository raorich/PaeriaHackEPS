import main
import logs

def get_parkings():
    """
    Fetches a list of all parking entries from the database and returns them in a structured JSON response.

    This function queries the database for all Parking records, formats the results into a list of dictionaries,
    and returns a JSON response containing the parking details. If an error occurs, an error response is returned.

    Returns:
        JSON response:
            - success: True if the operation was successful, False if an error occurred.
            - data: List of parking details if successful, or an error message if an error occurred.
    """
    try:
        # Step 1: Query the database to get all parking records
        parkings = main.Parking.query.all()

        # Step 2: Format the parking data into a list of dictionaries
        parking_list = []
        for parking in parkings:
            parking_list.append({
                'id': parking.id,               # Unique parking ID
                'name': parking.name,           # Name of the parking
                'location': parking.location,   # Location of the parking
                'latitude': parking.latitude,   # Latitude of the parking
                'longitude': parking.longitude,   # Longitude of the parking
                'total_capacity': parking.total_capacity,  # Total capacity of the parking lot
                'created_at': parking.created_at   # Creation date of the parking entry
            })

        # Step 3: Return a successful JSON response with parking data
        return main.jsonify({
            "success": True,
            "data": parking_list
        }), 200

    except Exception as e:
        # Step 4: Log the error and return an error response
        logs.error(f"Error occurred while fetching parkings: {str(e)}")
        return main.jsonify({
            "success": False,
            "error": str(e)
        }), 500

def get_parking():
    """
    Fetches a parking record from the database based on the provided parking_id.
    
    This function performs the following steps:
    1. Retrieves the parking_id from the request arguments.
    2. Verifies the validity of the parking_id.
    3. Queries the database for the parking record corresponding to the provided parking_id.
    4. Returns a JSON response with the parking data or an error message if the operation fails.
    
    Returns:
        JSON response:
            - success: True if the operation was successful, False if an error occurred.
            - data: The parking data if successful, or an error message if an error occurred.
    """
    try:
        # Step 1: Retrieve the parking_id from the request arguments
        parking_id = main.request.args.get("parking_id", None)

        # Step 2: Validate the parking_id argument
        if parking_id is None:
            logs.fail("Unable to proceed with parking request: parking_id in request is null.")
            return main.jsonify({"success": False, "error": "Received None value as parking_id"}), 400
        
        # Step 3: Query the database to get the parking record
        parking = main.db.session.get(main.Parking, parking_id)
        if not parking:
            logs.fail(f"Parking ID {parking_id} not found in the database.")
            return main.jsonify({"success": False, "error": "Parking ID not found in the database"}), 400
        
        # Step 4: Return the parking data in the response
        return main.jsonify({
            "success": True,
            "data": {
                "id": parking.id,
                "name": parking.name,
                "location": parking.location,
                'latitude': parking.latitude,   # Latitude of the parking
                'longitude': parking.longitude,   # Longitude of the parking
                "total_capacity": parking.total_capacity,
                "created_at": parking.created_at
            }
        }), 200
    
    except Exception as e:
        # Step 5: Log unexpected errors and return an error response
        logs.error(f"Unexpected error occurred while fetching parking: {str(e)}")
        return main.jsonify({
            "success": False,
            "error": str(e)
        }), 500
