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
new_content=$(cat <<EOF
user www-data;
worker_processes auto;
pid /run/nginx.pid;
include /etc/nginx/modules-enabled/*.conf;

events {
        worker_connections 768;
        # multi_accept on;
}

stream {
        # List of upstream AMQP connections
        upstream stream_amqp {
                least_conn;
                server node0:5672;
                server node1:5672;
                server node2:5672;
        }

        # List of upstream STOMP connections
        upstream stream_stomp {
                least_conn;
                server node0:61613;
                server node1:61613;
                server node2:61613;
        }

        # AMQP definition
        server {
                listen 5672; # the port to listen on this server
                proxy_pass stream_amqp; # forward traffic to this upstream group
                proxy_timeout 3s;
                proxy_connect_timeout 3s;
        }

        # STOMP definition
        server {
                listen 61613; # the port to listen on this server
                proxy_pass stream_stomp; # forward traffic to this upstream group
                proxy_timeout 3s;
                proxy_connect_timeout 3s;
        }
}

http {

        ##
        # Basic Settings
        ##

        sendfile on;
        tcp_nopush on;
        types_hash_max_size 2048;
        # server_tokens off;

        # server_names_hash_bucket_size 64;
        # server_name_in_redirect off;

        include /etc/nginx/mime.types;
        default_type application/octet-stream;

        ##
        # SSL Settings
        ##

        ssl_protocols TLSv1 TLSv1.1 TLSv1.2 TLSv1.3; # Dropping SSLv3, ref: POODLE
        ssl_prefer_server_ciphers on;

        ##
        # Logging Settings
        ##

        access_log /var/log/nginx/access.log;
        error_log /var/log/nginx/error.log;

        ##
        # Gzip Settings


        gzip on;

        # gzip_vary on;
        # gzip_proxied any;
        # gzip_comp_level 6;
        # gzip_buffers 16 8k;
        # gzip_http_version 1.1;
        # gzip_types text/plain text/css application/json application/javascript text/xml application/xml appl>

        ##
        # Virtual Host Configs
        ##

        include /etc/nginx/conf.d/*.conf;
        include /etc/nginx/sites-enabled/*;

        # Define an upstream group for HTTP failover
        upstream http_backend {
                least_conn;                  # Use the least connections strategy
                server node0:15672;          # First backend server
                server node1:15672;          # Second backend server
                server node2:15672;          # Third backend server
                # All servers are treated equally; no backups
        }
server {
        # listen to the 15672 port on this server
        listen 15672 default_server;

        # rule on the site root 
        location / {
                proxy_pass http://http_backend; # Forward traffic to the upstream group
                proxy_set_header Host \$host;
                proxy_set_header X-Real-IP \$remote_addr;
                proxy_set_header X-Forwarded-For \$proxy_add_x_forwarded_for;
                proxy_set_header X-Forwarded-Proto \$scheme;

            # Define timeouts (optional, adjust based on your requirements)
            proxy_connect_timeout       3s;
            proxy_send_timeout          3s;
            proxy_read_timeout          3s;
        }

}

}
EOF
)

# Backup the original nginx.conf file
sudo cp /etc/nginx/nginx.conf /etc/nginx/nginx.conf.bak

# Replace the content of nginx.conf with the new configuration
sudo echo "$new_content" | sudo tee /etc/nginx/nginx.conf > /dev/null

sudo nginx -s reload
