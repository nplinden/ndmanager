FROM openmc/openmc

WORKDIR /wrk

RUN pip install git+https://github.com/nplinden/ndmanager.git