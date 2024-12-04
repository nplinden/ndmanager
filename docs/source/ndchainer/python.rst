.. _ndc_python:

Python API
----------

You can use NDManager to set the depletion chain to use for an OpenMC run.

.. code:: python

   from ndmanager.API.openmc import set_chain
   set_chain("jeff33-fast")

The name provided to the ``set_chain`` function should correspond to a library installed or built with NDChain, i.e. it should show up in ``ndc list``.

Alternatively, you can use ``set_nuclear_data`` to set both the cross-sections and depletion chains at the same time:

.. code:: python

   from ndmanager.API.openmc import set_nuclear_data
   set_nuclear_data("jeff33", "jeff33-fast")

