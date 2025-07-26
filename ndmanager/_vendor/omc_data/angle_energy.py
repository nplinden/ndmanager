from abc import ABC, abstractmethod

import ndmanager._vendor.omc_data
from ndmanager._vendor.omc_data.mixin import EqualityMixin


class AngleEnergy(EqualityMixin, ABC):
    """Distribution in angle and energy of a secondary particle."""
    @abstractmethod
    def to_hdf5(self, group):
        pass

    @staticmethod
    def from_hdf5(group):
        """Generate angle-energy distribution from HDF5 data

        Parameters
        ----------
        group : h5py.Group
            HDF5 group to read from

        Returns
        -------
        ndmanager._vendor.omc_data.AngleEnergy
            Angle-energy distribution

        """
        dist_type = group.attrs['type'].decode()
        if dist_type == 'uncorrelated':
            return ndmanager._vendor.omc_data.UncorrelatedAngleEnergy.from_hdf5(group)
        elif dist_type == 'correlated':
            return ndmanager._vendor.omc_data.CorrelatedAngleEnergy.from_hdf5(group)
        elif dist_type == 'kalbach-mann':
            return ndmanager._vendor.omc_data.KalbachMann.from_hdf5(group)
        elif dist_type == 'nbody':
            return ndmanager._vendor.omc_data.NBodyPhaseSpace.from_hdf5(group)
        elif dist_type == 'coherent_elastic':
            return ndmanager._vendor.omc_data.CoherentElasticAE.from_hdf5(group)
        elif dist_type == 'incoherent_elastic':
            return ndmanager._vendor.omc_data.IncoherentElasticAE.from_hdf5(group)
        elif dist_type == 'incoherent_elastic_discrete':
            return ndmanager._vendor.omc_data.IncoherentElasticAEDiscrete.from_hdf5(group)
        elif dist_type == 'incoherent_inelastic_discrete':
            return ndmanager._vendor.omc_data.IncoherentInelasticAEDiscrete.from_hdf5(group)
        elif dist_type == 'incoherent_inelastic':
            return ndmanager._vendor.omc_data.IncoherentInelasticAE.from_hdf5(group)
        elif dist_type == 'mixed_elastic':
            return ndmanager._vendor.omc_data.MixedElasticAE.from_hdf5(group)

    @staticmethod
    def from_ace(ace, location_dist, location_start, rx=None):
        """Generate an angle-energy distribution from ACE data

        Parameters
        ----------
        ace : ndmanager._vendor.omc_data.ace.Table
            ACE table to read from
        location_dist : int
            Index in the XSS array corresponding to the start of a block,
            e.g. JXS(11) for the the DLW block.
        location_start : int
            Index in the XSS array corresponding to the start of an energy
            distribution array
        rx : Reaction
            Reaction this energy distribution will be associated with

        Returns
        -------
        distribution : ndmanager._vendor.omc_data.AngleEnergy
            Secondary angle-energy distribution

        """
        # Set starting index for energy distribution
        idx = location_dist + location_start - 1

        law = int(ace.xss[idx + 1])
        location_data = int(ace.xss[idx + 2])

        # Position index for reading law data
        idx = location_dist + location_data - 1

        # Parse energy distribution data
        if law == 2:
            distribution = ndmanager._vendor.omc_data.UncorrelatedAngleEnergy()
            distribution.energy = ndmanager._vendor.omc_data.DiscretePhoton.from_ace(ace, idx)
        elif law in (3, 33):
            distribution = ndmanager._vendor.omc_data.UncorrelatedAngleEnergy()
            distribution.energy = ndmanager._vendor.omc_data.LevelInelastic.from_ace(ace, idx)
        elif law == 4:
            distribution = ndmanager._vendor.omc_data.UncorrelatedAngleEnergy()
            distribution.energy = ndmanager._vendor.omc_data.ContinuousTabular.from_ace(
                ace, idx, location_dist)
        elif law == 5:
            distribution = ndmanager._vendor.omc_data.UncorrelatedAngleEnergy()
            distribution.energy = ndmanager._vendor.omc_data.GeneralEvaporation.from_ace(ace, idx)
        elif law == 7:
            distribution = ndmanager._vendor.omc_data.UncorrelatedAngleEnergy()
            distribution.energy = ndmanager._vendor.omc_data.MaxwellEnergy.from_ace(ace, idx)
        elif law == 9:
            distribution = ndmanager._vendor.omc_data.UncorrelatedAngleEnergy()
            distribution.energy = ndmanager._vendor.omc_data.Evaporation.from_ace(ace, idx)
        elif law == 11:
            distribution = ndmanager._vendor.omc_data.UncorrelatedAngleEnergy()
            distribution.energy = ndmanager._vendor.omc_data.WattEnergy.from_ace(ace, idx)
        elif law == 44:
            distribution = ndmanager._vendor.omc_data.KalbachMann.from_ace(
                ace, idx, location_dist)
        elif law == 61:
            distribution = ndmanager._vendor.omc_data.CorrelatedAngleEnergy.from_ace(
                ace, idx, location_dist)
        elif law == 66:
            distribution = ndmanager._vendor.omc_data.NBodyPhaseSpace.from_ace(
                ace, idx, rx.q_value)
        else:
            raise ValueError(f"Unsupported ACE secondary energy distribution law {law}")

        return distribution
