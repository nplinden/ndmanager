#!/bin/bash
set -ex
sudo apt install libhdf5-dev 
cd $HOME
git clone https://github.com/openmc-dev/openmc.git
cd openmc && mkdir build && cd build
cmake .. && make -j4 && sudo make install
cd .. && pip install .