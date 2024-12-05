.. _ndc_cli:

The ``ndc`` Command
-------------------

The NDChainer provides the ``ndc`` command to manage your chain files for
use with OpenMC.
All chain files are stored in the ``$NDMANAGER_HDF5/chains`` directory.

Listing Installed and Installable Library
+++++++++++++++++++++++++++++++++++++++++

The ``ndc list`` shows the OpenMC chains installed on your system as well
the official chains that you can download from the OpenMC website:

.. code-block:: console

   $ ndc list
   ----------------------------------------  Installable Chains  -----------------------------------------
   endfb71-thermal  [✓]: A chain based on the ENDF-B/VII.1 evaluation with thermal capture branching
                          ratios
   endfb71-fast     [✓]: A chain based on the ENDF-B/VII.1 evaluation with fast capture branching ratios
   endfb8-thermal   [✓]: A chain based on the ENDF-B/VIII.0 evaluation with thermal capture branching
                          ratios
   endfb8-fast      [✓]: A chain based on the ENDF-B/VIII.0 evaluation with thermal capture branching
                          ratios
   casl-thermal     [✓]: A simplified chain as described by https://doi.org/10.2172/1256820 with thermal
                          capture branching ratios
   casl-fast        [✓]: A simplified chain as described by https://doi.org/10.2172/1256820 with fast
                          capture branching ratios
   -------------------------------------------  Custom Chains  -------------------------------------------
   jeff33-fast     jeff33-thermal

As you can see, I have installed all official chains available and added my own based on JEFF-3.3.

Installing Official Chains
++++++++++++++++++++++++++


The ``ndc install`` lets you download and install chains from OpenMC's official website:

.. code-block:: console

   $ ndc install endfb8-fast

Removing a Library
++++++++++++++++++

You can remove installed chains as well:

.. code-block:: console

   $ ndc remove endfb8-fast

Building Your Own Chain
+++++++++++++++++++++++

The main purpose of the NDChainer module is to build depletion chains in OpenMC's XML format
for use in OpenMC depletion calculation.
To do this the ``ndc build`` command should be provided the path to a YAML file containing a
structured description of the target chain's content.
A valid ``ndc`` input file contain the following information:

* A ``name`` element which will be used to refer the chain with NDManager's API
* A ``description`` element to give some context on the chain
* A ``branching_ratios`` element with a value of either ``sfr`` or ``pwr``, to set radiative capture branching ratios for fast or thermal problems. Values are taken from OpenMC's official website. `sfr <https://openmc.org/sfr-spectrum-capture-branching-ratios/>`_, `pwd <https://openmc.org/pwr-spectrum-capture-branching-ratios/>`_)
* An optional ``halflife`` element with a floating point value. Nuclides with a shorter halflife than this value will be removed from the chain and branching ratios will be redirected accordingly
* A ``n`` element for incident neutron files with the following sub-elements

  * The ``base`` element should refer to an ENDF6 library installed with NDFetcher, this is the main source of the ENDF6 tapes for your library
  * The ``ommit`` element lists the nuclide present in the ENDF6 library that you want to discard
  * The ``add`` element tells NDOmcer to use ENDF6 tapes from a library different that the base one. It contains keys named after the desired library, with a list of the desired nuclides

* A ``decay`` element with keys similar to that of the ``n`` element
* A ``nfpy`` element for neutron-induced fission product yields, with keys similar to that of the ``n`` element

Here is a sample of what an ``ndc`` input file to build a JEFF-3.3 based chain should look like:

.. code-block:: yaml
   
  name: jeff33-fast
  description: |
    A depletion chain based on the JEFF-3.3 evaluations.
  branching_ratios: sfr
  n:
    base: jeff33
    ommit: C0
    add:
      endfb8: Ta180 C12 C13 O17
  decay:
    base: jeff33
  nfpy:
    base: jeff33


Just like I did for NDOmcer, I replace JEFF's C0 nuclide with C12 and C13 from ENDF-B/VIII.0.
Once the Yaml file is done, you can execute the build command:

.. code-block::

    ndc build jeff33-chain.yml

