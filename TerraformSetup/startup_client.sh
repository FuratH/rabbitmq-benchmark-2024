export DEBIAN_FRONTEND=noninteractive
sudo apt update -y -q
sudo apt-get upgrade -y

sudo apt-get remove needrestart -y 

# Set the service account key
echo '{
  "type": "service_account",
  "project_id": "csb-2023",
  "private_key_id": "7df7302376ddb5d974335f201f0a925d1dcc958b",
  "private_key": "-----BEGIN PRIVATE KEY-----\nMIIEvQIBADANBgkqhkiG9w0BAQEFAASCBKcwggSjAgEAAoIBAQDGJhceZHLrW6SX\nx8ZfA+dVC6XocGdFP53IXhb9l9NxQ4uG3Ew44J3vOGkVycjTF1OcpWPdHfA66GAH\njW/LU6kl6EHrw67zcNpbMoV3t3uge7MLZeacN1BpiPptsUcB7rxOMe3IBUmHTI3e\nxs43rYmjtNSzkkQstCfc52hmtkrS3UxjMrT5ZwbWDM8BH5/l6M3Fb3xzLtbgp4Lz\n8juQ2ibckFmg5rJmm0+JJpPNwsYyauni3onzr2hwkS4XG8tMlCqf2mBfhEZmRhT/\ngyEuvpwmMgSsdQESodNz4TLqcCE5ZLmBKIbF1Vu058cdvLeBlvysn2l7KpIDWrgy\n6wcTSiWdAgMBAAECggEAA9zLN5LysIbNSw4gXkrHsB81gTXrtWxbiYPYA+J5Qyxz\nZFIYBEXQnlClr8CKsx6xyQxqSW2jeKp98Le/laGQWwZPfqaGWwV4pC10b5R6ivLO\nVysJ10K2xQ/f/dJmVXHPZuDPR0ZfHA2QeGa8r1YpKDFGsidoP8zVOBekr9fe1oRk\nAwKJ2tTNCRzeBHn+98FMazsyvb8xlMd4l2mrh63grSEB0Taf5UyQj49IN+M+dNt+\nZrQ8b3MikeTDRQl3rOiBMbbmABsynVAxeMLLqxCR8n2Y9irdhHcvRQRqt1/RtaXc\nFQHAatHmy1rwQqiHOcIuCYJku+CKjRqpqHfu6Egw2wKBgQDxdIgQBllrq8dt+4MF\nV8U/RGtVmU5533TA+1PH9K6PndW+O4wwPCW9lPqgKkeRG2zY3Ak3ACpZBs3YNzUR\nNNAozOQnaPN4fTuXuUSDSMtSMlPfk2wMlIBZ1aMK48dYj37replPvnNGoA6lFHvT\nbplVcXGWtqY6HSPxHOeBMJ2+JwKBgQDSFbuawWzRlrPEv3jYU17wFq9kSDR2QmpK\nwvY8CBl7/ZCixCZ8K15z+GlQ4wNN6wQ6ETnkf5RJOGZr24ubQel1tOJw3xSEdvTj\n4kvBsjOcs7vJkOdaOagXSSOoayYC+/Gul0Z883sCF86wfrmmZXiIu9gbdJsaJkvd\nzdrEqj5cmwKBgFL2TUHkTJk4Pp/FiXEuhTGF2rNgp5wscTtVn6XWppvmCWkBoNt5\n7yXCqJKbtFdhavbgM7JYNjS8p8GgxnURBmzeaY44+17s+KrbF3Vcb6/gZv0s9DUm\nWSuEwi6dsQL22w8h4seJkqYznJSQAzPUjo7TGcpFG7xgAtd3rPuwrqKFAoGAamPx\nJvUPi7B7B4dDxqGp8YI7fliGoOEPfR7wngQoC7+kkJkvODCqW6aQhxL/6GS9Nj7l\nB4+IY/A5BiQftheSCDb7edevR0oKyKEgZk49jv0Ce5hzYSDTvD8g3LiuflJi2Vzo\nqHyRbcTqujzi/Z5jhTNDxNuvdHWyc/g88t2YSUMCgYEAr6/Ru3T+1Lg9PFVx9BR7\ncaa/T1P8WuPhuRXVfPPpn4w6XP1I8+SxZXNzW58oxbH2NmtMH+Cg9GT763xm0SWL\ni1Zu4pebJfK8NaFyaYecHQZr1HUlCR41McQ6RTshuvGKXHjyAoI+/zG8T/0o+H83\n4UfgXJhLw+kKx/hkhK3W8Ho=\n-----END PRIVATE KEY-----\n",
  "client_email": "57939934652-compute@developer.gserviceaccount.com",
  "client_id": "113230140637509580628",
  "auth_uri": "https://accounts.google.com/o/oauth2/auth",
  "token_uri": "https://oauth2.googleapis.com/token",
  "auth_provider_x509_cert_url": "https://www.googleapis.com/oauth2/v1/certs",
  "client_x509_cert_url": "https://www.googleapis.com/robot/v1/metadata/x509/57939934652-compute%40developer.gserviceaccount.com",
  "universe_domain": "googleapis.com"
}' > /tmp/service-account-key.json


export GOOGLE_APPLICATION_CREDENTIALS="/tmp/service-account-key.json"

# Authenticate with the service account
gcloud auth activate-service-account --key-file=/tmp/service-account-key.json


# Install Java 
sudo apt install openjdk-11-jre-headless -y

# Get benchmarking tool
git clone https://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@github.com/FuratH/RabbitMQ-Benchmark.git


# Create script to run client
echo '
sudo java -jar RabbitMQ-Benchmark/target/rabbitmq-benchmark-1.0.0-jar-with-dependencies.jar RabbitMQ-Benchmark/src/main/java/benchmark/config.yaml
' > /run.sh

sudo chmod +x run.sh

touch /done
