#!/bin/bash

if ! command -v curl >/dev/null; then
    echo "curl is not installed"
    exit 1
fi

ip_address=$1 && shift
port=$1 && shift
username=$1 && shift
password=$1 && shift
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


curl -s \
    --user "$username:$password" \
    --data-binary "{\"jsonrpc\":\"1.0\",\"id\":\"request\",\"method\":\"$method\",\"params\": [$params]}" \
    -H 'content-type: text/plain;' "http://$ip_address:$port/"

