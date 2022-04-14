#!/bin/bash

while ! pgrep dashd > /dev/null ; do sleep 1; done

dash-cli mnsync reset
while ! dash-cli mnsync next | grep -q "FINISHED" >/dev/null; do sleep 1; done
