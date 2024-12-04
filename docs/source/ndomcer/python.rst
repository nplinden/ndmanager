.. _ndo_python:

Python API
----------

You can use NDManager to set the cross-sections library to use for an OpenMC run.

.. code:: python

   from ndmanager.API.openmc import set_nuclear_data
   set_nuclear_data("jeff33")

The name provided to the ``set_nuclear_data`` function should correspond to a library installed
or built with NDOmcer, i.e. it should show up in ``ndo list``.
The ``set_nuclear_data`` function work by settings the ``openmc.config['cross_sections']``
value to the path to the correct ``cross_sections.xml`` file.
