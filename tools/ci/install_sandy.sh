#!/bin/bash
set -ex
cd $HOME
git clone --branch v1.1 https://github.com/luca-fiorito-11/sandy.git
cd sandy
pip install .