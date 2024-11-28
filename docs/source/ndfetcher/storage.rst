.. storage:

Data Storage
------------

Nuclear data libraries installed with NDFetcher are stored in the path specified by the 
``NDMANAGER_ENDF6`` variable.
In this directory, librarie are stored using the following structure:

.. code-block:: text

    # Directory structure for the foo library
    $NDMANAGER_ENDF6
    └──foo
       ├── ard
       │   ├── C.endf6
       │   ├── H.endf6
       │   └── Pu.endf6
       ├── n
       │   ├── Am242_m1.endf6
       │   ├── C12.endf6
       │   └── H1.endf6
       ├── photo
       │   ├── C.endf6
       │   ├── H.endf6
       │   └── Pu.endf6
       └── tsl
           ├── tsl_0002_para-H.endf6
           └── tsl_0037_H(CH2).endf6

Notice that ENDF6 tape are renamed using the ``{gnds_name}.endf6`` format if they are nuclide-specific,
and to the ``{element_name}.endf6`` format if they are element-specific.
TSL files keep their original name but their extension is set to ``.endf6`` to clearly identify
them as ENDF6 tapes.