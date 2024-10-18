.. _installation:

============
Installation
============

NDManager is available on `PyPI <https://pypi.org/project/ndmanager/>`_ a can therefore
be installed by running the following command:

.. code-block:: console

   $ pip install ndmanager

To use the NDManager's ``ndo`` command to build process nuclear data libraries, you
will need to install OpenMC.
Fortunately only the python API of OpenMC is needed, so running the following command
should be enough:

.. code-block:: console

   $ pip install git+https://github.com/openmc-dev/openmc.git

A full installation of OpenMC is recommanded however, especially if you want your processed files
to be useful.

If you want to install the development version of NDManager you can run to following command:

.. code-block:: bash

   pip install git+https://github.com/nplinden/ndmanager.git
