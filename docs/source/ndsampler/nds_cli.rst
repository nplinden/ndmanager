.. _nds_cli:

The ``nds`` Command
-------------------

The NDSampler module provides the ``nds`` command to manage your perturbed nuclear data libraries.

Building a Perturbed Library (PENDF)
++++++++++++++++++++++++++++++++++++

Building a perturbed library using the PENDF method is done using the ``nds pendf`` command.
It must be provided the path to a YAML file containing a structured description of what you want.
It should contain the following information:

* A ``summary`` element giving a short description of the perturbed library
* A ``name`` element giving a name to your perturbed library
* A ``reuse`` element telling what existing HDF5 library your perturbed library should rely on. This library should be installed with NDOmcer (i.e. it appears in ``ndo list``)
* A ``nsmp`` element telling how many samples should be created
* A ``temperature`` element telling what temperature should be used for Doppler broadening
* A ``kind`` element telling what nuclear data should be perturbed (for now, only ``xs`` is implemented)
* A ``samples`` element, containing details about what nuclide you want to perturb
  
  * This element contains sub-element structured like so:

    .. code-block:: yaml

       nuclide: xs_library cov_library@group_structure

Here is a sample of what an ``nds pendf`` input file looks like:

.. code-block:: yaml

  summary: Sampling Pu239 using TENDL2023 Covariances and a JEFF-3.3 base
  name: jeff33-Pu239
  reuse: jeff33
  nsmp: 10
  temperature: 600
  kind: xs
  samples:
    Pu239: jeff33 tendl2023@ECCO-33

This will create 10 perturbed libraries in which Pu239 cross-sections from JEFF-3.3 are perturbed using covariance matrices from TENDL-2023 on an ECCO-33 group structure, at a temperature of 600K.
All other nuclide cross-sections are taken from the ``jeff33`` library installed with NDOmcer.
The mapping to nominal cross-sections are done in the generated `cross_sections.xml` files rather than through the duplication of HDF5 files.

Building a Perturbed Library (HDF5)
++++++++++++++++++++++++++++++++++++

Building a perturbed library using the HDF5 method is done using the ``nds hdf5`` command.
It must be provided the path to a YAML file containing a structured description of what you want.
It should contain the following information:

* A ``summary`` element giving a short description of the perturbed library
* A ``name`` element giving a name to your perturbed library
* A ``reuse`` element telling what existing HDF5 library your perturbed library should rely on. This library should be installed with NDOmcer (i.e. it appears in ``ndo list``)
* A ``nsmp`` element telling how many samples should be created
* A ``kind`` element telling what nuclear data should be perturbed (for now, only ``xs`` is implemented)
* A ``samples`` element, containing details about what nuclide you want to perturb
  
  * This element contains sub-element structured like so:

    .. code-block:: yaml

      nuclide: xs_library cov_library@group_structure

Here is a sample of what an ``nds hdf5`` input file looks like:

.. code-block:: yaml

  summary: Sampling Pu239 using TENDL2023 Covariances and a JEFF-3.3 base
  name: jeff33-Pu239
  reuse: jeff33
  nsmp: 10
  kind: xs
  samples:
    Pu239: jeff33 tendl2023@ECCO-33

This will create 10 perturbed libraries in which Pu239 cross-sections from JEFF-3.3 are perturbed using covariance matrices from TENDL-2023 on an ECCO-33 group structure, at a temperature of 600K.
All other nuclide cross-sections are taken from the ``jeff33`` library installed with NDOmcer.
The mapping to nominal cross-sections are done in the generated `cross_sections.xml` files rather than through the duplication of HDF5 files.

Note that the input file is essentialy the same as the PENDF one.
The main difference between the two method is that ``nds pendf`` generates covariance matrices on the fly using ERRORR whereas ``nds hdf5`` uses preprocessed matrices written on disk.

Building Covariance Matrices
~~~~~~~~~~~~~~~~~~~~~~~~~~~~

The ``nds cov`` command allows you to build covariance matrices for a given multigroup energy structure, using the ERRORR module from NJOY.

For instance, if you have the TENDL-2023 library installed through NDFetcher, you can run:

.. code-block:: console

   $ nds cov tendl23 --ign ECCO-33

The ``ign`` argument must correspond to the name of the desired group structure, or to the associated number in NJOY.
The following table show what group structures are available.

=====  ================
  ign  Name
=====  ================
    2  CSWEG-239
    3  LANL-30
    4  ANL-27
    5  RRD-50
    6  GAM-I-68
    7  GAM-II-100
    8  LASER-THERMOS-35
    9  EPRI-CPM-69
   10  LANL-187
   11  LANL-70
   12  SAND-II-620
   13  LANL-80
   14  EURLIB-100
   15  SAND-IIA-640
   16  VITAMIN-E-174
   17  VITAMIN-J-175
   18  XMAS-NEA-LANL
   19  ECCO-33
   20  ECCO-1968
   21  TRIPOLI-315
   22  XMAS-LWPC-172
   23  VIT-J-LWPC-175
   24  SHEM-CEA-281
   25  SHEM-EPM-295
   26  SHEM-CEA-EPM-361
   27  SHEM-EPM-315
   28  RAHAB-AECL-89
   29  CCFE-660
   30  UKAEA-1025
   31  UKAEA-1067
   32  UKAEA-1102
   33  UKAEA-142
   34  LANL-618
=====  ================

Additionally you can provide the ``-j`` flag with an integer value to use multiple processes to build the matrices.
If the matrix database already exists, you can regenerate it from scratch by providing the ``--clean`` flag.

Listing Installed Perturbed Libraries
+++++++++++++++++++++++++++++++++++++

The ``nds list`` command gives you a summary of what perturbed libraries you have installed:

.. code-block:: console

   $ nds list
   Kind    Name          Base      Samples    Nuclides  Description
   ------  ------------  ------  ---------  ----------  -----------------------------------------
   HDF5    jeff33-Pu239  jeff33         10           1  Create sample for Pu239 nuclide in jeff33
   PENDF   jeff33-Pu239  jeff33         10           1  Create sample for Pu239 nuclide in jeff33
