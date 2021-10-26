import numpy as np

from hexrd import constants

from hexrd.ui.constants import ViewType


class RotationSeriesSpotOverlay:
    def __init__(self, plane_data, instr,
                 crystal_params=None,
                 eta_ranges=None,
                 ome_ranges=None,
                 ome_period=None,
                 eta_period=np.r_[-180., 180.],
                 aggregated=True):

        # FIXME: eta_period is currently not in use

        self._plane_data = plane_data
        self._instrument = instr
        if crystal_params is None:
            self._crystal_params = np.hstack(
                [constants.zeros_3,
                 constants.zeros_3,
                 constants.identity_6x1]
            )
        else:
            assert len(crystal_params) == 12, \
                "crystal parameters must have length 12"
            self._crystal_params = crystal_params

        if eta_ranges is None:
            self._eta_ranges = [(-np.pi, np.pi), ]
        else:
            assert hasattr(eta_ranges, '__len__'), \
                'eta ranges must be a list of 2-tuples'
            # !!! need better check
            self._eta_ranges = eta_ranges

        if ome_ranges is None:
            self._ome_ranges = [(-np.pi, np.pi), ]
        else:
            assert hasattr(ome_ranges, '__len__'), \
                'ome ranges must be a list of 2-tuples'
            # !!! need better check
            self._ome_ranges = ome_ranges

        if ome_period is None:
            self._ome_period = self._ome_ranges[0][0] + np.r_[0., 2*np.pi]
        else:
            self._ome_period = ome_period

        self.aggregated = aggregated

    @property
    def plane_data(self):
        return self._plane_data

    @property
    def instrument(self):
        return self._instrument

    @property
    def crystal_params(self):
        return self._crystal_params

    @crystal_params.setter
    def crystal_params(self, x):
        assert len(x) == 12, 'input must be array-like with length 12'

    @property
    def eta_ranges(self):
        return self._eta_ranges

    @eta_ranges.setter
    def eta_ranges(self, x):
        # FIXME: need a check here
        self._eta_ranges = x

    @property
    def ome_ranges(self):
        return self._ome_ranges

    @ome_ranges.setter
    def ome_ranges(self, x):
        # FIXME: need a check here
        self._ome_ranges = x

    @property
    def ome_period(self):
        return self._ome_period

    def overlay(self, display_mode=ViewType.raw):
        """
        Returns appropriate point groups for displaying bragg reflection
        locations for a monochromatic rotation series.

        Parameters
        ----------
        display_mode : TYPE, optional
            DESCRIPTION. The default is ViewType.raw.

        Raises
        ------
        NotImplementedError
            TODO: bin omega output as frames; functions exist in
            imageseries.omega

        Returns
        -------
        point_groups : TYPE
            DESCRIPTION.

        """
        sim_data = self.instrument.simulate_rotation_series(
            self.plane_data, [self.crystal_params, ],
            eta_ranges=self.eta_ranges,
            ome_ranges=self.ome_ranges,
            ome_period=self.ome_period
        )
        point_groups = {}
        keys = ['data', 'ranges']
        for det_key, psim in sim_data.items():
            panel = self.instrument.detectors[det_key]
            point_groups[det_key] = {key: [] for key in keys}
            valid_ids, valid_hkls, valid_angs, valid_xys, ang_pixel_size = psim
            angles, omegas = np.hsplit(valid_angs[0], [2])
            if display_mode == ViewType.polar:
                point_groups[det_key]['data'] = np.degrees(angles)
            elif display_mode in [ViewType.raw, ViewType.cartesian]:
                result = valid_xys[0]
                if display_mode == ViewType.raw:
                    # If raw, convert to pixels
                    result[:] = panel.cartToPixel(result)
                    result[:, [0, 1]] = result[:, [1, 0]]
                point_groups[det_key]['data'] = result

        return point_groups
