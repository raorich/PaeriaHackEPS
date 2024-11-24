import os
import datetime

# Ensure the log directory exists
log_directory = 'logs'
os.makedirs(log_directory, exist_ok=True)

def _get_log_filename():
    """Returns the log filename based on the current date."""
    try:
        today = datetime.datetime.now().strftime('%d-%m-%Y')
        return os.path.join(log_directory, f'{today}.log')
    except Exception as e:
        print(f"[ERROR] Failed to generate log filename: {e}")
        raise

def _write_log(tag, message):
    """Writes a log message with a specified tag."""
    try:
        log_filename = _get_log_filename()
        log_entry = f'[{datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")}] {tag}: {message}\n'
        with open(log_filename, 'a') as log_file:
            log_file.write(log_entry)
        delete_old_logs()
    except Exception as e:
        print(f"Failed to write log: {e}")

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

def delete_old_logs():
    """Deletes log files older than 48 hours."""
    try:
        now = datetime.datetime.now()
        for filename in os.listdir(log_directory):
            file_path = os.path.join(log_directory, filename)
            if os.path.isfile(file_path):
                file_creation_time = datetime.datetime.fromtimestamp(os.path.getmtime(file_path))
                if (now - file_creation_time).total_seconds() > 48 * 3600:
                    os.remove(file_path)
                    info(f"Deleted old log file: {filename}")
    except Exception as e:
        print(f"[ERROR] Failed to delete old logs: {e}")