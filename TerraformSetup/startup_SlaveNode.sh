#!/bin/bash

sudo apt update -y -q

#sudo apt install rabbitmq-server -y -q

sudo apt-get update 
sudo apt-get upgrade -y
sudo apt-get install curl gnupg -y
sudo apt-get install apt-transport-https -y

# Install rabbitmq

curl -1sLf "https://keys.openpgp.org/vks/v1/by-fingerprint/0A9AF2115F4687BD29803A206B73A36E6026DFCA" | sudo gpg --dearmor | sudo tee /usr/share/keyrings/com.rabbitmq.team.gpg > /dev/null

curl -1sLf "https://keyserver.ubuntu.com/pks/lookup?op=get&search=0xf77f1eda57ebb1cc" | sudo gpg --dearmor | sudo tee /usr/share/keyrings/net.launchpad.ppa.rabbitmq.erlang.gpg > /dev/null

curl -1sLf "https://packagecloud.io/rabbitmq/rabbitmq-server/gpgkey" | sudo gpg --dearmor | sudo tee /usr/share/keyrings/io.packagecloud.rabbitmq.gpg > /dev/null


distribution_name="jammy"

# Specify the file path
file_path="/etc/apt/sources.list.d/rabbitmq.list"

# Content to be copied into the file
content="# Source repository definition example.

## Provides modern Erlang/OTP releases
##
## \"$distribution_name\" as distribution name should work for any reasonably recent Ubuntu or Debian release.
## See the release to distribution mapping table in RabbitMQ doc guides to learn more.
deb [signed-by=/usr/share/keyrings/net.launchpad.ppa.rabbitmq.erlang.gpg] http://ppa.launchpad.net/rabbitmq/rabbitmq-erlang/ubuntu $distribution_name main
deb-src [signed-by=/usr/share/keyrings/net.launchpad.ppa.rabbitmq.erlang.gpg] http://ppa.launchpad.net/rabbitmq/rabbitmq-erlang/ubuntu $distribution_name main

## Provides RabbitMQ
##
## \"$distribution_name\" as distribution name should work for any reasonably recent Ubuntu or Debian release.
## See the release to distribution mapping table in RabbitMQ doc guides to learn more.
deb [signed-by=/usr/share/keyrings/io.packagecloud.rabbitmq.gpg] https://packagecloud.io/rabbitmq/rabbitmq-server/ubuntu/ $distribution_name main
deb-src [signed-by=/usr/share/keyrings/io.packagecloud.rabbitmq.gpg] https://packagecloud.io/rabbitmq/rabbitmq-server/ubuntu/ $distribution_name main"

# Open the file with the preferred text editor (vi in this case)
vi "$file_path" <<EOF
$content
EOF

echo "Content has been added to $file_path"

sudo apt-get update -y

sudo apt-get install -y erlang-base erlang-asn1 erlang-crypto erlang-eldap erlang-ftp erlang-inets erlang-mnesia erlang-os-mon erlang-parsetools erlang-public-key erlang-runtime-tools erlang-snmp erlang-ssl erlang-syntax-tools erlang-tftp erlang-tools erlang-xmerl

sudo apt-get install rabbitmq-server -y --fix-missing

sudo systemctl is-enabled rabbitmq-server

sudo systemctl status rabbitmq-server

sudo rabbitmq-plugins enable rabbitmq_management

sudo systemctl restart rabbitmq-server

#open ports

sudo ufw allow OpenSSH

sudo ufw enable

sudo ufw allow 15672/tcp
sudo ufw allow 5672/tcp
sudo ufw allow 4369/tcp
sudo ufw allow 25672/tcp
sudo ufw allow 15692/tcp
sudo ufw reload

sudo ufw allow proto tcp from any to any port 5672,15672,15692




# Define the new content
cookie="OJhz25F2ODxAdcaZZ6Hv8ZDUvo3SEBFlpE5x8FCbJP4EIf7xigiSURsR"

# Specify the file path
file_path="/var/lib/rabbitmq/.erlang.cookie"

# Check if the file exists
if [ -e "$file_path" ]; then
    # Replace the content of the file
    echo "$cookie" > "$file_path"
    echo "Content of $file_path has been replaced."
else
    echo "Error: File $file_path not found."
fi


sudo systemctl restart rabbitmq-server
sleep 5
sudo rabbitmqctl stop_app

sleep 5
sudo rabbitmqctl join_cluster rabbit@node0
sleep 5
sudo rabbitmqctl start_app

sleep 5

sudo systemctl restart rabbitmq-server
sleep 5
sudo rabbitmqctl stop_app

sleep 5
sudo rabbitmqctl join_cluster rabbit@node0
sleep 5
sudo rabbitmqctl start_app

sudo rabbitmq-plugins enable rabbitmq_prometheus

touch /prepy

sudo apt install python3-pip -y

touch /pip
sudo pip3 install Flask 

touch /flask

# Add failure injector 
sudo ufw allow 5000/tcp


# Add failure injector
flaskapi=$(cat <<EOL
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
            app.logger.info("RabbitMQ started")
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



EOL
)

# Replace the file content
echo "$flaskapi" > "server.py"

sudo ufw allow 5000/tcp

python3 server.py


touch /complete