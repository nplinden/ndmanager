.. python:

Python API
----------

NDManager provides some python API to interact with your database.

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

You can also access the classes used to interact with the IAEA nuclear data service: ``IAEA``,
 ``IAEALibrary``, and ``IAEASublibrary``.

 The ``IAEA`` acts as a dictionnary that maps library names or aliases to the corresponding
 ``IAEALibrary`` object, which maps sublibrary names (``n`` for neutron data, ``decay`` for
 radioactive decay data, etc.) to an ``IAEASublibrary``, which maps nuclide name to the tape's 
 URL.

 You can initialize the database like so:

 .. code-block::

   In [1]: from ndmanager import IAEA
      ...: iaea = IAEA()

If you have never used the `ndf` command or the `IAEA` class, initialization should take around
a minute.
The database is then cached into the `~/.config/ndmanager/IAEA_cache.json` file and subsequent
initialization should be near instantaneous.
Using the ``IAEA`` is then fairly straightforward

.. code-block::

   In [1]: iaea["endfb8"]["n"]["Pu239"]

Returns the URL of the desired tape (tapes a compressed in a zip file on the website).
To automatically download and extract the tape to an ENDF6 file, use the `download_single`
method:

.. code-block::

   In [1]: iaea["endfb8"]["n"].download_single("Pu239", "./Pu239.endf6")


