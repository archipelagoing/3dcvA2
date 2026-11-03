"""Run the best Teddy refinement; keep the other attempts below as comments."""
import json
from pathlib import Path

import numpy as np
# Attempt 1 used this import:
# from scipy.ndimage import median_filter

from stereo import match_stereo, bad_pixel_rate
# Attempt 3 also needs these helpers:
# from stereo import census_transform, hamming_distance, window_sum
from teddy import read_gray, save_image


def fill_rejected(disparity, trusted, valid):
    """Fill rejected points with the smaller nearest trusted disparity in that row.

    Smaller disparity favors background at occlusions. At an end, use the only
    available neighbor. Rows with no trusted samples retain the baseline. Never
    fill the original invalid border. No ground truth is used here.
    """
    filled = disparity.copy()
    for y in range(disparity.shape[0]):
        anchors = np.flatnonzero(trusted[y])
        missing = np.flatnonzero(valid[y] & ~trusted[y])
        if not anchors.size or not missing.size:
            continue
        positions = np.searchsorted(anchors, missing)
        before = anchors[np.maximum(positions - 1, 0)]
        after = anchors[np.minimum(positions, len(anchors) - 1)]
        filled[y, missing] = np.minimum(disparity[y, before], disparity[y, after])
    return filled


# Attempt 3: uniqueness filtering. It helped, but left/right checking did better.
# def unique_matches(left, right, disparity, valid):
#     """Require the best cost to beat alternatives outside +/-1 disparity by 10%."""
#     lc, rc = census_transform(left, 7), census_transform(right, 7)
#     best = np.full(left.shape, np.inf)
#     alternative = np.full(left.shape, np.inf)
#     height, width = left.shape
#     for shift in range(64):
#         if shift + 7 >= width - 7:
#             break
#         cost = np.zeros(left.shape, dtype=np.int32)
#         cost[:, shift:] = hamming_distance(lc[:, shift:], rc[:, :width-shift])
#         total = window_sum(cost, 9)
#         candidate = np.zeros(left.shape, dtype=bool)
#         candidate[7:height-7, shift+7:width-7] = True
#         chosen = candidate & (disparity == shift)
#         best[chosen] = total[chosen]
#         competitor = candidate & (np.abs(disparity.astype(int) - shift) > 1)
#         alternative[competitor] = np.minimum(alternative[competitor], total[competitor])
#     return valid & (alternative > 1.10 * best)


def consistency_mask(disparity, valid, reverse, reverse_valid):
    y, x = np.indices(disparity.shape)
    xr = x - disparity.astype(int)
    inside = (xr >= 0) & (xr < disparity.shape[1])
    xr = np.clip(xr, 0, disparity.shape[1]-1)
    return (valid & inside & reverse_valid[y, xr]
            & (np.abs(disparity.astype(int) - reverse[y, xr].astype(int)) <= 1))


def check_refinements():
    disparity = np.array([[0, 10, 50, 50, 4, 0]], dtype=np.uint16)
    valid = np.array([[False, True, True, True, True, False]])
    trusted = np.array([[False, True, False, False, True, False]])
    assert np.array_equal(fill_rejected(disparity, trusted, valid), [[0, 10, 4, 4, 4, 0]])
    assert np.array_equal(fill_rejected(disparity, np.zeros_like(valid), valid), disparity)
    d = np.full((1, 8), 2, dtype=np.uint16)
    mask = consistency_mask(d, np.ones_like(d, bool), d, np.ones_like(d, bool))
    assert np.array_equal(mask, [[False, False, True, True, True, True, True, True]])
    mask = consistency_mask(d, np.ones_like(d, bool), np.zeros_like(d), np.ones_like(d, bool))
    assert not mask.any()
    rng = np.random.default_rng(532)
    left = rng.integers(0, 256, (35, 55), dtype=np.uint8)
    right = np.zeros_like(left)
    right[:, :-4] = left[:, 4:]
    forward, forward_valid = match_stereo(left, right, 7, 9, 8)
    reverse, reverse_valid = match_stereo(np.fliplr(right), np.fliplr(left), 7, 9, 8)
    trusted = consistency_mask(forward, forward_valid, np.fliplr(reverse), np.fliplr(reverse_valid))
    assert trusted[7:-7, 11:-11].all()
    # Checks retained with the uniqueness attempt:
    # unique = unique_matches(left, right, forward, forward_valid)
    # assert unique[7:-7, 11:-11].all()
    print('PASS: filling, empty rows, consistency direction/threshold, shifted-pair reverse matching')


def main():
    check_refinements()
    output = Path('results')
    output.mkdir(parents=True, exist_ok=True)
    left, right = read_gray('data/teddyL.pgm'), read_gray('data/teddyR.pgm')
    baseline, valid = match_stereo(left, right, 7, 9)
    # Mirror both views to reuse the same matcher for right-to-left search.
    reverse, reverse_valid = match_stereo(np.fliplr(right), np.fliplr(left), 7, 9)
    reverse, reverse_valid = np.fliplr(reverse), np.fliplr(reverse_valid)
    consistent = consistency_mask(baseline, valid, reverse, reverse_valid)
    # Attempt 1: a median filter only made a small difference (11.45% interior error).
    # median = median_filter(baseline, size=3, mode='nearest')
    # median[~valid] = 0
    # prediction = median
    # trusted = valid
    # name = 'median_3x3'

    # Attempt 3: uniqueness plus filling reached 10.16% interior error.
    # unique = unique_matches(left, right, baseline, valid)
    # prediction = fill_rejected(baseline, unique, valid)
    # trusted = unique
    # name = 'uniqueness_then_fill'

    # Attempt 2 worked best: check both directions, then fill rejected matches.
    prediction = fill_rejected(baseline, consistent, valid)
    trusted = consistent
    name = 'left_right_then_fill'
    # Load truth only after all predictions have been made. Parameters are fixed.
    truth_file = read_gray('data/disp2.pgm')
    truth = np.floor(truth_file.astype(float) / 4 + 0.5)
    common = np.zeros(left.shape, bool)
    common[7:-7, 70:-7] = True
    common &= truth_file > 0
    assert np.all(prediction[~valid] == 0)
    save_image(output / 'teddy_refined_raw.png', prediction.astype(np.uint8))
    save_image(output / 'teddy_refined.png', np.rint(prediction * (255.0/63)).astype(np.uint8))
    result = {
        'method': name,
        'common_interior': bad_pixel_rate(prediction, truth, common),
        'valid_known_truth': bad_pixel_rate(prediction, truth, valid & (truth_file > 0)),
        'full_image_including_invalid': bad_pixel_rate(prediction, truth, np.ones(left.shape, bool)),
        'trusted_common_percent': float(100 * (trusted & common).sum() / common.sum()),
    }
    print(json.dumps(result), flush=True)
    # Keep the required unfiltered results separate.
    (output / 'teddy_refined_metrics.json').write_text(json.dumps(result, indent=2) + '\n')



if __name__ == '__main__':
    main()
