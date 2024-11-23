import os
import datetime

# Ensure the log directory exists
log_directory = 'logs'
os.makedirs(log_directory, exist_ok=True)

def _get_log_filename():
    """Returns the log filename based on the current date."""
    today = datetime.datetime.now().strftime('%d-%m-%Y')
    return os.path.join(log_directory, f'{today}.log')

def _write_log(tag, message):
    """Writes a log message with a specified tag."""
    log_filename = _get_log_filename()
    log_entry = f'[{datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")}] {tag}: {message}\n'
    with open(log_filename, 'a') as log_file:
        log_file.write(log_entry)

def debug(message):
    """Log a debug message."""
    _write_log('DEBUG', message)

def info(message):
    """Log an info message."""
    _write_log('INFO', message)

def warning(message):
    """Log a warning message."""
    _write_log('WARNING', message)

def error(message):
    """Log an error message."""
    _write_log('ERROR', message)

def critical(message):
    """Log a critical error message."""
    _write_log('CRITICAL', message)

def fail(message):
    """Log a fail message."""
    _write_log('FAIL', message)