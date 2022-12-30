import numpy as np

from skimage.draw import polygon

from hexrd.ui.create_hedm_instrument import create_hedm_instrument
from hexrd.ui.calibration.polarview import PolarView
from hexrd.ui.hexrd_config import HexrdConfig
from hexrd.ui.utils import add_sample_points
from hexrd.ui.utils.conversions import pixels_to_angles


def convert_raw_to_polar(det, line):
    # Make sure there at least 50 sample points so that the conversion
    # looks correct.
    line = add_sample_points(line, 50)

    instr = create_hedm_instrument()
    kwargs = {
        'ij': line,
        'panel': instr.detectors[det],
        'eta_period': HexrdConfig().polar_res_eta_period,
        'tvec_s': instr.tvec,
    }

    return [pixels_to_angles(**kwargs)]


def create_polar_mask(name, line_data):
    # Calculate current image dimensions
    pv = PolarView(None)
    shape = pv.shape
    # Generate masks from line data
    final_mask = np.ones(shape, dtype=bool)
    for line in line_data:
        tth = np.asarray([point[0] for point in line])
        eta = np.asarray([point[1] for point in line])

        j_col = np.floor((tth - np.degrees(pv.tth_min)) / pv.tth_pixel_size)
        i_row = np.floor((eta - np.degrees(pv.eta_min)) / pv.eta_pixel_size)

        rr, cc = polygon(i_row, j_col, shape=shape)
        mask = np.ones(shape, dtype=bool)
        mask[rr, cc] = False
        final_mask = np.logical_and(final_mask, mask)
    HexrdConfig().masks[name] = final_mask


def rebuild_polar_masks():
    HexrdConfig().masks.clear()
    for name, value in HexrdConfig().raw_mask_coords.items():
        line_data = []
        for det, data in value:
            line_data.extend(convert_raw_to_polar(det, data))
        create_polar_mask(name, line_data)
