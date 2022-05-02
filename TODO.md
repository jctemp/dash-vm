# BETTER AUTOMATION OF THE SETUP PROCESS

## SEEDNODE

1. install dashcore on machine
2. write dashd to .dashcore
3. prepare network
4. create masternode data
5. write data in a specific way => `masternodes.json`
6. update .dashcore/dash.conf
7. add cronjob to mine every 3min block

## MASTERNODE

1. read `masternodes.json`
2. install dashcore on machine
3. write dashd to .dashcore with read in data
4. install sentinel
5. add to cronjob

## SEEDNODE PLATFORM

1. activate sporks
2. mining until quorum and chainlock is present

## MASTERNODE PLATFORM

TODO: re-think process