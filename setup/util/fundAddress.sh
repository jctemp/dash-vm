#!/bin/bash

# need this for rpc
ip="10.0.0.10"
port="19998"
username="dashrpc"
password="password"

# define valid cli optins
valid_args=$(getopt -o i:p:u:P: --long ip:,port:,username:,password: -- "$@")

if [ $? != 0 ]; then
    echo "{\"message\": \"Invalid cli option\"}" | jq . >&2
    exit 1
fi

eval set -- "$valid_args"

while [ : ]; do
    case "$1" in
    -i | --ip)
        ip="$2"
        shift 2
        ;;
    -p | --port)
        port="$2"
        shift 2
        ;;
    -u | --username)
        username="$2"
        shift 2
        ;;
    -P | --password)
        password="$2"
        shift 2
        ;;
    --)
        shift
        break
        ;;
    *)
        echo "Internal error!"
        exit 1
        ;;
    esac
done

address=$1
amount=$2

json=$(rpc --ip $ip --port $port --user $username --pass $password \
    sendtoaddress $address $amount)

if [ $? != 0 ]; then
    echo "$json" | jq . >&2
    exit 1
fi

txId=$(echo "$json" | tr -d '"')

confirm --ip $ip --port $port --user $username --pass $password $txId

echo "$txId"

