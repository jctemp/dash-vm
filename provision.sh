#!/bin/bash

echo "Installing core dependencies"
sudo apt-get update
sudo apt-get upgrade -y
sudo apt-get autoremove
sudo apt-get install -y git curl wget vim ca-certificates \
                        gnupg lsb-release build-essential \
                        cmake libgmp-dev libzmq3-dev jq \
                        python3 python3-pip python3-virtualenv
 
# install node and nvm
if ! command -v node
then
    echo "=============== Installing node ==============="

    curl -sL https://deb.nodesource.com/setup_16.x | sudo bash -
    sudo apt-get install -y nodejs

    echo " => success"
fi

# install docker
if ! command -v docker
then
    echo "=============== Installing docker ==============="

    curl -fsSL https://download.docker.com/linux/ubuntu/gpg | sudo gpg --dearmor -o /usr/share/keyrings/docker-archive-keyring.gpg
    echo "deb [arch=$(dpkg --print-architecture) signed-by=/usr/share/keyrings/docker-archive-keyring.gpg] https://download.docker.com/linux/ubuntu \
        $(lsb_release -cs) stable" | sudo tee /etc/apt/sources.list.d/docker.list > /dev/null

    sudo apt-get update
    sudo apt-get install -y docker-ce docker-ce-cli containerd.io
    sudo chmod 666 /var/run/docker.sock

    echo " => success"

fi

# install docker-compose
if ! command -v docker-compose
then
    echo "=============== Installing docker-compose ==============="

    sudo curl -L "https://github.com/docker/compose/releases/download/1.29.2/docker-compose-$(uname -s)-$(uname -m)" -o /usr/local/bin/docker-compose
    sudo chmod +x /usr/local/bin/docker-compose
    sudo ln -s /usr/local/bin/docker-compose /usr/bin/docker-compose

    echo " => success"
fi

echo "=============== SETUP FINISHED ==============="

node -v
docker -v
docker-compose -v

echo "=============================================="