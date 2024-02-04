#!/bin/bash

sudo apt update -y -q


# open ports 
sudo ufw allow 15672/tcp
sudo ufw allow 5672/tcp
sudo ufw allow 4369/tcp
sudo ufw allow 25672/tcp
sudo ufw allow 15692/tcp
sudo ufw reload
sudo ufw allow proto tcp from any to any port 5672,15672,15692


# Install Nginx for loadbalancing
sudo apt-get install nginx -y -q


# Replace nginx config 
# If more then 3 nodes are needed, they have to be registered here



# Backup the original nginx.conf file
sudo cp /etc/nginx/nginx.conf /etc/nginx/nginx.conf.bak

git clone https://github.com/FuratH/rabbitmq-benchmark-2024.git

sudo cat rabbitmq-benchmark-2024/loadbalancer/nginx.conf > /etc/nginx/nginx.conf
 

sudo nginx -s reload
