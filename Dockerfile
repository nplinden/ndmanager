FROM openmc/openmc

WORKDIR /wrk

RUN mkdir .ndmanager .ndmanager/endf6 .ndmanager/nuclear_data .ndmanager/modulefiles

ENV NDMANAGER_ENDF6="/wrk/.ndmanager/endf6"

ENV NDMANAGER_HDF5="/wrk/.ndmanager/hdf5"

ENV NDMANAGER_MODULEPATH="/wrk/.ndmanager/modulefiles"

RUN pip install git+https://github.com/nplinden/ndmanager.git