import RPi.GPIO as GPIO
import time
from threading import Timer
import config
import logs
import api_requests

BEAM_PIN = 27
beam_broken_time = None
timeout = None

def beam_timeout_handler():
    """Function to call when the beam is broken for too long."""
    print("Beam has been broken for more than 3 seconds!")
    if config.config_json['mode'] == "entry":
        api_requests.request_tiquet_info(f"{config.config_json['server_address']}/add-door-register-entry")
    else: 
        api_requests.register_parking_exit(f"{config.config_json['server_address']}/add-door-register-exit",11)


def break_beam_callback(channel):
    global beam_broken_time
    if GPIO.input(BEAM_PIN):  # Beam unbroken
        logs.debug("Beam unbroken")
        print("[DEBUG] Beam unbroken.")
        beam_broken_time = None  # Reset the timer
    else:  # Beam broken
        logs.debug("Beam broken")
        print("[DEBUG] Beam broken.")
        beam_broken_time = time.time()  # Record the time of breaking
        Timer(timeout, check_beam_status).start()

def check_beam_status():
    """Check if the beam remains broken after the timeout period."""
    if beam_broken_time and (time.time() - beam_broken_time) >= timeout:
        beam_timeout_handler()

def start():
    """Initialize the beam detection system."""
    global timeout

    timeout = config.config_json['beam_timeout']
    
    GPIO.setmode(GPIO.BCM)
    GPIO.setup(BEAM_PIN, GPIO.IN, pull_up_down=GPIO.PUD_UP)
    GPIO.add_event_detect(BEAM_PIN, GPIO.BOTH, callback=break_beam_callback)
    logs.info("Beam detection system started.")

def clean_up():
    """Clean up the GPIO setup."""
    GPIO.cleanup()
    print("Beam detection system stopped.")
