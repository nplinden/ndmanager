.. _ndchainer:

===================
NDChainer module
===================

The NDChainer provides the ``ndc`` command to manage your chain files for
use with OpenMC.
All chain files are stored in the ``$NDMANAGER_HDF5/chains`` directory

``list``
--------

The ``ndc list`` command shows the chains file that are available for use
with OpenMC:

.. code-block::

    $ ndc list
    ------------------------------------------  Available Chains  -------------------------------------------
    jeff33           A depletion chain based on the JEFF-3.3 evaluations.
    jeff33-short     A depletion chain based on the JEFF-3.3 evaluations, reduced to include only nuclide
                     with a half-life higher than a day.

``build``
---------

The ``ndc build`` command allows you to build a chain file in the xml format
from a descriptive Yaml file, in a format similar to the one used by the NDOmcer module:

.. code-block:: yaml

    name: jeff33-short
    description: |
      A depletion chain based on the JEFF-3.3 evaluations, reduced
      to include only nuclide with a half-life higher than a day.
    halflife: 8.6e4
    n:
      basis: jeff33
      ommit: C0
      add:
        endfb8: Ta180 C12 C13 O17
    decay:
      basis: jeff33
    nfpy:
      basis: jeff33

The Yaml file must contain a chain name and description, and can optionnaly
include a ``halflife`` field which sets a minimum half-life under which
nuclids will be excluded from the chain.

All subsequent field are related to the ENDF6 file sublibraries that will be used to
build the chain file: ``n`` for incident neutron data, ``decay`` for radioactive decay data,
``nfpy`` for neutron induced fission yield data.

All of these field require a ``basis`` subfield to indicate a default source of ENDF6
tapes to use.
Two additionnal subfields can be added:

* ``ommit`` takes a list of nuclide that will be ommitted from the build.
* ``add`` takes subfields with the name of other ENDF6 libraries, and a list of nuclides to add to the build. If the nuclides already exist in the basis ENDF6 library, they will be substituted.

Once the Yaml file is done, you can execute the build command:

.. code-block::

    ndc build jeff33-chain.yml

Environment Module Integration
-------------------------------

A common way of defining the nuclear data library to use for an OpenMC
simulation is to set the ``OPENMC_CHAIN_FILE`` environment variable
to the path to the desired ``xml`` file.

NDManager allows for the automatic creation of configuration files for
the `Environment Modules <https://modules.sourceforge.net/>`_ system,
a software often used on HPC clusters to manage shell environments.

If the ``NDMANAGER_MODULEPATH`` environment variable is set, NDManager
will automatically create a module file in its location when a chain is built.
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

Loading a chain with ``module load`` will automatically set the
required environment variables.
