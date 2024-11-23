import api_requests as api
from datetime import datetime
import config # Import the config module
import logs
import beam
import signal

def handle_sigusr1(sig, frame):
    """
    This function is called when SIGUSR1 is received.
    For now, it logs a message.
    """
    print("Received SIGUSR1: Switching operating mode.")
    if config.config_json["mode"] == "entry":
        config.config_json["mode"] = "exit"
        print("State changed to: exit")
    else:
        config.config_json["mode"] = "entry"
        print("State changed to: entry")
    
    config.save_config()

def main():
    """
    Main program execution.
    """
    # Handle USR1 signal
    signal.signal(signal.SIGUSR1, handle_sigusr1)

    # Load the configuration from file or create a new one
    config_data = config.load_config()

    # Display loaded configuration
    logs.info("Current Configuration:")
    for key, value in config_data.items():
        logs.info(f"  {key}: {value}")

    # Calculate and display session timing
    logs.info("Session Details:")
    logs.info(f"Session started at: {config_data['time_created']}")

    # Proceed with the main logic
    logs.info("Starting the parking sensor program...")
    
    # Request session ID
    session_id = api.request_controller_id(f"{config_data['server_address']}/get-session-id")
    if session_id:
        # Save session ID
        config.config_json["session_id"] = session_id
        config.save_config()
    
    print("Starting parking monitorization...")

    try:
        # Initialize the beam sensjor
        beam.start()
        input()
    except KeyboardInterrupt:
        beam.clean_up()
        logs.info("Controller stopped.")

if __name__ == "__main__":
    main()
