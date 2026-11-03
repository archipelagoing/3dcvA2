"""Inspect the supplied stereo inputs and trusted HW1 pickle; no stereo is computed."""
import pickle
import zipfile
from pathlib import Path
import cv2
import numpy as np

images = {}
with zipfile.ZipFile('teddy 2.zip') as archive:
    for name in ('teddyL', 'teddyR', 'disp2'):
        path = Path('teddy') / f'{name}.pgm'
        image = cv2.imread(str(path), cv2.IMREAD_UNCHANGED)
        assert image is not None and image.shape == (375, 450) and image.dtype == np.uint8
        assert path.read_bytes() == archive.read(str(path))
        images[name] = image
        print(f'{path}: {image.shape}, {image.dtype}, range {image.min()}..{image.max()}, matches ZIP')

# Small patch checks support the expected ordering; these are not stereo evaluation.
for x, y in ((200, 150), (300, 200), (150, 250)):
    template = images['teddyL'][y-4:y+5, x-4:x+5]
    strip = images['teddyR'][y-4:y+5, x-70:x+5]
    costs = cv2.matchTemplate(strip, template, cv2.TM_SQDIFF_NORMED)[0]
    right_center = x - 70 + int(costs.argmin()) + 4
    print(f'Patch ({x}, {y}): disparity {x-right_center}, ground truth {images["disp2"][y,x]/4:.2f}')

with Path('data/data.obj').open('rb') as file:
    scene = pickle.load(file, encoding='latin1')
assert len(scene) == 5
for i, value in enumerate(scene):
    value = np.asarray(value)
    print(f'Scene entry {i}: shape {value.shape}, dtype {value.dtype}')
    if i < 3:
        print(value)
    else:
        assert value.shape[0] == 6 and np.isfinite(value).all()
        assert value[3:].min() >= 0 and value[3:].max() <= 1
        print('XYZ minima:', value[:3].min(axis=1), 'maxima:', value[:3].max(axis=1))
        print('RGB range:', value[3:].min(), value[3:].max())
print('PASS: inputs inspected; physical scene units remain unconfirmed')
