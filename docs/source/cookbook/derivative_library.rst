.. _derivative_library:

Building a Derivative Library
-----------------------------

Sometimes you may want to investigate the effect of a single nuclide evaluation on a reactor model.
For instance if you work on chloride molten salt, you may be aware that ``Cl35`` :math:`(n,\alpha)` cross-sections are not very well known above 1MeV, and this may have large consequence on the reactor's eigenvalue.
`Tahara <https://www.tandfonline.com/doi/epdf/10.1080/00223131.2023.2282553?needAccess=true>`_ shows some comparison library comparisons for and MCSFR model.

To target ``Cl35`` specifically, you may want to run a calculation using your usual library like ENDF-B/VIII.0, and using a library using ENDF-B/VIII.0 for all nuclide except ``Cl35`` where you might use JENDL-5.0 or whatever you'd prefer.
The first step is to install both libraries:

.. code-block:: console

   $ ndf install endfb8 jendl5

To build library derivative of ENDF-B/VIII.0, you could create an NDOmcer input file to rebuild the entire thing, but this would mean that hundreds of cross-section files would be duplicated with no benefit.
Instead, the smarter way of building the library would be to build only the new Cl35 HDF5 file, and write the ``cross_sections.xml`` file such that all other nuclide point to the ``endfb8`` library.

To do this, you can replace the ``base`` element in NDOmcer's input file with a ``reuse`` element.
This element should be associated with a library name already available to NDOmcer, such as the ``endfb8`` library we created in the first tutorial.

.. code-block:: yaml

    # endfb8-jendl5-cl35.yml
    name: endfb8-jendl5-cl35
    summary: A library based on the ENDF-B/VIII.0 evaluations, with Cl35 from JENDL-5.0.
    description: |
      A library based on the ENDF-B/VIII.0 evaluations, with Cl35 from JENDL-5.0.
    neutron:
      reuse: endfb8
      add:
        jendl5: Cl35
      temperatures: 250 294 600 900 1200 2500
    photon:
      base: endfb8
    tsl:
      base: endfb8

You can now run NDOmcer:

.. code-block:: console

   ndo build endfb8-jendl5-cl35.yml

Looking at the library in your database should look something like this:

.. code-block:: text
   
  $NDMANAGER_HDF5/endfb8-jendl5-cl35
  ├── cross_sections.xml
  ├── input.yml
  ├── neutron
  │   ├── Cl35.h5
  │   └── logs
  │       └── Cl35.log
  ├── photon
  │   └── logs
  └── tsl
      └── logs

With the ``cross_section.xml`` file referencing the ``endfb8`` library for most nuclides.



