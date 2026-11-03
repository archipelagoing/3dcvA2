"""Check calibration resizing, rectification, disparity sign, and grayscale weights."""
import sys
from pathlib import Path
import numpy as np

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / 'src'))
from pointcloud_renderer import scale_intrinsics
from run_fish import grayscale, project

K = np.array([[200., 0, 100], [0, 220., 80], [0, 0, 1]])
original = K.copy()
points = np.array([[0., 0.2, -0.3], [0., 0.1, 0.2], [2., 4., 8.]])
for scale in (0.5, 0.25):
    scaled = scale_intrinsics(K, scale)
    assert np.allclose(project(points, scaled, [0, 0, 0]), scale * project(points, K, [0, 0, 0]))
    assert np.array_equal(scaled[2], [0, 0, 1])
    assert np.allclose(np.array([200, 160]) * scale / [scaled[0, 0], scaled[1, 1]],
                       np.array([200, 160]) / [K[0, 0], K[1, 1]])
assert np.array_equal(K, original)
left = project(points, K, [0, 0, 0])
right = project(points, K, [-0.12, 0, 0])
assert np.array_equal(left[1], right[1])
assert np.allclose(left[0] - right[0], K[0, 0] * 0.12 / points[2])
assert np.all(left[0] > right[0])
colors = np.array([[[100, 0, 0], [0, 100, 0], [0, 0, 100]]], np.uint8)
assert np.array_equal(grayscale(colors), [[30, 59, 11]])
for bad_scale in (0, -1, float('nan')):
    try:
        scale_intrinsics(K, bad_scale)
    except ValueError:
        pass
    else:
        raise AssertionError('Invalid scale was accepted')
print('PASS: scaled projections, field of view, unchanged K, rectification, disparity sign, RGB weights, invalid scales')
