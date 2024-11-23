import os
import json
from datetime import datetime
import logs

CONFIG_FILE = "config.json"

# Define a global dictionary to hold the configuration
config_json = {}

def generate_config():
    """
    Generate a new configuration dictionary with default values, including a creation timestamp.
    The configuration will be stored in both the dictionary and a file.
    """
    global config_json
    config_json = {
        "parking_id": 1,                                 # Default parking ID
        "MAC": "00:14:22:01:23:45",                      # 
        "session_id": "000000",                          # Default controller ID
        "server_address": "http://172.16.143.120:5000",  # Default server address
        "time_created": datetime.now().isoformat(),      # Creation timestamp
        "beam_timeout": 3,                               # In seconds
        "mode": "entry"                                  # Opeartion mode (just for simulation purposes)
    }
    
    # Save and write configuration
    save_config()

    logs.info(f"Configuration file '{CONFIG_FILE}' created with default values.")
    return config_json  # Returning the global config_json

def load_config():
    """
    Load the configuration from the file, or create a new one if it doesn't exist.
    Also updates the dictionary with the configuration values.
    """
    global config_json
    if not os.path.exists(CONFIG_FILE):
        logs.info(f"Configuration file '{CONFIG_FILE}' not found. Generating a new one...")
        return generate_config()
    else:
        with open(CONFIG_FILE, "r") as file:
            config_json = json.load(file)  # Update the global config_json
        logs.info(f"Configuration file '{CONFIG_FILE}' loaded.")
        return config_json  # Returning the global config_json


def save_config():
    """
    Save the current configuration stored in the dictionary to the config file.
    And store configuration time
    """
    global config_json
    # Update time
    config_json["time_created"] = datetime.now().isoformat()
    
    # Save config
    with open(CONFIG_FILE, "w") as file:
        json.dump(config_json, file, indent=4)  # Use the global config_json
    logs.info(f"Configuration saved to '{CONFIG_FILE}'.")
