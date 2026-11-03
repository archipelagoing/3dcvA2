"""Small checks for matching, camera geometry, and the bonus."""
import numpy as np
from stereo import census_transform, hamming_distance, window_sum, match_stereo, bad_pixel_rate
from renderer import scale_intrinsics
from fish import grayscale, project
from planes import plane_from_three, ransac_plane, look_at, plane_homography, warp_bilinear
from improve_teddy import check_refinements

def check_stereo():
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


def check_geometry():
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


def check_planes():
    rng = np.random.default_rng(42)
    xz = rng.uniform(-2, 2, (300, 2))
    clean = np.column_stack((xz[:, 0], np.full(300, 1.5), xz[:, 1]+5))
    assert plane_from_three(np.array([[0,0,0],[1,1,1],[2,2,2]])) is None
    plane = plane_from_three(clean[:3])
    assert np.allclose(clean @ plane[:3]+plane[3], 0)
    noisy = clean + rng.normal(0, 0.001, clean.shape)
    outliers = rng.uniform(-4, 4, (100,3))
    fit, _ = ransac_plane(np.vstack((noisy, outliers)), rng, threshold=0.01)
    assert abs(fit[1]) > 0.999 and abs(fit[3]-1.5) < 0.01
    assert (np.abs(noisy @ fit[:3]+fit[3]) < 0.01).all()
    K = np.array([[200.,0,100],[0,200.,80],[0,0,1]])
    center = np.array([0.,-3.,5.])
    R = look_at(center,np.array([0.,1.5,5.]))
    t = -R @ center
    H = plane_homography(K,K,R,t,plane)
    source = K @ clean.T
    expected = K @ (R @ clean.T+t[:,None])
    actual = H @ source
    assert np.allclose(actual[:2]/actual[2],expected[:2]/expected[2])
    assert np.allclose(H,plane_homography(K,K,R,t,-plane))
    assert np.allclose(R @ R.T,np.eye(3)) and np.isclose(np.linalg.det(R),1)
    image = rng.integers(0,256,(10,12,3),dtype=np.uint8)
    warped,valid = warp_bilinear(image,np.eye(3),10,12)
    assert np.array_equal(warped[valid],image[valid])
    translation = np.array([[1.,0,1],[0,1,0],[0,0,1]])
    warped,valid = warp_bilinear(image,translation,10,12)
    assert np.array_equal(warped[:-1,1:],image[:-1,:-1])
    assert not valid[:,0].any()
    # Half-pixel interpolation of a simple ramp gives its midpoint.
    ramp=np.tile(np.arange(5,dtype=np.uint8)[None,:,None]*20,(5,1,3))
    shift=np.array([[1.,0,0.5],[0,1,0],[0,0,1]])
    warped,valid=warp_bilinear(ramp,shift,5,5)
    assert np.array_equal(warped[1,1], [10,10,10])
    print('PASS: exact/noisy planes, outlier rejection, collinear samples, camera rotation, homography projection/sign, identity/translated/bilinear warps')


if __name__ == '__main__':
    check_stereo()
    check_geometry()
    check_planes()
    check_refinements()
