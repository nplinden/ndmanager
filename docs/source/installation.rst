.. _installation:

=====
Setup
=====

Installation
~~~~~~~~~~~~

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

You will also need the NJOY executable in your ``PATH`` to process libraries.

If you want to install the development version of NDManager you can run to following command:

.. code-block:: bash

   pip install git+https://github.com/nplinden/ndmanager.git

Configuration
~~~~~~~~~~~~~

By default, your nuclear data will be stored in

* ``$HOME/.config/ndmanager/endf6`` for ENDF6 files
* ``$HOME/.config/ndmanager/hdf5`` for OpenMC's HDF5 processed files
* ``$HOME/.config/ndmanager/chains`` for OpenMC's chain files

You can redefine these paths by creating a ``$HOME/.config/ndmanager/settings.yml``
file containing:

.. code-block:: yaml

   NDMANAGER_ENDF6: /path/to/endf6
   NDMANAGER_HDF5: /path/to/hdf5
   NDMANAGER_CHAINS: /path/to/chains

You can also export the ``NDMANAGER_ENDF6``, ``NDMANAGER_HDF5``, and 
``NDMANAGER_CHAINS`` environment variables manually.
These environment variable will be prioritized before the content of
you settings file.

You can also change the path to your settings directory by settings the ``NDMANAGER_CONFIG``
environment variable.




