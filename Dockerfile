FROM debian:bookworm

WORKDIR /root
RUN mkdir /ndmanager

# Installing dependencies
RUN apt-get update -y && \
    apt-get upgrade -y && \
    apt-get install -y python3-pip python-is-python3 git \
    build-essential cmake python3-venv \
    gfortran libhdf5-dev && \
    apt-get autoremove

# Python setup
RUN python3 -m venv /ve \
    && /ve/bin/pip install --upgrade pip

# NJOY installation
RUN git clone --single-branch --depth 1 https://github.com/njoy/NJOY2016 \
    && cd NJOY2016 \
    && mkdir build \
    && cd build \
    && cmake -Dstatic=on .. \
    && make 2>/dev/null -j${compile_cores} install \
    && cd $HOME \
    && rm -rf NJOY2016

# OpenMC installation
RUN git clone https://github.com/openmc-dev/openmc.git \
    && cd openmc \
    && mkdir build \
    && cd build \
    && cmake -DCMAKE_BUILD_TYPE=Release .. \
    && make -j 4 \
    && make install \
    && cd .. \
    && /ve/bin/pip install . \
    && cd $HOME \
    && rm -rf openmc

# Sandy installation
RUN git clone --branch v1.1 https://github.com/luca-fiorito-11/sandy.git \
    && cd sandy \
    && /ve/bin/pip install . \
    && cd $HOME \
    && rm -rf sandy

# Install the develop version of NDManager
RUN git clone https://github.com/nplinden/ndmanager.git \
    && cd ndmanager \
    && /ve/bin/pip install . \
    && cd $HOME \
    && rm -rf ndmanager

# Define NDMANAGER environment variables
ENV NDMANAGER_ENDF6="/ndmanager/endf6"
ENV NDMANAGER_HDF5="/ndmanager/hdf5"
ENV NDMANAGER_CHAINS="/ndmanager/chains"
ENV PATH=/ve/bin:$PATH