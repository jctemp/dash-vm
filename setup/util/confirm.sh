#!/bin/bash

# prints how of a block got confirmed
function confirmations() {
    local response=$(rpc --ip $ip --port $port --user $username --pass $password \
        gettransaction \"$1\" | jq -r '.confirmations')

    if [ $? != 0 ]; then
        echo >&2 "$response"
        return 1
    fi

    echo "$response"
    return 0
}

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

txId=$1

output=$(confirmations "$1")
if [ $? != 0 ]; then
    echo >&2 "$output"
    exit 1
fi

while [ "$output" -lt 1 ]; do
    sync
    rpc --ip $ip --port $port --user $username --pass $password \
        generate 1 >/dev/null

    sleep 1

    output=$(confirmations "$1")
    if [ $? != 0 ]; then
        echo >&2 "$output"
        exit 1
    fi
done
