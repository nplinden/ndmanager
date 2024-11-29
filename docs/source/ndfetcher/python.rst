.. python:

Python API
----------

NDManager provides some python API to interact with your database.

.. code-block::

    In [1]: from ndmanager import get_endf6
       ...: get_endf6("endfb71", "n", "Pu239")
    Out[1]: PosixPath('/Users/nlinden/.ndmanager/endf6/endfb71/n/Pu239.endf6')

A typical use for this would be for loading the ENDF6 tape into an OpenMC
``IncidentNeutron`` object:

.. code-block::

      In [1]: from ndmanager import get_endf6
         ...: from openmc.data import IncidentNeutron
         ...: tape = get_endf6("endfb8", "n", "Pu239")
         ...: n = IncidentNeutron.from_endf(tape)
