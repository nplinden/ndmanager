NDManager
=========

|Coverage Status|

NDManager is a python package that helps you manage your nuclear data
files in a clean manner.

It provides an API and a CLI for creating and interacting with a
database of ENDF6 files, as well as processed data files and depletion
chain files in the OpenMC format.

In addition, it encapsulate the
`sandy <https://github.com/luca-fiorito-11/sandy>`__ nuclear data
sampling tool to help you easily generate perturbed files in the OpenMC
HDF5 format.

Full documentation is available
`here <https://ndmanager.readthedocs.io/en/latest/>`__.

Installation
------------

NDManager is available on `PyPI <https://pypi.org/project/ndmanager/>`__
and can therefore be installed with ``pip``:

.. code-block:: console

   $ pip install ndmanager

There are however a few caveats regarding the dependencies of NDManager.
To build processed nuclear data files in the OpenMC HDF5 format, an
installation of the `NJOY <https://github.com/njoy/NJOY2016>`__
processing code as well as the
`OpenMC <https://github.com/openmc-dev/openmc>`__ python API is
required. These can’t be installed with pip so you will need to install
them separately.

NDManager also uses sandy to generate perturbed data files, currently
the prefered version is ``v1.1`` and is not available on PyPI, you can
install it manually with to following command:

.. code-block:: console

   $ pip install git+https://github.com/luca-fiorito-11/sandy.git@v1.1

Configuration
-------------

NDManager allows you to manage databases for different kinds of files:
\* ENDF6 evaluation nuclear data files \* HDF5 processed nuclear data
files \* XML depletion chain files \* HDF5 sampled nuclear data files

The directories in which these databases will be stored can be specified
using the following environment variables: ``NDMANAGER_ENDF6``,
``NDMANAGER_HDF5``, ``NDMANAGER_CHAINS``, ``NDMANAGER_SAMPLES``.

You can also define these paths in a YAML file located at
``$HOME/.config/ndmanager``:

.. code:: yaml

   NDMANAGER_ENDF6: /path/to/endf6
   NDMANAGER_HDF5: /path/to/hdf5
   NDMANAGER_CHAINS: /path/to/chains
   NDMANAGER_SAMPLES: /path/to/samples

If no path is set, the data will be stored in
``$HOME/.config/ndmanager``

Using NDManager
---------------

The Fetcher Module ``ndf``
~~~~~~~~~~~~~~~~~~~~~~~~~~

The ``ndf`` module acts as a kind of package manager for evaluated
nuclear data files. It uses the `IAEA
ENDF-Archive <https://www-nds.iaea.org/public/download-endf/>`__ as an
online source of ENDF6 files.

Most of the libraries in this repo have a common directory structure
making them easy to parse. You can list the available libraries using
the ``ndf list`` command:

.. code-block:: console

   $ ndf list
   ----------------------------------------------------  Available libraries  ----------------------------------------------------
   brond22              BROND-2-2            [ ]: BROND-2 USSR evaluated neutron data library, issued in 1992
   brond31              BROND-3.1            [✓]: BROND-3.1 Russian evaluated neutron data library, issued in 2016
   cendl31              CENDL-3.1            [ ]: CENDL-3.1 Chinese evaluated neutron data library, issued in 2009
   cendl32              CENDL-3.2            [ ]: CENDL-3.2 Chinese evaluated neutron data library, issued in 2020
   endfb70              ENDF-B-VII.0         [ ]: ENDF/B-VII.0 U.S. Evaluated Nuclear Data Library, issued in 2006
   endfb71              ENDF-B-VII.1         [ ]: ENDF/B-VII.1 U.S. Evaluated Nuclear Data Library, issued in 2011
   endfb8               ENDF-B-VIII.0        [✓]: ENDF/B-VIII.0 U.S. Evaluated Nuclear Data Library, issued in 2018
   endfb81              ENDF-B-VIII.1        [ ]: ENDF/B-VIII.1 U.S. Evaluated Nuclear Data Library, issued in 2024
   fendl32b             FENDL-3.2b           [ ]: FENDL-3.2b Fusion Evaluated Nuclear Data Library, 2022
   jeff31               JEFF-3.1             [ ]: JEFF-3.1 Evaluated nuclear data library of the OECD Nuclear Energy Agency
   jeff311              JEFF-3.1.1           [✓]: JEFF-3.1 Evaluated nuclear data library of the OECD Nuclear Energy Agency
   jeff312              JEFF-3.1.2           [ ]: JEFF-3.1.2 Evaluated nuclear data library of the OECD Nuclear Energy Agency
   jeff33               JEFF-3.3             [✓]: JEFF-3.3 Evaluated nuclear data library of the OECD Nuclear Energy Agency, 2017
   jendl32              JENDL-3.2            [ ]: JENDL-3.2 Japanese evaluated nuclear data library, 1994
   jendl4               JENDL-4.0            [ ]: JENDL-4.0 Japanese evaluated nuclear data library, 2010
   jendl5               JENDL-5-Aug2023      [ ]: JENDL-5 Japanese evaluated nuclear data library, 2021
   tendl2021            TENDL-2021           [ ]: TENDL-2021 TALYS-based Evaluated Nuclear Data Library, 2021
   tendl2023            TENDL-2023           [✓]: TENDL-2023 TALYS-based Evaluated Nuclear Data Library, 2023
   -------------------------------------------------------------------------------------------------------------------------------

.. |Coverage Status| image:: https://coveralls.io/repos/github/nplinden/ndmanager/badge.svg?branch=develop
   :target: https://coveralls.io/github/nplinden/ndmanager?branch=develop
