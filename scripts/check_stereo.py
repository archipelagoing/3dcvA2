"""Small, independent checks before evaluating the real stereo pair."""
import sys
from pathlib import Path
import numpy as np
sys.path.insert(0, str(Path(__file__).resolve().parents[1] / 'src'))
from stereo import census_transform, hamming_distance, window_sum, match_stereo, bad_pixel_rate

# Row-major neighbors around center 5: 1,2,3,4,6,7,8,9 -> 11110000.
small = np.arange(1, 10, dtype=np.uint8).reshape(3, 3)
descriptor = census_transform(small, 3)
assert descriptor[1, 1] == 240
assert hamming_distance(descriptor, np.zeros_like(descriptor))[1, 1] == 4
assert np.count_nonzero(descriptor) == 1
assert hamming_distance(np.array([[2**48-1]], dtype=np.uint64), np.zeros((1, 1), np.uint64))[0, 0] == 48

rng = np.random.default_rng(532)
values = rng.integers(0, 49, size=(13, 17))
for size in (5, 9):
    actual = window_sum(values, size)
    radius = size // 2
    for y in range(radius, values.shape[0]-radius):
        for x in range(radius, values.shape[1]-radius):
            assert actual[y, x] == values[y-radius:y+radius+1, x-radius:x+radius+1].sum()

# Build the right view so corresponding texture occurs N pixels to the left.
left = rng.integers(0, 256, size=(35, 55), dtype=np.uint8)
shift = 4
right = np.zeros_like(left)
right[:, :-shift] = left[:, shift:]
for census_size in (3, 7):
    radius = census_size // 2
    lc, rc = census_transform(left, census_size), census_transform(right, census_size)
    assert np.all(hamming_distance(lc[radius:-radius, shift+radius:-radius],
                                   rc[radius:-radius, radius:-shift-radius]) == 0)
    for aggregation_size in (5, 9):
        margin = radius + aggregation_size // 2
        same, valid = match_stereo(left, left, census_size, aggregation_size, 8)
        assert np.all(same[valid] == 0)
        found, valid = match_stereo(left, right, census_size, aggregation_size, 8)
        assert np.all(found[margin:-margin, shift+margin:-margin] == shift)
        assert not valid[:margin].any() and not valid[:, :margin].any()
        assert not valid[-margin:].any() and not valid[:, -margin:].any()

# Compare WTA with an independent, slow loop over raw pixel comparisons.
l = rng.integers(0, 256, size=(13, 16), dtype=np.uint8)
r = rng.integers(0, 256, size=l.shape, dtype=np.uint8)
actual, valid = match_stereo(l, r, 3, 3, 3)
for y in range(2, 11):
    for x in range(2, 14):
        costs = []
        for d in range(min(3, x-2)+1):
            cost = 0
            for ay in (-1, 0, 1):
                for ax in (-1, 0, 1):
                    ly, lx, rx = y+ay, x+ax, x+ax-d
                    for dy in (-1, 0, 1):
                        for dx in (-1, 0, 1):
                            if dx or dy:
                                cost += (l[ly+dy, lx+dx] < l[ly, lx]) != (r[ly+dy, rx+dx] < r[ly, rx])
            costs.append(cost)
        assert actual[y, x] == np.argmin(costs)
assert bad_pixel_rate(np.array([[0, 1, 2]]), np.zeros((1, 3)), np.ones((1, 3), bool))['bad_pixels'] == 1
print('PASS: hand-computed census, 48-bit Hamming, integral sums, identical/shifted pairs, borders, brute-force WTA, error threshold')
