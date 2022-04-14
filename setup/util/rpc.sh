#!/bin/bash

# check if curl is installed
if ! command -v curl >/dev/null; then
    echo >&2 "curl is not installed"
    exit 1
fi

# check if jq is installed
if ! command -v jq >/dev/null; then
    echo >&2 "jq is not installed"
    exit 1
fi

# default settings for rpc
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

# parse method
method=$1 && shift

# iterate over the remaining arguments
for param in "$@"; do

    # if param contains "q:" then quote the value
    if [[ $param =~ "q:" ]]; then
        params="$params, \"$param\""
    else
        params="$params, $param"
    fi

    params="${params%,}"

done

# make rpc and save response
response=$(
    curl -s \
        --user "$username:$password" \
        --data-binary "{\"jsonrpc\":\"1.0\",\"id\":\"request\",\"method\":\"$method\",\"params\": [$params]}" \
        -H 'content-type: text/plain;' "http://$ip:$port/"
)

# depending on response type, print the result
result=$(echo "$response" | jq -r '.result')
error=$(echo "$response" | jq -r '.error')

if [ "$error" != "null" ]; then
    echo "$error" | jq .
    exit 1
fi

echo $result | jq -e . >/dev/null 2>&1 

if [ $? != 0 ]; then
    echo "$result"
    exit 0
fi

echo $result | jq .
