.. _ndo_storage:

Data Storage
------------

Nuclear data libraries installed with NDOmcer are stored in the path specified by the 
``NDMANAGER_HDF5`` variable.
In this directory, librarie are stored using the following structure:

.. code-block:: text

    # Directory structure for the foo library
    $NDMANAGER_HDF5
    └──cendl32
       ├── cross_sections.xml
       ├── input.yml
       └── neutron
           ├── Ag0.h5
           ├── Ag107.h5
           ├── Ag109.h5
           └── Al27.h5

The ``input.yml`` contains the original input file used to build the library.
