.. _nds_python:

Python API
----------

You can use NDManager's python API to easily iterate over your perturbed library's samples:

.. code:: python

   from ndmanager.API.openmc import PerturbationList, set_nuclear_data
   from reactor import model

   libraries = PerturbationList("jeff33-Pu239", "HDF5")
   for p in libraries:
       set_nuclear_data(p)
       model.run()

