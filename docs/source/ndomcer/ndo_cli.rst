.. _ndo_cli:

The ``ndo`` Command
-------------------

The NDOmcer module provides the ``ndo`` command to manage your HDF5 OpenMC
processed nuclear data files.
There are two ways of obtaining nuclear data in the HDF5 format for use with
OpenMC: downloading from the official OpenMC website and build your own library
using OpenMC's python API.

All data is stored in a directory defined by the ``NDMANAGER_HDF5``
environment variable, which you can set in your ``.bashrc`` file or equivalent.

Listing Installed and Installable libraries
+++++++++++++++++++++++++++++++++++++++++++

The ``ndo list`` shows the OpenMC nuclear data libraries installed on your system as well
the official libraries that you can download from the OpenMC website:

.. code-block:: console

    $ ndo list
    ----------------------------------------------  Installable Libraries  ----------------------------------------------
    official/endfb71 ENDF-B/VII.1    [✓]: Official OpenMC library based on ENDF-B/VII.1
    official/endfb8  ENDF-B/VIII.0   [ ]: Official OpenMC library based on ENDF-B/VIII.0
    official/jeff33  JEFF-3.3        [ ]: Official OpenMC library based on JEFF-3.3
    lanl/endfb70     ENDF-B/VII.0    [✓]: ENDF-B/VII.0 based library converted from ACE files distributed with MCNP5/6
    lanl/endfb71     ENDF-B/VII.1    [✓]: ENDF-B/VII.1 based library converted from ACE files distributed with MCNP5/6
    lanl/endfb8      ENDF-B.VIII.0   [ ]: ENDF-B/VIII.0 based library converted from ACE files distributed by Los Alamos
                                          National lab (LANL)
    ------------------------------------------------  Custom Libraries  -------------------------------------------------
    cendl32          A library based on the CENDL-3.2 evaluations.

Here, you can see that I have installed three official libraries, and that I personnaly built
an additionnal one based on CENDL-3.2.

Installing Official Libraries
+++++++++++++++++++++++++++++

The ``ndo install`` lets you download and install libraries from OpenMC's official website:

.. code-block:: console

   $ ndo install lanl/endfb8

This will download the library archive, extract it, and move the files to NDManager's database.

Removing a Library
++++++++++++++++++

If a library takes too much space on you disk you can simply remove it:

.. code-block:: console

   $ ndo remove lanl/endfb8

Building Your Own Library
+++++++++++++++++++++++++

The main purpose of the NDOmcer module is to build nuclear data libraries in the HDF5 format
for use in OpenMC.
To do this the ``ndo build`` command should be provided the path to a YAML file containing
a structured description of the target library's content.
A valid ``ndo`` input file should contain the following information:

* A ``summary`` element giving a short description of the library
* A ``description`` element giving a more verbose description of the library
* A ``name`` element that will be used to refer to the built library
* A ``neutron`` element with the following sub-elements

  * The ``base`` element should refer to an ENDF6 library installed with NDFetcher, this is the main source of the ENDF6 tapes for your library
  * The ``temperature`` element lists the temperatures for Doppler broadening
  * The ``ommit`` element lists the nuclide present in the ENDF6 library that you want to discard
  * The ``add`` element tells NDOmcer to use ENDF6 tapes from a library different that the base one. It contains keys named after the desired library, with a list of the desired nuclides

* A ``photon`` element with the following sub-elements

  * The ``base`` element should refer to an ENDF6 library installed with NDFetcher, this is the main source of the ENDF6 tapes for your library
  * The ``ommit`` element lists the atoms present in the ENDF6 library that you want to discard
  * The ``add`` element tells NDOmcer to use ENDF6 tapes from a library different that the base one. It contains keys named after the desired library, with a list of the desired atoms
* A ``tsl`` element with the following sub-elements
  * The ``base`` element should refer to an ENDF6 library installed with NDFetcher, this is the main source of the ENDF6 tapes for your library
  * The ``ommit`` element lists the TSL files present in the ENDF6 library that you want to discard, TSL files should be refered with their explicit names in the NDFetcher database
  * The ``add`` element tells NDOmcer to use ENDF6 tapes from a library different that the base one. It contains element named after the desired libraries. These elements contain element named after NDFetcher-installed TSL tapes. These elements contain the name of the nuclide to use to build the TSL file
  * The ``temperatures`` element contains the temperature at which to build the files. It contains element named after the desired file. These elements contain the list of temperatures to build (Available temperatures depend on the TSL tape's content)

Here is a sample of what an ``ndo`` file to build a JEFF-3.3 based library looks like:

.. code-block:: yaml

    summary: A library based on the JEFF-3.3 evaluations.
    description: |
      This defines a library based on the JEFF-3.3 evaluations for
      neutron cross-sections and thermal scattering laws, and on
      ENDF-B/VIII.0 for gamma photoatomic reactions and atomic
      relaxation.

      Some evaluations from other libraries are used instead
      or in addition to JEFF-3.3 evaluations:
      C0:     JEFF-3.3 contains C0 and C13 isotopes of carbon. Since
              using C0 can cause some issues running the same problem
              with multiple libraries, I prefer to remove them and
              use ENDF-B/VIII.0 carbon instead. Normally you would also
              build TSL libraries using C0, I substitute it for C12.
      C12:    See C0
      C13:    See C0. The C13 evaluation of JEFF-3.3 is faulty anyway.
      Ta180:  OpenMC wrongly defines natural Ta as containing Ta180
              instead of Ta180M because ENDF-B/VIII.0 has no Ta180M
              evaluation. Since JEFF-3.3 has no Ta180, materials
              containing Ta will crash simulations.
      O17:    The O17 evaluation of JEFF-3.3 is faulty. I use the ENDF-B/VIII.0
              evaluation instead.
    name: jeff33
    neutron:
      base: jeff33
      temperatures: 250 294 600 900 1200 2500
      ommit: C0
      add:
        endfb8: Ta180 C12 C13 O17
    photon:
      base: endfb8
    tsl:
      base: jeff33
      add:
        jeff33:
          tsl_0031_Graphite.endf6: C12

Once you input file is done, you can execute the build command.
You can allocate multiple processes to the build using the ``-j`` flag:

.. code-block:: console

   $ ndo build jeff33.yml -j 40

You can remove the existing library using ``ndo remove`` or provide the ``--clean`` to 
``ndo build`` overwrite it.
You can override the list of neutron temperatures using the ``--temperatures`` flag following by a
list of temperatures.

.. code-block:: console

   $ ndo build jeff33.yml --clean --temperatures 600 -j 40

If the library name already exists and you just want to add new temperature to the build, you can rerun the build command with new temperature and these build be simply added to the existing files.


Dealing With Negative KERMA Values
++++++++++++++++++++++++++++++++++

The NDOmcer provides a last command that fills a very specific purpose:
fixing the issues of negative kerma (MT=301 reactions) for many isotopes
in some evaluations.
These negative kermas can cause unphysical results if you are trying to tally
heating in a material than contains them.

The ``ndo sn301`` (as in "substitute negative values for MT=301") takes a target
library name that will be modified, and a list of source libraries from which MT=301 values
will be taken
These sources libraries will be searched one by one util a suitable MT=301 value is found.
If none is found, the kerma will be set to zero.

Typical use:

.. code-block:: console

   $ ndo sn301 --target jeff33 --sources endfb8 jendl5 cendl32 tendl23

Not providing any source library will simply set the faulty cross-sections
to zero.

