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

git clone https://github.com/FuratH/rabbitmq-benchmark-2024.git

python3 rabbitmq-benchmark-2024/Failureinjector/server.py


touch /complete