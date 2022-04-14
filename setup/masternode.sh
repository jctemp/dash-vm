#!/bin/bash

script_name="$(basename "$0")"
p2p_port=19999
rpc_ip="127.0.0.1"
rpc_port=19998
rpc_user="dashrpc"
rpc_pass="password"

echo "[$script_name]:" "Start masternode setup"

echo " > Wait for node"

sync

ip_address=""
port=0

protx_register=""
protx_signmessage=""
protx_tx=""
protx_signature=""
protx_hash=""

sleep 1

# ====== COLLATERAL =================================================================

echo " > Generating collateral"

collateral_address=$(dash-cli getnewaddress)
collateral_hash=$(fundAddress -i $rpc_ip -p $rpc_port -u $rpc_user -P $rpc_pass \
    $collateral_address 1000)

if [ $? != 0 ]; then
    echo "Error: $collateral_hash"
    exit 1
fi

rpc --ip $rpc_ip --port $rpc_port --user $rpc_user --pass $rpc_pass \
    lockunspent false "[{\"txid\":\"$collateral_hash\",\"vout\":1}]"
sleep 1
collateral_output=$(dash-cli masternode outputs | jq .\""$collateral_hash"\" | tr -d '"')
sleep 1

# ====== BLS ========================================================================

echo " > Generating bls key"

bls_keys=$(dash-cli bls generate)
bls_private_key=$(echo "$bls_keys" | jq ."secret" | tr -d '"')
bls_public_key=$(echo "$bls_keys" | jq ."public" | tr -d '"')

sleep 1

# ====== ADDRESSES ==================================================================

echo " > Generating addresses"

address_owner=$(dash-cli getnewaddress)
address_voting=$(dash-cli getnewaddress)
address_payout=$(dash-cli getnewaddress)
address_fee_source=$(dash-cli getnewaddress)

fundAddress -i $rpc_ip -p $rpc_port -u $rpc_user -P $rpc_pass \
    $address_payout 1 >/dev/null
fundAddress -i $rpc_ip -p $rpc_port -u $rpc_user -P $rpc_pass \
    $address_fee_source 1 >/dev/null

sleep 1

# ====== MACHINE ====================================================================

echo " > Set machine details"

ip_address=$(hostname -I | awk -F" " '{print $2}') # TODO: better way to get ip
port="$p2p_port"

sleep 1
# ====== PROTX =====================================================================

echo " > Start ProTx"

echo " > Waiting for ProTx"

echo " > Restarting Node"

echo "[$script_name]:" "Finished masternode setup"
