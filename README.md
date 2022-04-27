# DASHUP

## Prerequisites

- Vagrant 2.2.19 +
- VirtualBox 6.1.32 +

## Description

An automation tool to create a dash network.

## Usage

Start to spawn virtual machines with the following command. You need to be in the root of the project.

```
vagrant up
```

Now you can ssh to the machines with the following command.

```
vagrant ssh <node-name>
```

Install the dashup program on every node of the network.

```bash
# create virtual env for python3 and install dashup
python3 -m venv ~/dashup && source ~/dashup/bin/activate
pip install --editable /vagrant

# if it exists already, do
source ~/dashup/bin/activate
```

### Layer 1

To setup a node in the network you have to run the following command:
```
dashup core
```
This will install core and all dependencies. It is important that you take care of doing this only on the seednode first because the seednode takes care of preparing keys for the network. Therefore you have to run this command on the seednode first.

```
dashup seednode
```
It will generate keys and wallets as funds for the masternode. After you have run this command you can run `dashup core` on the other nodes.

Now you can create masternodes in the network. However, you have to check if the seednode is running first. For this just run `dash-cli uptime` on the seednode. If the output is not an error then the seednode is running, hence you can run the following command:
```
dashup masternode
```

Here are output examples:

```bash
# Core install output
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
Setting up dashd
[INFO] Installing dashd
[INFO] Setting dashd configuration file
[INFO] Possible ip addresses:
   1) 10.0.2.15
   2) 10.0.0.10
   3) 172.17.0.1
[WARNING] USER INPUT REQUIRED
Select interface to use [1-3]: 2
[INFO] SELECTED 10.0.0.10
no crontab for vagrant
[OK] Setup complete
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

# Seednode install output
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
Seednode setup
[INFO] Setting up seednode
[INFO] Generating sporks
[INFO] Writing sporks.json
[INFO] Generating platform keys
[INFO] Writing platform_wallets.json
How many masternodes do you want to create?
[WARNING] USER INPUT REQUIRED
Count: 7
[OK] Setup complete
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

# Masternode install output
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
Masternode setup
[INFO] Setting up masternode
[INFO] Creating collateral
[INFO] Generating bls key
[INFO] Generating and funding addresses
[INFO] Retrieving config of machine
[INFO] ProTx registration
[INFO] Waiting for node to appear in masternode list
[INFO] Set bls key in config
[INFO] Installing sentinel

...

[OK] Setup complete
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
```

### Layer 2

Todo: Add description

```bash
# TODO
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

---
---


## Vagrant and Virtual Machines

### Initialize Project Directory

`vagrant init ubuntu/focal64`

- vagrant uses base images to clone VMs
- base images are called boxes, hence *ubuntu/focal64* is a box
- places all necessary files in the current directory
- `Vagrantfile` has all information about the VMs

### Boot an Environment and SSH into a machine

`vagrant up`

- after initialisation one can boot vagrant environment
- configuring the virtual machines depending on specified information in the `Vagrantfile`
- `==> default: Machine booted and ready!` is printed after the machine is started and ready to be used

`vagrant ssh <name>`

- usind the ssh command will allow to connect to the virtual machine
- inside the virtual machine use logout to exit correctly the ssh connection

```bash
$ vagrant ssh vagrant
Welcome to Ubuntu 20.04.4 LTS (GNU/Linux 5.4.0-105-generic x86_64)
 * Documentation:  https://help.ubuntu.com
 * Management:     https://landscape.canonical.com
 * Support:        https://ubuntu.com/advantage
  System information as of Wed Apr  6 09:00:41 UTC 2022
  System load:  1.43              Processes:               121
  Usage of /:   3.4% of 38.71GB   Users logged in:         0
  Memory usage: 20%               IPv4 address for enp0s3: 10.0.2.15
  Swap usage:   0%
1 update can be applied immediately.
To see these additional updates run: apt list --upgradable
The list of available updates is more than a week old.
To check for new updates run: sudo apt update
vagrant@ubuntu-focal:~$ 
```

### Destroy and Remove Environment

`vagrant destory`

- removes all resource created by a virtual machine
- confirm prompt with `y` to remove the data

`vagrant box list` + `vagrant box remove ubuntu/focal64`

- boxes can be removed by box remove + name

### Shared files

- vagrant share project directory and is under `/vagrant` inside the virtual machine
- printing the contents of the directory should show all files in the project directory

### Stop machines

`vagrant halt`

- attempts to shut down guest OS and power down the machine
- it is a clean shut down preserve information on the disk