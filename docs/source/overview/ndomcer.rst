.. _ndomcer:

==============
NDOmcer module
==============

The NDOmcer module provides the ``ndo`` command to manage you HDF5 OpenMC
processed nuclear data files.
There are two ways of obtaining nuclear data in the HDF5 format for use with
OpenMC: downloading from the official OpenMC website and build your own library
using OpenMC's python API.

All data is stored in a directory defined by the ``NDMANAGER_HDF5``
environment variable, which you can set in your ``.bashrc`` file or equivalent.

``list``
--------

The ``ndo list`` command shows OpenMC nuclear data libraries available for
download:

.. code-block::

    $ ndo list
    --------------------------------------------------------  Available libraries  ---------------------------------------------------------
    official/endfb71 ENDF-B/VII.1    [ ]: Official OpenMC library based on ENDF-B/VII.1
    official/endfb8  ENDF-B/VIII.0   [✓]: Official OpenMC library based on ENDF-B/VIII.0
    official/jeff33  JEFF-3.3        [✓]: Official OpenMC library based on JEFF-3.3
    lanl/endfb70     ENDF-B/VII.0    [ ]: ENDF-B/VII.0 based library converted from ACE files distributed with MCNP5/6
    lanl/endfb71     ENDF-B/VII.1    [ ]: ENDF-B/VII.1 based library converted from ACE files distributed with MCNP5/6
    lanl/endfb8      ENDF-B.VIII.0   [ ]: ENDF-B/VIII.0 based library converted from ACE files distributed by Los Alamos National lab (LANL)
    ---------------------------------------------------------------------------------------------------------------------------------------

All libraries are shown with a shorthand name containing a prefix and the
name of the source set of evaluations.
A short description is provided and an indication on the library's installation
is shown.
For now, the only source of data is the official OpenMC website.

``install``
-----------

The ``ndo install`` command allows you to install a library:

.. code-block:: bash

    ndo install lanl/endfb71

``build``
---------

The main purpose of the NDOmcer module is to build nuclear data libraries in the HDF5 format
for use in OpenMC.
To do this the ``ndo build`` command should be provided the path to a Yaml file containing
a structured description of the target library's content.
Here is a sample Yaml file to build a JEFF-3.3 based library with some modifications:

.. code-block:: yaml

    name: jeff33
    description: |
        This defines a library based on the JEFF-3.3 evaluations for
        neutron cross-sections and thermal scattering laws, and on
        ENDF-B/VIII.0 for photoatomic reactions and atomic
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
    temperatures: 250 294 600 900 973 1200
    n:
        base: jeff33
        ommit: C0
        add:
            endfb8: Ta180 C12 C13 O17
    tsl:
        base: jeff33
        substitute:
            C0: C12
    photo:
        base: endfb8
    ard:
        base: endfb8

The file contains two metadata fields to give the target library a name
and description, as well as a temperatures field.
All subsequent field are related to the ENDF6 file sublibraries that will be used to
build the HDF5 files: ``n`` for incident neutron data, ``tsl`` for thermal scattering law
data, ``photo`` for photo-atomic data, and ``ard`` for atomic relaxation data.

All of these field require a ``base`` subfield to indicate a default source of ENDF6
tapes to use. For the ``n``, ``photo``, and ``ard`` fields, two additionnal subfields can be
added:

* ``ommit`` takes a list of nuclide that will be ommitted from the build.
* ``add`` takes subfields with the name of other ENDF6 libraries, and a list of nuclides to add to the build. If the nuclides already exist in the base ENDF6 library, they will be substituted.

To perform similar operations for thermal scattering, you will need to provide the full TSL
tape names.
The ``tsl`` takes an additionnal ``substitute`` subfield to fill the gaps when nuclides
needed for TSL computation have been expicitely ommited.

Once the Yaml file is done, you can execute the build command:

.. code-block::

    ndo build jeff33.yml


``remove``
----------

The ``ndo remove`` command allows you to uninstall a library:

.. code-block::

    $ ndo remove jeff33 lanl/endfb71


Environment Module Integration
-------------------------------

A common way of defining the nuclear data library to use for an OpenMC
simulation is to set the ``OPENMC_CROSS_SECTIONS`` environment variable
to the path to the desired ``cross_sections.xml`` file.

NDManager allows for the automatic creation of configuration files for
the `Environment Modules <https://modules.sourceforge.net/>`_ system,
a software often used on HPC clusters to manage shell environments.

If the ``NDMANAGER_MODULEPATH`` environment variable is set, NDManager
will automatically create a module file in its location when a library is
installed or built.
To allow the module files to be discovered by the ``module`` command,
the content of ``NDMANAGER_MODULEPATH`` should also be appended to the
``MODULEPATH`` variable.
A typical configuration in your ``.bashrc`` file or equivalent might be:

.. code-block:: bash

    export NDMANAGER_MODULEPATH=~/.ndmanager/modulefiles
    export MODULEPATH=$MODULEPATH:$NDMANAGER_MODULEPATH

Once this is done, the ``module avail`` command should show the desired
libraries:

.. code-block::

    $ module avail
    ---------------------------- /Users/nlinden/.ndmanager/modulefiles ----------------------------
    xs/jeff33  xs/lanl-endfb71

    ----------------------- /opt/homebrew/Cellar/modules/5.4.0/modulefiles ------------------------
    dot  module-git  module-info  modules  null  use.own

    Key:
    modulepath

Loading a library with ``module load`` will automatically set the
required environment variables.

Python API
----------

NDOmcer provides a limited (for now) python API in the form of a
``set_ndl`` function that allows you to set the ``openmc.config["cross_sections"]``
variables to the right path by only provided the NDOmcer name of
the desired library:

.. code-block:: python

    from ndmanager import set_ndl
    set_ndl("jeff33")

A clunky command: ``sn301``
---------------------------

The NDOmcer provides a last command that fills a very specific purpose:
fixing the issues of negative kerma (MT=301 reactions) for many isotopes
in some evaluations.

What this commands does is take a target HDF5 library, say "jeff33",
and look for all occurences of negative values for the MT=301 reaction.
It will then go over any number of source HDF5 libraries and check if
the corresponding values are positive.
If they are, they will be used to replace the values in the target library.
If no suitable values are found, the MT=301 cross-sections in the target
library will be set to zero.

Typical use:

.. code-block::

    ndo sn301 --target jeff33 --sources endfb8 jendl5 cendl32 tendl23

Not providing any source library will simply set the faulty cross-sections
to zero.