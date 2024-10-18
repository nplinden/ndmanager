.. _ndfetcher:

===================
NDFetcher module
===================

The NDFetcher module provides the ``ndf`` command to manage your evaluated nuclear
data files in the ENDF6 format.
The spirit of ``ndf`` is to be used as a kind of package manager for nuclear
data libraries.
The main source of ENDF6 files for NDFetcher is the
`IAEA website <https://www-nds.iaea.org/public/download-endf/>`_, as it stores
most ENDF6 data libraries using a common, easy to parse directory structure.

All data is stored in a directory defined by the ``NDMANAGER_ENDF6`` environment
variable, which you can set in your ``.bashrc`` file or equivalent.

``list``
--------
The ``ndf list`` command shows evaluated nuclear data libraries available for
download:

.. code-block::

    $ ndf list
    ---------------------------------------------------------------  Available libraries  ----------------------------------------------------------------
    jeff33   JEFF-3.3        [✓]: Version 3.3 of the Joint Evaluated Fission and Fusion (JEFF) library distributed by OECD's Nuclear Energy Agency (NEA)
    jeff311  JEFF-3.1.1      [✓]: Version 3.1.1 of the Joint Evaluated Fission and Fusion (JEFF) library distributed by OECD's Nuclear Energy Agency (NEA)
    jendl5   JENDL-5-Aug2023 [ ]: Version 5 of the Japanese Evaluated Nuclear Data Library (JENDL)library distributed by JAEA
    endfb71  ENDF-B-VII.1    [✓]: Version 7.1 of the ENDF-B data library distributed by the NNDC
    endfb8   ENDF-B-VIII.0   [✓]: Version 8.0 of the ENDF-B data library distributed by the NNDC
    tendl19  TENDL-2019      [ ]: 2019 release of the TENDL library distributed by the Paul Scherrer Institute (Switzerland).
    tendl23  TENDL-2023      [ ]: 2023 release of the TENDL library distributed by the Paul Scherrer Institute (Switzerland).
    cendl32  CENDL-3.2       [✓]: Version 3.2 of the Chinese Evaluated Nuclear Data Library (CENDL) distributed by the China Nuclear Data Center.
    cendl31  CENDL-3.1       [✓]: Version 3.1 of the Chinese Evaluated Nuclear Data Library (CENDL) distributed by the China Nuclear Data Center.
    ------------------------------------------------------------------------------------------------------------------------------------------------------

All libraries are shown with a shorthand name, used throughout ``ndmanager``, as well as a
fancy name under which the libraries are stored on IAEA's website.
``ndf list`` also provides a short description of the libraries as well as an indication whether
the libraries are installed on your machine or not.

``info``
--------

The ``ndf info`` command give you more information on any of the installable libraries.
It take one or more library names (in their shortened form) as arguments.

.. code-block::

    $ ndf info jeff33
    ---------------------------------------------------------------------  jeff33  ---------------------------------------------------------------------
    Fancy name:               JEFF-3.3
    Source:                   https://www-nds.iaea.org/public/download-endf/JEFF-3.3
    Homepage:                 https://www.oecd-nea.org/dbforms/data/eva/evatapes/jeff_31/index-JEFF3.1.1.html
    Available Sublibraries:   decay  n  nfpy  sfpy  tsl
    Index:                    1 NSUB=4      Materials:3852  Size:45Mb    Zipped:9Mb                       [DECAY] Radioactive Decay Data
                              2 NSUB=5      Materials:3     Size:372Kb   Zipped:94Kb                      [S/FPY] Spontaneous Fission Product Yields
                              3 NSUB=10     Materials:562   Size:2Gb     Zipped:451Mb    20.MeV-200.MeV   [N]     Incident-Neutron Data
                              4 NSUB=11     Materials:19    Size:5Mb     Zipped:2Mb      1.MeV-14.MeV     [N/FPY] Neutron-Induced Fission Product Yields
                              5 NSUB=12     Materials:20    Size:150Mb   Zipped:37Mb     5.eV-20.MeV      [TSL]   Thermal Neutron Scattering Data

                              Total: Materials:4456  Size:2Gb     Zipped:497Mb
    ---------------------------------------------------------------------------------------------------------------------------------------------------

The ``info`` command shows the source of the data as well as information on which
sublibraries are distributed.

``install``
-----------
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
The ``--sub`` flag should appear *after* the list of libraries:

.. code-block::

    $ ndf install jeff33 endfb8 --sub n tsl photo ard
    ╭────────┬─────┬───────┬─────────┬───────╮
    │        │ n   │ tsl   │ photo   │ ard   │
    ├────────┼─────┼───────┼─────────┼───────┤
    │ jeff33 │ ..  │ ..    │ ✕       │ ✕     │
    │ endfb8 │ ..  │ ..    │ ..      │ ..    │
    ╰────────┴─────┴───────┴─────────┴───────╯

``remove``
----------

The ``ndf remove`` command allows you to uninstall a library:

.. code-block::

    $ ndf remove jeff33 endfb8

It removes all installed sublibraries.

Python API
----------

NDManager provides a very limited (for now) python API to interact
with your database.

.. code-block::

    In [1]: from ndmanager import get_endf6
       ...: get_endf6("endfb71", "n", "Pu239")
    Out[1]: PosixPath('/Users/nlinden/.ndmanager/endf6/endfb71/n/Pu239.endf6')

A typical use for this would be for loading the ENDF6 tape into an OpenMC
``IncidentNeutron`` object:

.. code-block::

      In [1]: from ndmanager import get_endf6
         ...: from openmc.data import IncidentNeutron
         ...: tape = get_endf6("endfb8", "n", "Pu239")
         ...: n = IncidentNeutron.from_endf(tape)



