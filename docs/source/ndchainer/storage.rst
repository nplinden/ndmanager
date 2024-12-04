.. _ndc_storage:

Data Storage
------------

Depletion chains installed with NDChainer are stored in the path specified by the ``NDMANAGER_CHAINS`` variable.
In this directory, librarie are stored using the following structure:

.. code-block:: text

    # Directory structure for the foo library
    $NDMANAGER_CHAINS
     ├── jeff33-fast.yml
     └── jeff33-thermal.yml

The names of the files being the name provided in the input file.
