.. _configuration:

Configuration
-------------

NDManager allows you to manage databases for different kinds of files:

* ENDF6 evaluation nuclear data files 
* HDF5 processed nuclear data files 
* XML depletion chain files 

The directories in which these databases will be stored can be specified
using the following environment variables: ``NDMANAGER_ENDF6``,
``NDMANAGER_HDF5``, ``NDMANAGER_CHAINS``.

You can also define these paths in a YAML file located at
``$HOME/.config/ndmanager/settings.yml``:

.. code-block:: yaml

    NDMANAGER_ENDF6: /path/to/endf6
    NDMANAGER_HDF5: /path/to/hdf5
    NDMANAGER_CHAINS: /path/to/chains

If no path is set, the data will be stored in ``$HOME/.config/ndmanager``