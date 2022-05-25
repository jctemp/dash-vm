# OPTIONS

This document will describe the different options a devnet tool should offer to give a user the possibility to create a devnet
without having the stress of having to manually every node by hand. The options are the following.

## SEEDNODE

This type of node does not exist in the Dash network. Conceptually it is the initial node of the local network creating all the required information for a network to be able to run a devnet. Its tasks are to generate the sporks and platform keys. Besides that, it also takes care of the collaterals for the masternodes, and it should provide an option for nodes to find other nodes in the network.

```
seednode: inital node to setup a devnet
```

## MASTERNODE

Masternodes are the same as described by the Dash Core. One could create a masternode only if the network were _"initialized_" with a seednode.

```
masternode: create a masternode for a devnet
```

## FULLNODE

This type of node is one there to ensure network stability. The idea is that one could create a fullnode with mining capabilities or which is acting as a connection point for other nodes.

```
fullnode: vanilla dash fullnode
```
