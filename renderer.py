"""CPU pinhole projection adapted from HW1's PointCloud2Image approach.

Coordinates use zero-based image pixels. Poses map world to camera: Xc = R X + t.
Unlike the original overwrite-by-input-order loop, collisions use nearest depth.
No maximum filter, interpolation, or hole filling is applied.
"""
import numpy as np


def render_pointcloud(points, K, R, t, height, width):
    """Return an RGB uint8 image and depth buffer (inf where no point projects).

    points has shape (6, N): XYZ followed by RGB in [0, 1]. Camera translation
    and cloud coordinates must share units; K uses pixels.
    """
    camera = np.asarray(R) @ points[:3] + np.asarray(t).reshape(3, 1)
    projected = np.asarray(K) @ camera
    valid = np.isfinite(projected).all(axis=0) & (camera[2] > 0)
    indices = np.flatnonzero(valid)
    uv = np.rint(projected[:2, valid] / projected[2, valid]).astype(np.int64)
    inside = (uv[0] >= 0) & (uv[0] < width) & (uv[1] >= 0) & (uv[1] < height)
    indices, uv = indices[inside], uv[:, inside]
    pixel = uv[1] * width + uv[0]
    depth = np.full(height * width, np.inf)
    np.minimum.at(depth, pixel, camera[2, indices])
    nearest = camera[2, indices] == depth[pixel]
    image = np.zeros((height * width, 3), dtype=np.uint8)
    image[pixel[nearest]] = np.rint(np.clip(points[3:, indices[nearest]].T, 0, 1) * 255).astype(np.uint8)
    return image.reshape(height, width, 3), depth.reshape(height, width)


def scale_intrinsics(K, scale=1.0):
    """Scale focal lengths and principal point with the image dimensions."""
    if not np.isfinite(scale) or scale <= 0:
        raise ValueError('Scale must be positive and finite')
    scaled = np.asarray(K, dtype=float).copy()
    scaled[:2] *= scale
    return scaled
