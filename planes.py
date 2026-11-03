"""Plane fitting and camera geometry for the homework bonus."""
import numpy as np


def plane_from_three(points):
    """Fit n.X + d = 0 from three points using their homogeneous null space."""
    rows = np.column_stack((points, np.ones(3)))
    if np.linalg.matrix_rank(rows[:, :3] - rows[0, :3]) < 2:
        return None
    _, _, vectors = np.linalg.svd(rows)
    plane = vectors[-1]
    plane /= np.linalg.norm(plane[:3])
    return plane if plane[3] >= 0 else -plane


def fit_plane(points):
    """Least-squares refinement: the smallest covariance eigenvector is normal."""
    center = points.mean(axis=0)
    centered = points - center
    _, vectors = np.linalg.eigh(centered.T @ centered)
    normal = vectors[:, 0]
    plane = np.r_[normal, -normal @ center]
    return plane if plane[3] >= 0 else -plane


def ransac_plane(points, rng, threshold=0.025, max_trials=2000, confidence=0.999):
    """Score random three-point planes, then refine the best consensus twice.

    points is a sampled N x 3 cloud. Distances are in scene units because n is unit length.
    """
    best_count = 0
    best_plane = None
    budget = max_trials
    trials = 0
    while trials < budget:
        plane = plane_from_three(points[rng.choice(len(points), 3, replace=False)])
        trials += 1
        if plane is None:
            continue
        distances = np.abs(points @ plane[:3] + plane[3])
        inliers = distances < threshold
        count = int(inliers.sum())
        if count <= best_count:
            continue
        best_count, best_plane = count, plane
        ratio = count / len(points)
        if ratio == 1:
            budget = trials
        elif ratio > 0:
            required = int(np.ceil(np.log(1-confidence) / np.log1p(-ratio**3)))
            budget = min(budget, max(100, required))
    if best_plane is None or best_count < 3:
        raise RuntimeError('RANSAC did not find a usable plane')
    for _ in range(2):
        inliers = np.abs(points @ best_plane[:3] + best_plane[3]) < threshold
        best_plane = fit_plane(points[inliers])
    return best_plane, trials


def look_at(center, target, right_hint=np.array([1., 0, 0])):
    """World-to-camera rotation with x right, y down, and positive z forward."""
    forward = target - center
    forward /= np.linalg.norm(forward)
    right = right_hint - (right_hint @ forward) * forward
    right /= np.linalg.norm(right)
    down = np.cross(forward, right)
    return np.vstack((right, down, forward))


def plane_homography(K_a, K_b, R_b, t_b, plane):
    """Map image A to B; A is the world origin with R_a=I and t_a=0.

    For n.X+d=0, X_B=(R_b - t_b n.T/d) X_A on the plane.
    """
    if abs(plane[3]) < 1e-10:
        raise ValueError('Reference camera lies on the plane')
    return K_b @ (R_b - np.outer(t_b, plane[:3]) / plane[3]) @ np.linalg.inv(K_a)


def warp_bilinear(image, H, height, width):
    """Inverse-map each destination pixel and interpolate its four source neighbors."""
    y, x = np.indices((height, width))
    source = np.linalg.inv(H) @ np.vstack((x.ravel(), y.ravel(), np.ones(x.size)))
    finite = np.abs(source[2]) > 1e-12
    coordinates = np.zeros((2, x.size))
    coordinates[:, finite] = source[:2, finite] / source[2, finite]
    sx, sy = coordinates
    x0, y0 = np.floor(sx).astype(int), np.floor(sy).astype(int)
    valid = finite & (x0 >= 0) & (y0 >= 0) & (x0+1 < image.shape[1]) & (y0+1 < image.shape[0])
    x0, y0 = x0[valid], y0[valid]
    dx, dy = (sx[valid]-x0)[:, None], (sy[valid]-y0)[:, None]
    colors = ((1-dx)*(1-dy)*image[y0, x0] + dx*(1-dy)*image[y0, x0+1]
              + dx*dy*image[y0+1, x0+1] + (1-dx)*dy*image[y0+1, x0])
    output = np.zeros((x.size, 3), dtype=np.uint8)
    output[valid] = np.rint(colors).clip(0, 255).astype(np.uint8)
    return output.reshape(height, width, 3), valid.reshape(height, width)
