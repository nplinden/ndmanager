FROM openmc/openmc

WORKDIR /wrk

RUN mkdir endf6 nuclear_data modulefiles

ENV NDMANAGER_ENDF6="/wrk/endf6"

ENV NDMANAGER_HDF5="/wrk/nuclear_data"

ENV NDMANAGER_MODULEPATH="/wrk/modulefiles"

RUN pip install git+https://github.com/nplinden/ndmanager.git