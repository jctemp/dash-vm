#!/bin/bash

# ┏━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━┓
# ┃                                        UTILS                                        ┃
# ┗━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━┛

# Force syncs node to network with mnsync next. Waits until the dashd process is running.
# Calls "mnsync next" until the "FINISHED" string is returned.
function sync() {
    echo "[${FUNCNAME[0]}]:" "Starting node sync..."

    while ! pgrep dashd; do sleep 1; done

    local output
    output=$(dash-cli mnsync next)
    while ! echo "$output" | grep -q "FINISHED" >/dev/null; do
        sleep 1
        output=$(dash-cli mnsync next)
    done

    echo "[${FUNCNAME[0]}]:" "Node sync complete."
}

# Generates blocks in the network until the amount of blocks is reached. The seed node
# is generating the blocks.
function generateBlocks() {

    if [ $# -ne 1 ]; then
        echo "Usage: generateBlocks <amount>"
        return 1
    fi

    echo "[${FUNCNAME[0]}]:" "Generating $1 blocks"

    local res
    local count

    count=0

    res=$(dash-cli generate 1)
    count=$(("$count" + $(echo "$res" | jq ".|length")))
    echo "  $(echo "$res" | jq .[]?)"

    while [ "$count" -lt "$1" ]; do

        res=$(dash-cli generate 1)
        count=$(("$count" + $(echo "$res" | jq ".|length")))
        echo "  $(echo "$res" | jq .[]?)"

    done

    echo "[${FUNCNAME[0]}]:" "Generating complete."
    return 0
}

# Generates blocks in the network until the amount of funds is reached. The seed is
# generating the blocks.
function generate() {

    if [ $# -ne 1 ]; then
        echo "Usage: generate <amount>"
        return 1
    fi

    echo "[${FUNCNAME[0]}]:" "Mining blocks for $1 DASH..."

    while [ "$(echo "$(dash-cli getwalletinfo | jq .balance) < $1" | bc -l)" -eq 1 ]; do
        dash-cli generate 1 >/dev/null
    done

    echo "[${FUNCNAME[0]}]:" "Mining complete."
    return 0
}

# Remove all dash related files and stop the dashd process.
function purge() {
    echo "[${FUNCNAME[0]}]:" "Deleting dash related files..."
    sudo rm -rf /usr/local/bin/*dash*
    rm -rf .dashcore/
    pkill dashd
    echo "[${FUNCNAME[0]}]:" "Deleted dash related files."
}

# Wrapper function for remote procedure calls. The first argument is the command and
# all folling arguments are passed as arguments in list.
function rpc() {

    if [ $# -eq 0 ]; then
        echo "Usage: rpc <command> [arguments...]"
        return 1
    fi

    local cmd
    local args

    cmd="$1"
    shift
    printf -v args '%s,' "$@"

    curl -s \
        --user dashrpc:password \
        --data-binary '{ "jsonrpc": "1.0", "id":"rpc", "method": '\""$cmd"\"', "params": ['"${args%,}"'] }' \
        -H 'content-type: text/plain;' http://10.0.0.10:19998/
    # /wallet/<wallet-name>
}

# Generates blocks in the network until the amount of blocks is reached. The seed node
# is generating the blocks.
function mint() {

    if [ $# -ne 1 ]; then
        echo "Usage: mint <amount>"
        return 1
    fi

    echo "[${FUNCNAME[0]}]:" "Generating $1 blocks"

    local res
    local count

    count=0

    res=$(rpc generate 1)
    count=$(("$count" + $(echo "$res" | jq ".|length")))
    echo "  $(echo "$res" | jq .[]?)"

    while [ "$count" -lt "$1" ]; do

        res=$(rpc generate 1)
        count=$(("$count" + $(echo "$res" | jq ".|length")))
        echo "  $(echo "$res" | jq .[]?)"

    done

    echo "[${FUNCNAME[0]}]:" "Generating complete."
    return 0
}

# Check how often a block has been confirmed.
function confirmations() {

    if [ $# -ne 1 ]; then
        echo "Usage: confirmations <txid>"
        return 1
    fi

    rpc gettransaction \""$1"\" | jq .result.confirmations
    return 0
}

# Mines blocks until a transaction has been confirmed.
function confirm() {

    if [ $# -ne 1 ]; then
        echo "Usage: confirm <txid>"
        return 1
    fi

    local output
    output=$(confirmations "$1")
    while [ "$output" -lt 1 ]; do
        rpc mnsync reset >/dev/null
        sync >/dev/null
        rpc generate 1 >/dev/null
        sleep 1
        output=$(confirmations "$1")
    done
    return 0
}

# Locks the unspent outputs of a transaction.
function lockunspent() {

    if [ $# -ne 1 ]; then
        echo "Usage: lockunspent <txid>"
        return 1
    fi

    local collateral_hash
    collateral_hash="$1"

    rpc lockunspent false "[{\"txid\":\"$collateral_hash\",\"vout\":1}]"
    return 0
}

# Sends funds from seed wallet to an address.
function fund() {

    if [ $# -ne 2 ]; then
        echo "Usage: fund <address> <amount>"
        return 1
    fi

    local address
    local amount
    local txId
    local res

    address=$1
    amount=$2
    res=$(rpc sendtoaddress \""$address"\" "$amount")

    if [ "$(echo "$res" | jq ".error|length")" -gt 0 ]; then
        echo "Msg: $(echo "$res" | jq .error.message)"
        return 1
    fi

    txId=$(echo "$res" | jq -c .result | tr -d '"')
    confirm "$txId"
    echo "$txId"

    return 0
}

# Check if Tx hash in mempool
function check_protx() {

    if [ $# -ne 1 ]; then
        echo "Usage: check_protx <masternode.json file>"
        return 1
    fi

    local tx_hash
    local filename
    local block_height
    local block_hash

    filename="$1"
    tx_hash=$(jq .protx.hash <"$filename" | tr -d '"')
    block_height=$(dash-cli getmempoolentry "$tx_hash" | jq .height)
    block_hash=$(dash-cli getblockhash "$block_height")
    dash-cli getblock "$block_hash" | jq .confirmations
}

# Activate DIPs in the network.
function active_sporks() {
    for spork in $(dash-cli spork show | jq '. | keys[]' | tr -d '"'); do
        dash-cli spork "$spork" 0 >/dev/null
    done
    dash-cli spork active | jq '. | keys[] as $k | "\($k) = \(.[$k])"'
}

# List all active masternodes.
function masternode_list() {
    dash-cli masternode list | jq '. | keys[] as $k | .[$k].address' | tr -d '"'
}

# Check if current node is in the list of active masternodes.
# 0 = yes, 1 = no
function masternode_in_list() {

    if [ $# -ne 1 ]; then
        echo "Usage: masternode_in_list <masternode.json file>"
        return 1
    fi

    local value
    value="$1"

    local tx_hash
    if [ -f "$1" ]; then
        tx_hash=$(jq .protx.hash <"$value")
    else
        tx_hash=$(echo "$value" | jq .protx.hash)
    fi

    for hash in $(dash-cli masternode list | jq '. | keys[] as $k | .[$k].proTxHash'); do
        if [ "$hash" == "$tx_hash" ]; then
            echo "Masternode is in the list"
            return 0
        fi
    done
    echo "Masternode is not in the list"
    return 1
}

# ┏━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━┓
# ┃                                       WRAPPER                                       ┃
# ┗━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━┛

function core() {
    # SET DIRECTORY NAMES
    ACTIVE_DIR=$(pwd)
    SCRIPT_DIR="/vagrant/node"

    echo "[${FUNCNAME[0]}]:" "Setup core"

    # CHECK IF DASH IS INSTALLED
    if [ ! -f /usr/local/bin/dashd ]; then
        echo "> Downloading dashcore"
        mkdir "${ACTIVE_DIR}/tmp" && cd "${ACTIVE_DIR}/tmp" || return
        wget -q https://github.com/dashpay/dash/releases/download/v0.17.0.3/dashcore-0.17.0.3-x86_64-linux-gnu.tar.gz

        echo "> Copy files to /usr/local/bin"
        tar xf dashcore-*.tar.gz
        sudo install -t /usr/local/bin dashcore-*/bin/*

        cd ..
        rm -rf "${ACTIVE_DIR}/tmp"
    else
        echo "> dashcore already installed"
    fi

    # RENEW DASHCORE FOLDER
    echo "> Create ${HOME}/.dashcore directory"
    rm -rf "${HOME}/.dashcore" && mkdir "${HOME}/.dashcore"
    cp -t "${HOME}/.dashcore" "${SCRIPT_DIR}/dash.conf"
    chmod 666 "${HOME}/.dashcore/dash.conf"
    sed -i 's/# externalip=/externalip='"$(hostname -I | awk -F" " '{print $2}')"'/' ~/.dashcore/dash.conf
    echo

    # CRON JOB
    crontab -l >cronJobs

    if ! grep -e dashd cronJobs >/dev/null; then
        echo "*/1 * * * * pgrep dashd || /usr/local/bin/dashd" >>cronJobs &&
            echo "> Successfully installed dashd cron job."
    else
        echo "> dashd cron job already installed."
    fi

    crontab cronJobs
    rm cronJobs

    echo "[${FUNCNAME[0]}]:" "Finished core setup"
}

function sentinel() {
    # INSTALL SENTINEL FOR MASTERNODE LATER

    echo "[${FUNCNAME[0]}]:" "Setup Sentinel"
    rm -rf "${HOME}/sentinel"

    cd || return
    git clone -q -b master https://github.com/dashpay/sentinel.git

    echo "> Creating Sentinel environment"
    cd sentinel || return
    virtualenv venv >env-debug.log
    venv/bin/pip install -r requirements.txt >pip-debug.log
    echo

    # CRON JOB
    crontab -l >cronJobs

    if ! grep -e sentinel cronJobs >/dev/null; then
        echo "* * * * * cd ~/sentinel && venv/bin/python bin/sentinel.py 2>&1 >> ~/sentinel/sentinel-cron.log" >>cronJobs &&
            echo "Successfully installed sentinel cron job."
    else
        echo "> sentinel cron job already installed."
    fi

    crontab cronJobs
    rm cronJobs
    cd || return

    echo "[${FUNCNAME[0]}]:" "Finished Sentinel setup"
}

function seednode() {
    if [ $# -ne 1 ]; then
        echo "How many masternodes need funding?"
        echo "Usage: seed_setup <number of masternodes>"
        return
    fi

    # CRON JOB
    crontab -l >cronJobs

    if ! grep -e sentinel cronJobs >/dev/null; then
        echo "*/1 * * * * pgrep dashd && /usr/local/bin/dash-cli generate 1 " >>cronJobs &&
            echo "Successfully installed 3 min mining interval cron job."
    else
        echo "> 3 min mining interval cron job already installed."
    fi

    crontab cronJobs
    rm cronJobs

    echo "[${FUNCNAME[0]}]: Starting seed node setup..."
    sync
    generate $((1200 * "$1"))
    echo "[${FUNCNAME[0]}]: Setup complete."
}

function masternode() {

    echo "[${FUNCNAME[0]}]:" "Starting masternode setup..."
    sync

    # VARIABLES FOR PROCEDURE

    local collateral_address
    local collateral_hash
    local collateral_output

    local bls_keys
    local bls_private_key
    local bls_public_key

    local address_owner
    local address_voting
    local address_payout
    local address_fee_source

    local ip_address
    local port

    local protx_register
    local protx_signmessage
    local protx_tx
    local protx_signature
    local protx_hash

    # ====== COLLATERAL =================================================================

    echo "[${FUNCNAME[0]}]:" "> Generate collateral"

    collateral_address=$(dash-cli getnewaddress)
    if ! collateral_hash=$(fund "$collateral_address" 1000); then
        echo "$collateral_hash"
        return 1
    fi

    lockunspent "$collateral_hash" >/dev/null
    collateral_output=$(dash-cli masternode outputs | jq .\""$collateral_hash"\" | tr -d '"')

    sleep 1

    # ====== BLS ========================================================================

    echo "[${FUNCNAME[0]}]:" "> Generate bls"

    bls_keys=$(dash-cli bls generate)
    bls_private_key=$(echo "$bls_keys" | jq ."secret" | tr -d '"')
    bls_public_key=$(echo "$bls_keys" | jq ."public" | tr -d '"')

    sleep 1

    # ====== ADDRESSES ==================================================================

    echo "[${FUNCNAME[0]}]:" "> Generate addresses"

    address_owner=$(dash-cli getnewaddress)
    address_voting=$(dash-cli getnewaddress)
    address_payout=$(dash-cli getnewaddress)
    address_fee_source=$(dash-cli getnewaddress)

    fund "$address_payout" 1 >/dev/null
    fund "$address_fee_source" 1 >/dev/null

    sleep 1

    # ====== MACHINE ====================================================================

    echo "[${FUNCNAME[0]}]:" "> Set machine details"

    ip_address=$(hostname -I | awk -F" " '{print $2}')
    port="19999"

    sleep 1

    # ====== PROTX =====================================================================

    echo "[${FUNCNAME[0]}]:" "> Execute Protx"

    protx_register=$(dash-cli protx register_prepare \
        "$collateral_hash" \
        "$collateral_output" \
        "$ip_address":$port \
        "$address_owner" \
        "$bls_public_key" \
        "$address_voting" \
        0 \
        "$address_payout" \
        "$address_fee_source")

    sleep 1

    protx_signmessage=$(echo "$protx_register" | jq .signMessage | tr -d '"')
    protx_tx=$(echo "$protx_register" | jq .tx | tr -d '"')
    protx_signature=$(dash-cli signmessage "$collateral_address" "$protx_signmessage")
    protx_hash=$(dash-cli protx register_submit "$protx_tx" "$protx_signature")

    sleep 1

    # ====== MASTERNODE =================================================================

    json_string=$(
        jq -n \
            --arg chash "$collateral_hash" \
            --arg caddr "$collateral_address" \
            --arg coutput "$collateral_output" \
            --arg bpriv "$bls_private_key" \
            --arg bpub "$bls_public_key" \
            --arg aowner "$address_owner" \
            --arg avoting "$address_voting" \
            --arg apayout "$address_payout" \
            --arg afeesource "$address_fee_source" \
            --arg mip "$ip_address" \
            --arg mport "$port" \
            --arg psig "$protx_signature" \
            --arg phash "$protx_hash" \
            '{"collateral":{"hash":$chash,"address":$caddr,"index":$coutput},"bls":{"private":$bpriv,"public":$bpub},"addresses":{"owner":$aowner,"voting":$avoting,"payout":$apayout,"fee_source":$afeesource},"machine":{"ip":$mip,"port":$mport},"protx":{"signature":$psig,"hash":$phash}}'
    )

    local dump

    echo "[${FUNCNAME[0]}]:" "> Wait for Masternode to appear in list"

    while ! dump=$(masternode_in_list "$json_string" >/dev/null); do
        echo "$dump" >/dev/null
        rpc mnsync reset >/dev/null
        sync >/dev/null
        mint 2 >/dev/null
        sleep 2
    done

    echo "[${FUNCNAME[0]}]:" "> Restart node as Masternode"

    sed -i 's/# masternodeblsprivkey=/masternodeblsprivkey='"$bls_private_key"'/' ~/.dashcore/dash.conf
    dash-cli stop
    sleep 1
    sync

    # ====== FINISHING ==================================================================

    local json_string
    local filename
    filename="masternode.json"
    echo "$json_string" >"$filename"
}
