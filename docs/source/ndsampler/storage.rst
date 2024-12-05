.. _nds_storage:

Data Storage
------------

Perturbed libraries built with NDSampler are stored in the path specified by the ``NDMANAGER_SAMPLES`` variable:

.. code-block:: text

    $NDMANAGER_SAMPLES
    ├── HDF5
    │   └── jeff33-Pu239
    │       ├── cross_sections
    │       │   ├── 0.xml
    │       │   └── 1.xml
    │       ├── input.yml
    │       ├── Pu239
    │       │   ├── 0.h5
    │       │   ├── 1.h5
    │       │   └── logs
    │       └── samples.xlsx
    └── PENDF
        └── jeff33-Pu239
            ├── cross_sections
            │   ├── 0.xml
            │   └── 1.xml
            ├── input.yml
            └── Pu239
                ├── 0.h5
                ├── 1.h5
                ├── COV_94239_MF33.tape
                ├── logs
                └── PERT_94239_MF33.xlsx

Notice that all libraries contain the original input file, an excel file summarizing the sampled perturbation, the actual HDF5 files, and a ``cross_sections.xml`` file for each sample.
In addition libraries processed with the PENDF method also save the 0K PENDF file.

Covariance matrices libraries are stored in the path specified by the ``NDMANAGER_COV`` variable:

.. code-block:: text

    $NDMANAGER_COV
    └── foo
        ├── ANL-27
        │   ├── Am242_m1.h5
        │   ├── C12.h5
        │   ├── H1.h5
        │   └── logs
        │       ├── Am242_m1
        │       ├── C12
        │       └── H1
        └── ECCO-33
            ├── Am242_m1.h5
            ├── C12.h5
            ├── H1.h5
            └── logs
                ├── Am242_m1
                ├── C12
                └── H1

