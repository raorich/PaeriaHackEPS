import requests
import config
import logs

def request_controller_id(server_address, parking_id, mac):
    """
    Send a request to the server to get a unique controller ID.
    
    Args:
        server_address (str): The URL of the server.
        parking_id (str): The parking ID for the request.
    
    Returns:
        str: The controller ID if the request is successful, None otherwise.
    """
    payload = {
        "parking_id": parking_id,
        "mac": mac,
    }

    """
    Response: 
        "session_id": ""
        "parking_id": ""
        "mac": ""
        
    """

    try:
        print("Requesting controller ID from the server...")
        response = requests.post(server_address, json=payload)
        response.raise_for_status()  # Raise an error for HTTP error codes
        
        # Extract the controller ID from the response
        data = response.json().get("data",{})

        # Store data credentials
        session_id_response = data.get("session_id")
        parking_id_response = data.get("parking_id")
        mac_response = data.get("mac")

        # Verify data response
        if mac_response == config.config_json["MAC"]:
            if parking_id_response == config.config_json["parking_id"]:
                if session_id_response:
                    logs.info(f"Received correct session ID: {session_id_response}")
                    return session_id_response
                else:
                    logs.warning("Server response did not contain a controller ID. Ignoring...")
            else:
                logs.warning(f"Received incorrect Parking ID {parking_id_response}. Ignoring...")    
        else:
            logs.warning(f"[DEBUG] Received incorrect MAC {mac_response}. Ignoring...")

        # Return none as fail return
        return None

    except requests.exceptions.RequestException as e:
        logs.error(f"Failed to request controller ID: {e}")
        return None
