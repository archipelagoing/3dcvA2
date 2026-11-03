"""Check CPU projection and render the real HW1 scene at its original resolution."""
import pickle
import sys
import time
from pathlib import Path

import cv2
import numpy as np

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / 'src'))
from pointcloud_renderer import render_pointcloud

# Exercise occlusion, behind-camera rejection, out-of-frame rejection and RGB order.
points = np.array([[0, 0, 0, 100], [0, 0, 0, 0], [2, 1, -1, 1],
                   [0, 1, 0, 0], [1, 0, 0, 0], [0, 0, 1, 1]], dtype=float)
K = np.array([[10., 0, 2], [0, 10., 2], [0, 0, 1]])
image, depth = render_pointcloud(points, K, np.eye(3), np.zeros(3), 5, 5)
assert np.array_equal(image[2, 2], [255, 0, 0]) and depth[2, 2] == 1
assert np.isfinite(depth).sum() == 1
shifted, shifted_depth = render_pointcloud(points[:, :2], K, np.eye(3), [-0.1, 0, 0], 5, 5)
assert shifted_depth[2, 1] == 1 and np.array_equal(shifted[2, 1], [255, 0, 0])

start = time.perf_counter()
with open('data/data.obj', 'rb') as file:
    scene = pickle.load(file, encoding='latin1')
_, _, height, width = scene[0].flatten()
points = np.hstack((scene[4], scene[3]))
image, depth = render_pointcloud(points, scene[2], np.eye(3), np.zeros(3), int(height), int(width))
assert image.shape == (2048, 3072, 3)
assert np.isfinite(depth).sum() > height * width * 0.1
Path('output').mkdir(exist_ok=True)
path = Path('output/fish_setup_check.png')
assert cv2.imwrite(str(path), cv2.cvtColor(image, cv2.COLOR_RGB2BGR))
saved = cv2.imread(str(path))
assert np.array_equal(cv2.cvtColor(saved, cv2.COLOR_BGR2RGB), image)
print(f'PASS: synthetic geometry and RGB checks; {np.isfinite(depth).sum():,} occupied pixels')
print(f'PASS: real scene {width} x {height}, saved and read back {path}; {time.perf_counter()-start:.2f}s')
