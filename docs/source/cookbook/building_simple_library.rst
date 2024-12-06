.. _building_simple_library:

Building a Simple HDF5 Library
------------------------------

Let's say you want to build an HDF5 library based on the ENDF-B/VIII.0 evaluations.
The first step is downloading the corresponding tapes from the IAEA database, I usually use as many processes as possible using the ``-j`` flag:

.. code-block:: console

   $ ndf install endfb8 -j 30

Most of the time requirement for downloading the libraries is in the overhead of making the HTTP requests rather than actually receiving data, so using multiple processes is very beneficial.

Once the installation is done, define what your library should look like in a YAML file:

.. code-block:: yaml

    # endfb8.yml
    name: endfb8
    summary: A library based on the ENDF-B/VIII.0 evaluations.
    description: |
      This defines a library based on the ENDF-B/VIII.0 evaluations.
    neutron:
      base: endfb8
      temperatures: 250 294 600 900 1200 2500
    photon:
      base: endfb8
    tsl:
      base: endfb8

Now run NDOmcer with:

.. code-block:: console

   $ ndo build endfb8.yml -j 30

You can then check that you can use the library correctly with OpenMC:

.. code-block:: python

   from ndmanager.API.openmc import set_nuclear_data
   from reactor import model
   set_nuclear_data("endfb8")
   model.run()

This should not return any error.

I you'd like to add new temperatures after the library is already built, you can rerun NDOmcer with new value.
Only temperature that do not already exist in the processed library with be built.
The resulting file will then be merged into the library:

.. code-block:: console

   $ ndo build endfb8.yml -j 30 --temperatures 400


