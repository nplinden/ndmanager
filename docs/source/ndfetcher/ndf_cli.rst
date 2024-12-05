.. _ndf_cli:

The ``ndf`` Command
-------------------

The NDFetcher module provides the ``ndf`` command to manage your evaluated nuclear
data files in the ENDF6 format.
The spirit of ``ndf`` is to be used as a kind of package manager for nuclear
data libraries.
The main source of ENDF6 files for NDFetcher is the
`IAEA website <https://www-nds.iaea.org/public/download-endf/>`_, as it stores
most ENDF6 data libraries using a common, easy to parse directory structure.

NDFetcher provides three commands:

.. code-block:: text

   usage: ndf [-h] {install,list,remove} ...

   Manage your ENDF6 format nuclear data libraries

   options:
     -h, --help            show this help message and exit

   Commands:
     {install,list,remove}
       install             Download ENDF6 files from the IAEA website
       list                List libraries compatible with NDManager
       remove              Remove one or more installed ENDF6 libraries



Finding Your Favorite Library
+++++++++++++++++++++++++++++
The ``ndf list`` command shows evaluated nuclear data libraries available for
download:

.. code-block::

    $ ndf list
    ----------------------------------------------------  Available libraries  ----------------------------------------------------
    brond22              BROND-2-2            [ ]: BROND-2 USSR evaluated neutron data library, issued in 1992
    brond31              BROND-3.1            [ ]: BROND-3.1 Russian evaluated neutron data library, issued in 2016
    cendl31              CENDL-3.1            [ ]: CENDL-3.1 Chinese evaluated neutron data library, issued in 2009
    cendl32              CENDL-3.2            [✓]: CENDL-3.2 Chinese evaluated neutron data library, issued in 2020
    endfb70              ENDF-B-VII.0         [ ]: ENDF/B-VII.0 U.S. Evaluated Nuclear Data Library, issued in 2006
    endfb71              ENDF-B-VII.1         [ ]: ENDF/B-VII.1 U.S. Evaluated Nuclear Data Library, issued in 2011
    endfb8               ENDF-B-VIII.0        [✓]: ENDF/B-VIII.0 U.S. Evaluated Nuclear Data Library, issued in 2018
    endfb81              ENDF-B-VIII.1        [ ]: ENDF/B-VIII.1 U.S. Evaluated Nuclear Data Library, issued in 2024
    fendl32b             FENDL-3.2b           [ ]: FENDL-3.2b Fusion Evaluated Nuclear Data Library, 2022
    jeff31               JEFF-3.1             [ ]: JEFF-3.1 Evaluated nuclear data library of the OECD Nuclear Energy Agency
    jeff311              JEFF-3.1.1           [ ]: JEFF-3.1 Evaluated nuclear data library of the OECD Nuclear Energy Agency
    jeff312              JEFF-3.1.2           [ ]: JEFF-3.1.2 Evaluated nuclear data library of the OECD Nuclear Energy Agency
    jeff33               JEFF-3.3             [✓]: JEFF-3.3 Evaluated nuclear data library of the OECD Nuclear Energy Agency, 2017
    jendl32              JENDL-3.2            [ ]: JENDL-3.2 Japanese evaluated nuclear data library, 1994
    jendl4               JENDL-4.0            [ ]: JENDL-4.0 Japanese evaluated nuclear data library, 2010
    jendl5               JENDL-5-Aug2023      [ ]: JENDL-5 Japanese evaluated nuclear data library, 2021
    tendl2021            TENDL-2021           [ ]: TENDL-2021 TALYS-based Evaluated Nuclear Data Library, 2021
    tendl2023            TENDL-2023           [✓]: TENDL-2023 TALYS-based Evaluated Nuclear Data Library, 2023
    -----------------------------------------------------  Custom Libraries  ------------------------------------------------------
    bar             foo             jeff4t3


All libraries are shown with a shorthand name, used throughout ``ndmanager``, as well as a
fancy name under which the libraries are stored on IAEA's website.
``ndf list`` also provides a short description of the libraries as well as an indication whether
the libraries are installed on your machine or not.
It will also display any custom library you might have installed manually.

By default, only the most common libraries are displayed, you can provides the `--all` flag to display
all libraries available in the IAEA database.
In total, 71 libraries are available.

Installing a Library
++++++++++++++++++++
The ``ndf install`` allows you to download any of the nuclear data libraries listed by the
``ndf list`` command.
It takes the shortened named of the libraries you want to install as argument.

By default, ``ndf`` will download a restricted number of sublibraries,
shown in the following table:

+------------+----------------------------------------+---------+
| Short name | Description                            | Default |
+============+========================================+=========+
| n          | Incident-Neutron Data                  | Yes     |
+------------+----------------------------------------+---------+
| decay      | Radioactive Decay Data                 | Yes     |
+------------+----------------------------------------+---------+
| nfpy       | Neutron-Induced Fission Product Yields | Yes     |
+------------+----------------------------------------+---------+
| sfpy       | Spontaneous Fission Product Yields     | Yes     |
+------------+----------------------------------------+---------+
| tsl        | Thermal Neutron Scattering Data        | Yes     |
+------------+----------------------------------------+---------+
| ard        | Atomic Relaxation Data                 | Yes     |
+------------+----------------------------------------+---------+
| photo      | Photo-Atomic Interaction Data          | Yes     |
+------------+----------------------------------------+---------+
| g          | Photo-Nuclear Data                     | No      |
+------------+----------------------------------------+---------+
| e          | Electro-Atomic Interaction Data        | No      |
+------------+----------------------------------------+---------+
| p          | Incident-Proton Data                   | No      |
+------------+----------------------------------------+---------+
| d          | Incident-Deuteron Data                 | No      |
+------------+----------------------------------------+---------+
| t          | Incident-Tritium Data                  | No      |
+------------+----------------------------------------+---------+
| he4        | Incident-He4 Data                      | No      |
+------------+----------------------------------------+---------+
| he3        | Incident-He3 Data                      | No      |
+------------+----------------------------------------+---------+

To download all available sublibraries you can pass the ``--all`` or ``-a``
flag to the ``ndf install`` command.
To explicitely download a set of sublibraries, you can pass the ``--sub`` or
``-s`` parameter and the list of sublibraries you wish to download.
Note that the ``--sub`` flag should appear *after* the list of libraries.
Finally, you can pass the ``-j`` flag with an integer to use multiple processes
to download the libraries faster.

.. code-block::

    $ ndf install endfb81 -j 5 --sub photo ard
    ENDF/B-VIII.1/photo      : 100%|████████████████████████████████████████| 100/100 [00:13s]
    ENDF/B-VIII.1/ard        : 100%|████████████████████████████████████████| 100/100 [00:02s]

In addition to downloading nuclear data, the ``ndf install`` command allows you to install a custom
made library stored on your machine for use with NDManager.
For instance if your want to use the `JEFF-4T3 <https://www.oecd-nea.org/dbdata/jeff/jeff40/t4/>`_
library published by the NEA, you can download it from the website and extract the zip archive.

From the resulting directory, simply run:

.. code-block::

  $ ndf install . --name jeff4t3

You can now use the JEFF-4T3 library with NDManager seemlessly.


Removing a Library
++++++++++++++++++

The ``ndf remove`` command allows you to uninstall a library:

.. code-block::

    $ ndf remove endfb81

It removes all installed sublibraries.
