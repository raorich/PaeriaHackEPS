from api_requests import *
from datetime import datetime
import config # Import the config module
import logs

def main():
    """
    Main program execution.
    """
    # Load the configuration from file or create a new one
    config_data = config.load_config()

    # Display loaded configuration
    logs.info("Current Configuration:")
    for key, value in config_data.items():
        logs.info(f"  {key}: {value}")

    # Calculate and display session timing
    logs.info("Session Details:")
    logs.info(f"  Session started at: {config_data['time_created']}")

    # Proceed with the main logic
    logs.info("Starting the parking sensor program...")
    
    # Request session ID
    session_id = request_controller_id(f"{config_data["server_address"]}/get-session-id")
    if session_id:
        # Save session ID
        config.config_json["session_id"] = session_id
        config.save_config()
    
    print("Start parking monitorization")
    request_tiquet_info(f"{config_data["server_address"]}/add-door-register-entry")

    #register_parking_exit(f"{config_data["server_address"]}/add-door-register-exit",11)

if __name__ == "__main__":
    main()
