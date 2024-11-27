.. _installation:

Installation
------------

The latest stable version of NDManager is available on `PyPI <https://pypi.org/project/ndmanager/>`_ 
and can therefore be installed using ``pip``:

.. code-block:: console

   $ pip install ndmanager

There are however a few caveats regarding the dependencies of NDManager.
To build processed nuclear data files in the OpenMC HDF5 format, an
installation of the `NJOY <https://github.com/njoy/NJOY2016>`_ processing
code as well as the `OpenMC <https://github.com/openmc-dev/openmc>`_
Monte-Carlo code are required. 
These can't be installed with pip so you will need to install them separately.

NDManager also uses sandy to generate perturbed data files, currently
the prefered version is v1.1 and is not available on PyPI, you can
install it manually with to following command:

.. code-block:: console

    $ pip install git+https://github.com/luca-fiorito-11/sandy.git@v1.1

For Sandy to work, you will need to define the ``NJOY`` environment variable as the path to
the NJOY binary. 
