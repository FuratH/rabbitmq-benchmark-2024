export DEBIAN_FRONTEND=noninteractive
sudo apt update -y -q
sudo apt-get upgrade -y

sudo apt-get remove needrestart -y 


# Install Java 
sudo apt install openjdk-11-jre-headless -y

# Get benchmarking tool
git clone https://github.com/FuratH/rabbitmq-benchmark-2024.git



touch /done
