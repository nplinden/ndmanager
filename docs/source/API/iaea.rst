.. _iaea:

===================================
IAEA Nuclear Data Service Interface
===================================

NDManager provides an API for interacting with the `IAEA Nuclear Data Service
repository <https://www-nds.iaea.org/public/download-endf/>`_ of evaluated nuclear data files.
This interface relies on the common directory structure used by most libraries stored on this 
website:

.. code:: text

    https://www-nds.iaea.org/public/download-endf/
    └── Library
        ├── 000-NSUB-index.htm
        ├── sub1-index.html
        ├── sub2-index.html
        ├── sub3-index.html
        ├── sub1
        │   ├── tape1.zip
        │   └── tape2.zip
        ├── sub2
        │   ├── tape1.zip
        │   └── tape2.zip
        └── sub3
            ├── tape1.zip
            └── tape2.zip

.. autosummary::
   :toctree: generated
   :nosignatures:
   :template: myclass.rst

   ndmanager.IAEA
   ndmanager.IAEALibrary
   ndmanager.IAEASublibrary
