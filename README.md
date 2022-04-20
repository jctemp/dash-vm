# DASHUP

## Description

An automation tool to create a dash network.

## Usage

```
# 1)
cd
python3 -m venv dashup
source dashup/bin/activate
pip install --editable /vagrant

# 2) use program

# get info
dashup

dashup core
dashup seednode

dashup core
dashup masternode

dashup platform seednode
dashup platform masternode

. /vagrant/shell-scripts/service_helper.sh --source-only

drive_fork&
dpi_fork&
stream_fork&

tenderdash node

less ~/platform/packages/js-drive/abci.log
less ~/platform/packages/dapi/api.log
less ~/platform/packages/dapi/core-streams.log

npm i dash

grpcurl -plaintext -proto protos/core/v0/core.proto \
    10.0.0.20:3010 \
    org.dash.platform.dapi.v0.Core/getStatus

```

## STEPS

1) Create Seednode
2) Create Masternode
3) do platform seednode
4) do platform masternode