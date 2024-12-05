.. _fine_tuning:

Fine Tuning an HDF5 Library
===========================

Now let's build a more complicated library to display some of the capabilities of NDManager.
We'll want to create a library based on the JEFF-3.3 evaluation.
Since JEFF-3.3 does not publish photon evaluations, we'll use the ones from ENDF-B/VIII.0 instead.
Finally we'll make a few tweak to the library:

* To correctly simulate carbon inventory, we'll replace JEFF-3.3 natural ``C0`` nuclide with ``C12`` and ``C13`` from ENDF-B/VIII.0
* The JEFF-3.3 evaluation of ``O17`` is faulty, let's use the one from ENDF-B/VIII.0 instead
* OpenMC wrongly defines natural Ta as containing Ta180 instead of Ta180M because ENDF-B/VIII.0 has no Ta180M evaluation. Since JEFF-3.3 has no Ta180, materials containing Ta will crash simulations. Let's add the ENDF-B tape to the mix.

Since we replaced natural carbon, TSL to incident neutron data mapping must be changed accordingly.

.. code-block:: yaml

    # jeff33.yml
    name: jeff33
    summary: A library based on the JEFF-3.3 evaluations.
    description: |
      A tweaked JEFF-3.3 library
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
