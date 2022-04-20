#!/bin/bash

function drive_fork() {
    echo "drive"
    cd ~/platform || exit
    cd packages/js-drive && yarn node scripts/abci.js >abci.log
    echo "end"
}

function dpi_fork() {
    echo "api"
    cd ~/platform || exit
    cd packages/dapi && yarn node scripts/api.js >api.log
    echo "end"
}

function stream_fork() {
    echo "streams"
    cd ~/platform || exit
    cd packages/dapi && yarn node scripts/core-streams.js >core-streams.log
    echo "end"
}

# . /vagrant/service_helper.sh --source-only

# drive_fork&
# dpi_fork&
# stream_fork&

# less ~/platform/packages/js-drive/abci.log
# less ~/platform/packages/dapi/api.log
# less ~/platform/packages/dapi/core-streams.log