#!/bin/bash

RED=$(tput setaf 1 :-"" 2>/dev/null)
GREEN=$(tput setaf 2 :-"" 2>/dev/null)
YELLOW=$(tput setaf 3 :-"" 2>/dev/null)
CYAN=$(tput setaf 6 :-"" 2>/dev/null)
RESET=$(tput sgr0 :-"" 2>/dev/null)

export RED
export GREEN
export YELLOW
export CYAN
export RESET

function hline() {
    printf '%.s─' $(seq 1 "$(tput cols)")
    printf '\n'
}

function msg_start() {
    hline
    printf '%s\n' "$YELLOW" "$@" "$RESET"
}

function msg_finished() {
    printf '%s\n' "$CYAN" "$@" "$RESET"
}

function msg_final() {
    hline
    printf '%s\n' "$GREEN" "$@" "$RESET"
    hline
}

# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

msg_start "Installing core dependencies"

sudo apt update
sudo apt upgrade -y
sudo apt autoremove

sudo apt install -y debian-keyring \
    debian-archive-keyring apt-transport-https \
    git curl wget vim ca-certificates \
    gnupg lsb-release build-essential ripgrep \
    cmake libgmp-dev libzmq3-dev jq \
    python3 python3-pip python3-virtualenv
sudo apt autoremove

git config --global advice.detachedHead false
pip install --upgrade pip
apt install python3.8-venv

# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

msg_finished "Core dependencies installed"

if ! command -v docker >/dev/null; then
    msg_start "Installing docker"

    curl -fsSL https://download.docker.com/linux/ubuntu/gpg | sudo gpg --dearmor -o /usr/share/keyrings/docker-archive-keyring.gpg
    echo "deb [arch=$(dpkg --print-architecture) signed-by=/usr/share/keyrings/docker-archive-keyring.gpg] https://download.docker.com/linux/ubuntu \
        $(lsb_release -cs) stable" | sudo tee /etc/apt/sources.list.d/docker.list >/dev/null

    sudo apt-get update
    sudo apt-get install -y docker-ce docker-ce-cli containerd.io
    sudo groupadd docker
    sudo usermod -aG docker "$USER"

    msg_finished "Docker installed at $(which docker)"
fi

# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

if ! command -v docker-compose >/dev/null; then
    msg_start "Installing docker-compose"

    sudo curl -L "https://github.com/docker/compose/releases/download/1.29.2/docker-compose-$(uname -s)-$(uname -m)" -o /usr/local/bin/docker-compose
    sudo chmod +x /usr/local/bin/docker-compose
    sudo ln -s /usr/local/bin/docker-compose /usr/bin/docker-compose

    msg_finished "Docker-compose installed at $(which docker-compose)"
fi

# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

if ! command -v node >/dev/null; then
    msg_start "Installing node"

    curl -fsSL https://deb.nodesource.com/setup_16.x | sudo -E bash -
    sudo apt-get install -y nodejs
    sudo npm install -g npm@latest

    msg_finished "Node installed at $(which node)"
fi

# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

# TODO: FIX APPENDING EXPORTS TO /etc/profile OR SOMETHING

if [ ! -d /usr/local/go ]; then
    msg_start "Installing go"

    curl -LO https://go.dev/dl/go1.18.1.linux-amd64.tar.gz
    sudo tar -C /usr/local -xzf go1.18.1.linux-amd64.tar.gz
    rm go1.18.1.linux-amd64.tar.gz

    # TODO: make this configurable or use $HOME => provisioning with vagrant uses "root" as user, hence $HOME does not work
    target="/home/vagrant"

    # if text in file already, do nothing
    if ! grep -q "GOPATH" "$target/.profile"; then

        cat <<EOF | sudo tee -a "$target/.profile"
# go envrioment variables for the .bashrc file
if [ -d /usr/local/go ]; then
    export GOROOT="/usr/local/go"
    export GOPATH="$HOME/go"
    export PATH="$PATH:$GOROOT/bin:$GOPATH/bin"
fi
EOF

    fi

    source "$target/.profile"

    msg_finished "Go installed at $(which go)"
fi

sudo apt autoremove

# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

hline

node -v
docker -v
docker-compose -v
/usr/local/go/bin/go version

msg_final "Finished provisioning"
