#!/bin/bash

function platform() {
    # 1) wait for chainlock
    while ! dash-cli getbestblockhash >/dev/null 2>&1; do
        sleep 1
    done

    # 2) get platform wallet pubkeys 
    # TODO: auto generation of wallet pubkeys in seed node + save to shared folder /vagrant/platformWallets.json
    jq '. | to_entries | map(select(.key | match("PubKey"))) | from_entries' < "/vagrant/platformWallets.json" > "/vagrant/walletPubKeys.json"
 

    local core_rpc_port=19998
    local core_p2p_port=19999
    local rpc_username=dashrpc
    local rpc_password=password
    local quorum_type=101
    local chainlock_height
    local network_name

    chainlock_height=$(dash-cli getbestchainlock | jq .height)
    network_name=$(dash-cli getblockchaininfo | jq .chain | tr -d '"')

    setup_mongodb

    git clone -q -b v0.22.1 https://github.com/dashevo/platform.git
    cd platform || return 1
    sudo corepack enable

    # JS DRIVE SETUP
    cd packages/js-drive/ || return 1
    cp .env.example .env

    sed -i "s/^CORE_JSON_RPC_PORT.*/CORE_JSON_RPC_PORT=$core_rpc_port/" .env
    sed -i "s/^CORE_JSON_RPC_USERNAME.*/CORE_JSON_RPC_USERNAME=$rpc_username/" .env
    sed -i "s/^CORE_JSON_RPC_PASSWORD.*/CORE_JSON_RPC_PASSWORD=$rpc_password/" .env
    sed -i "s/^INITIAL_CORE_CHAINLOCKED_HEIGHT.*/INITIAL_CORE_CHAINLOCKED_HEIGHT=$chainlock_height/" .env
    sed -i "s/^VALIDATOR_SET_LLMQ_TYPE.*/VALIDATOR_SET_LLMQ_TYPE=$quorum_type/" .env
    sed -i "s/^NETWORK.*/NETWORK=$network_name/" .env

    sed -i "s/^DPNS_MASTER_PUBLIC_KEY=*/DPNS_MASTER_PUBLIC_KEY=$dpnsPubKey/" .env
    sed -i "s/^DASHPAY_MASTER_PUBLIC_KEY=*/DASHPAY_MASTER_PUBLIC_KEY=$dashpayPubKey/" .env
    sed -i "s/^FEATURE_FLAGS_MASTER_PUBLIC_KEY=*/FEATURE_FLAGS_MASTER_PUBLIC_KEY=$featureFlagPubKey/" .env
    sed -i "s/^MASTERNODE_REWARD_SHARES_MASTER_PUBLIC_KEY=*/MASTERNODE_REWARD_SHARES_MASTER_PUBLIC_KEY=$masternodeRewardPubKey/" .env

    npm_config_zmq_external=true
    yarn install

forever start -a --uid "drive" scripts/abci.js

    setup_tenderdash $core_rpc_port $rpc_username $rpc_password $network_name $quorum_type $chainlock_height



}

function setup_mongodb() {
    sudo apt remove -y mongo*

    # make mongodb available through apt package manager
    wget -qO - https://www.mongodb.org/static/pgp/server-5.0.asc | sudo apt-key add -
    echo "deb [ arch=amd64,arm64 ] https://repo.mongodb.org/apt/ubuntu focal/mongodb-org/5.0 multiverse" | sudo tee /etc/apt/sources.list.d/mongodb-org-5.0.list
    sudo apt-get update
    
    # insatll mongodb
    sudo apt-get install -y mongodb-org
    
    # configure mongodb
    sudo sed -i 's/#replication:/replication:\n  replSetName: driveDocuments/' /etc/mongod.conf
    
    # enable and restart service
    sudo systemctl enable mongod
    sudo systemctl restart mongod

    while ! pgrep mongod; do sleep 2; done
    sleep 5;

    # initiate mongodb replica set
    mongo<<<"rs.initiate({_id:'driveDocuments',version: 1,members:[{_id: 0,host: 'localhost:27017',},],});"
}

function setup_tenderdash() {

    if [ $# -ne 6 ]; then
        echo "Usage: tenderdash <rpc_port> <rpc_username> <rpc_password> <network_name> <quorum_type> <chain_lock_height>"
        return 1
    fi

    local core_rpc_port=$1
    local rpc_username=$2
    local rpc_password=$3
    local network_name=$4
    local quorum_type=$5
    local chainlock_height=$6

    # 0) install go
    wget -q https://go.dev/dl/go1.18.1.linux-amd64.tar.gz
    sudo tar xfz go1.18.1.linux-amd64.tar.gz -C /usr/local/
    rm go1.18.1.linux-amd64.tar.gz
    export PATH=$PATH:/usr/local/go/bin

    # 1) install
    git clone -q -b v0.7.0 https://github.com/dashevo/tenderdash.git
    cd tenderdash || return 1
    make install-bls > ./install-bls.log
    make build-linux > ./build-linux.log
    sudo install -t /usr/local/bin build/*
    cd || return 1

    # 2) init tenderdash to get configs
    tenderdash init

    # 3) configure tenderdash: general
sed -i 's/\(^moniker.*\)/#\1/' ~/.tenderdash/config/config.toml
sed -i 's/^timeout_commit.*/timeout_commit = "500ms"/' ~/.tenderdash/config/config.toml
sed -i 's/^create_empty_blocks_interval.*/create_empty_blocks_interval = "3m"/' ~/.tenderdash/config/config.toml
sed -i 's/^namespace.*/namespace = "drive_tendermint"/' ~/.tenderdash/config/config.toml
sed -i "s/^priv_validator_core_rpc_host.*/priv_validator_core_rpc_host = \"127.0.0.1:$core_rpc_port\"/" ~/.tenderdash/config/config.toml
sed -i "s/^priv_validator_core_rpc_username.*/priv_validator_core_rpc_username = \"$rpc_username\"/" ~/.tenderdash/config/config.toml
sed -i "s/^priv_validator_core_rpc_password.*/priv_validator_core_rpc_password = \"$rpc_password\"/" ~/.tenderdash/config/config.toml

    # 4) configure tenderdash: local networks
    sed -i 's/^addr_book_strict.*/addr_book_strict = false/' ~/.tenderdash/config/config.toml
    sed -i "s/^quorum_type.*/quorum_type = \"$quorum_type\"/" ~/.tenderdash/config/config.toml

    # 5) configure tenderdash: genesis.json
    sed -i "s/^  \"initial_core_chain_locked_height\".*/  \"initial_core_chain_locked_height\": $chainlock_height,/" ~/.tenderdash/config/genesis.json
    sed -i "s/^  \"chain_id.*/  \"chain_id\": \"$network_name\",/" ~/.tenderdash/config/genesis.json
    sed -i "s/^  \"quorum_type\".*/  \"quorum_type\": \"$quorum_type\",/" ~/.tenderdash/config/genesis.json

    # TODO: TENDERDASH CRON JOB

    return 0
}


