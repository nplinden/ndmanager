FROM openmc/openmc

WORKDIR /wrk

RUN mkdir .ndmanager .ndmanager/endf6 .ndmanager/nuclear_data

ENV NDMANAGER_ENDF6="/wrk/.ndmanager/endf6"

ENV NDMANAGER_HDF5="/wrk/.ndmanager/hdf5"

RUN pip install git+https://github.com/nplinden/ndmanager.git