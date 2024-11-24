import main
import logs

def get_tickets():
    try:
        # Get request arguments
        parking_id = main.request.args.get("parking_id",None)
        active = main.request.args.get("active",None)
        
        # Get session from the database
        if parking_id is not None:
            parking = main.db.session.get(main.Parking, parking_id)
            if not parking:
                logs.fail("Unable to query parking id while proceding with tickets request.")
                return main.jsonify({"success": False, "error": "Parking ID not found in the database"}), 400

            # If the tickets don't have a value assigned execute request withouth active value
            if active is None:
                filter_tickets = main.Ticket.query.filter_by(parking_id=parking_id)
            else:
                filter_tickets = main.Ticket.query.filter_by(parking_id=parking_id, active=active)
        else:
            filter_tickets = main.Ticket.query.filter_by(active=active)
        
        # Initialise tickets list 
        tickets_list = []
        # Store tickets
        for ticket in filter_tickets:
            tickets_list.append({
                'id': ticket.id,
                'ubication': ticket.ubication,
                'parking_id': ticket.parking_id,
                'active': ticket.active
            })
        
        # Return tickets request
        return main.jsonify({
            "success": True,
            "data": tickets_list
        }), 200

    except Exception as e:
        logs.fail("Unexpected error when retrieving tickets.")
        return main.jsonify({
            "success": False,
            "error": str(e)
        }), 500
