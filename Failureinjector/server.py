from flask import Flask, request, send_file
import subprocess
import logging
import threading
import time
import os  # Import os module
from datetime import datetime

app = Flask(__name__)

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

# Global variable for the monitoring thread
# Global variables for monitoring
monitoring_thread = None
monitoring_active = False

def check_rabbitmq_status():
    try:
        result = subprocess.run(["sudo", "systemctl", "is-active", "rabbitmq-server"], 
                                capture_output=True, text=True, check=True)
        return result.stdout.strip()
    except subprocess.CalledProcessError as e:
        app.logger.error(f"Error checking RabbitMQ status: {e}")
        return "unknown"

def start_rabbitmq_service():
    try:
        subprocess.run(["sudo", "systemctl", "start", "rabbitmq-server"], check=True)
    except subprocess.CalledProcessError as e:
        app.logger.error(f"Failed to start RabbitMQ: {e}")

def monitor_rabbitmq():
    global monitoring_active
    while monitoring_active:
        status = check_rabbitmq_status()
        with open("rabbitmq_monitor.log", "a") as file:
            file.write(f"{datetime.now()} - RabbitMQ status: {status}\n")
        if status != "active":
            app.logger.info("RabbitMQ is down. Attempting to start...")
            start_rabbitmq_service()
        time.sleep(1)

@app.route('/start-monitoring', methods=['GET'])
def start_monitoring():
    global monitoring_thread, monitoring_active

    # Delete existing log file if it exists
    log_file_path = "rabbitmq_monitor.log"
    if os.path.exists(log_file_path):
        os.remove(log_file_path)

    if monitoring_thread is None or not monitoring_thread.is_alive():
        monitoring_active = True
        monitoring_thread = threading.Thread(target=monitor_rabbitmq)
        monitoring_thread.start()
        return "Monitoring started", 200
    else:
        return "Monitoring is already running", 400


@app.route('/stop-monitoring', methods=['GET'])
def stop_monitoring():
    global monitoring_active, monitoring_thread

    if monitoring_thread is None or not monitoring_thread.is_alive():
        return "Monitoring is not running", 400

    monitoring_active = False

    # Wait for the monitoring thread to finish
    if monitoring_thread.is_alive():
        monitoring_thread.join()

    log_file_path = "rabbitmq_monitor.log"
    if os.path.exists(log_file_path):
        return send_file(log_file_path, as_attachment=True)
    else:
        return "Log file does not exist", 404


@app.route('/start-rabbitmq', methods=['GET'])
def start_rabbitmq():
    app.logger.info(f"Accessed /start-rabbitmq - {request.remote_addr} - {datetime.now()}")
    try:
        subprocess.run(["sudo", "systemctl", "start", "rabbitmq-server"], check=True)
        return "RabbitMQ started", 200
    except subprocess.CalledProcessError as e:
        app.logger.error(f"Failed to start RabbitMQ: {e}")
        return f"Error: {e}", 500

app.route('/stop-rabbitmq', methods=['GET'])
def stop_rabbitmq():
    app.logger.info(f"Accessed /stop-rabbitmq - {request.remote_addr} - {datetime.now()}")
    try:
        subprocess.run(["sudo", "systemctl", "stop", "rabbitmq-server"], check=True)
        return "RabbitMQ stopped", 200
    except subprocess.CalledProcessError as e:
        app.logger.error(f"Failed to stop RabbitMQ: {e}")
        return f"Error: {e}", 500

@app.route('/kill-rabbitmq', methods=['GET'])
def kill_rabbitmq():
    app.logger.info(f"Accessed /kill-rabbitmq - {request.remote_addr} - {datetime.now()}")
    try:
        # Find and kill the RabbitMQ process
        kill_result = subprocess.run(["sudo", "pkill", "-9", "beam.smp"], check=True)
        return "RabbitMQ process killed", 200
    except subprocess.CalledProcessError as e:
        app.logger.error(f"Failed to kill RabbitMQ process: {e}")
        return f"Error: {e}", 500

@app.route('/restart-rabbitmq', methods=['GET'])
def restart_rabbitmq():
    app.logger.info(f"Accessed /restart-rabbitmq - {request.remote_addr} - {datetime.now()}")
    try:
        # Restart the RabbitMQ service
        subprocess.run(["sudo", "systemctl", "restart", "rabbitmq-server"], check=True)
        return "RabbitMQ service restarted", 200
    except subprocess.CalledProcessError as e:
        app.logger.error(f"Failed to restart RabbitMQ: {e}")
        return f"Error: {e}", 500


@app.route('/health', methods=['GET'])
def health_check():
    status = check_rabbitmq_status()
    return f"RabbitMQ status: {status}", 200

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000)


