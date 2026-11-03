"""Generate Teddy census images, disparity maps, masks, and measured error rates."""
import json
import time
from pathlib import Path
import cv2
import numpy as np

from stereo import census_transform, census_visualization, match_stereo, bad_pixel_rate


def read_gray(path):
    image = cv2.imread(str(path), cv2.IMREAD_GRAYSCALE)
    if image is None:
        raise FileNotFoundError(path)
    return image


def save_image(path, image):
    if not cv2.imwrite(str(path), image):
        raise OSError(f'Could not save {path}')


def main():
    output = Path('results')
    output.mkdir(parents=True, exist_ok=True)
    left = read_gray('data/teddyL.pgm')
    right = read_gray('data/teddyR.pgm')
    stored_truth = read_gray('data/disp2.pgm')
    # Explicit half-up rounding rather than NumPy's ties-to-even convention.
    ground_truth = np.floor(stored_truth.astype(float) / 4 + 0.5)
    known_truth = stored_truth > 0
    # Shared interior: every disparity 0..63 has complete neighborhoods for all
    # four settings. This makes the comparison use identical pixels.
    common_mask = np.zeros(left.shape, dtype=bool)
    common_mask[7:-7, 63+7:-7] = True
    common_mask &= known_truth
    results = []
    for census_size in (3, 7):
        for name, image in (('left', left), ('right', right)):
            descriptor = census_transform(image, census_size)
            save_image(output / f'teddy_census_{name}_wc{census_size}.png', census_visualization(descriptor, census_size))
        for aggregation_size in (5, 9):
            start = time.perf_counter()
            disparity, valid = match_stereo(left, right, census_size, aggregation_size)
            stem = f'wc{census_size}_wa{aggregation_size}'
            save_image(output / f'teddy_disparity_{stem}.png', disparity.astype(np.uint8))
            save_image(output / f'teddy_disparity_view_{stem}.png', np.rint(disparity * (255.0 / 63)).astype(np.uint8))
            result = {'census_size': census_size, 'aggregation_size': aggregation_size,
                      'common_interior': bad_pixel_rate(disparity, ground_truth, common_mask),
                      'valid_known_truth': bad_pixel_rate(disparity, ground_truth, valid & known_truth),
                      'full_image_including_invalid': bad_pixel_rate(disparity, ground_truth, np.ones(left.shape, bool)),
                      'seconds': round(time.perf_counter() - start, 3)}
            results.append(result)
            print(json.dumps(result), flush=True)
    (output / 'teddy_metrics.json').write_text(json.dumps({'results': results}, indent=2) + '\n')


if __name__ == '__main__':
    main()
