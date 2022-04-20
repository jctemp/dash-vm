#!/bin/bash

cd || exit
python3 -m venv dashup
source dashup/bin/activate
pip install --editable /vagrant
