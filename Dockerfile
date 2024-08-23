FROM openmc/openmc

WORKDIR /wrk

RUN mkdir endf6 nuclear_data modulefiles

ENV ENDF6_PATH="/wrk/endf6"

ENV OPENMC_NUCLEAR_DATA="/wrk/nuclear_data"

ENV NDMANAGER_MODULEPATH="/wrk/modulefiles"

RUN pip install git+https://github.com/nplinden/ndmanager.git