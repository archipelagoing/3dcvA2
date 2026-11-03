"""Render a rectified fish pair and run the unfiltered homework stereo method."""
import argparse
import json
import pickle
import sys
import time
from pathlib import Path

import cv2
import numpy as np

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / 'src'))
from pointcloud_renderer import render_pointcloud, scale_intrinsics
from stereo import match_stereo, bad_pixel_rate
from run_teddy import save_image


def grayscale(rgb):
    # The homework specifies these weights instead of OpenCV's default conversion.
    weights = np.array([0.30, 0.59, 0.11])
    return np.rint(rgb @ weights).astype(np.uint8)


def project(points, K, translation):
    """Project points with parallel camera axes (R is the identity)."""
    camera_points = points + np.asarray(translation).reshape(3, 1)
    pixels = K @ camera_points
    return pixels[:2] / pixels[2]


def render_views(points, K, baseline, height, width, output):
    """Save both camera views and return their grayscale images and depths."""
    views = []
    depths = []
    for name, translation in (('left', np.zeros(3)), ('right', np.array([-baseline, 0, 0]))):
        rgb, depth = render_pointcloud(points, K, np.eye(3), translation, height, width)
        save_image(output / f'{name}_rgb.png', cv2.cvtColor(rgb, cv2.COLOR_RGB2BGR))
        saved_bgr = cv2.imread(str(output / f'{name}_rgb.png'))
        saved_rgb = cv2.cvtColor(saved_bgr, cv2.COLOR_BGR2RGB)
        assert np.array_equal(saved_rgb, rgb)
        gray = grayscale(rgb)
        save_image(output / f'{name}_gray.png', gray)
        save_image(output / f'{name}_render_mask.png', np.isfinite(depth).astype(np.uint8) * 255)
        views.append(gray)
        depths.append(depth)
    return views, depths


def reference_from_depth(left_depth, right_depth, focal_length, baseline, search_max):
    """Build a diagnostic reference and a mask of points visible in both views."""
    height, width = left_depth.shape
    # Geometry-derived reference, not an independent captured ground-truth image.
    reference = np.zeros((height, width), dtype=float)
    rendered = np.isfinite(left_depth)
    reference[rendered] = focal_length * baseline / left_depth[rendered]
    rows, columns = np.indices((height, width))
    right_columns = np.rint(columns - reference).astype(int)
    inside = (right_columns >= 0) & (right_columns < width)
    safe_x = np.clip(right_columns, 0, width - 1)
    # Conservative mutual visibility check: right depth within 1% of left depth.
    visible = rendered & inside & np.isfinite(right_depth[rows, safe_x])
    depth_agrees = np.zeros((height, width), bool)
    matching_depths = right_depth[rows, safe_x][visible]
    depth_difference = np.abs(matching_depths - left_depth[visible])
    depth_agrees[visible] = depth_difference <= 0.01 * left_depth[visible]
    visible &= depth_agrees
    # Seven pixels cover the largest census and aggregation radii combined.
    evaluation_mask = np.zeros((height, width), bool)
    evaluation_mask[7:-7, search_max + 7:-7] = True
    evaluation_mask &= visible
    return reference, evaluation_mask


def run_matching(left, right, reference, evaluation_mask, search_max, output):
    """Save each of the four homework configurations and its diagnostic score."""
    experiments = []
    for census_size, aggregation_size in ((3, 5), (3, 9), (7, 5), (7, 9)):
        disparity, valid = match_stereo(left, right, census_size, aggregation_size, search_max)
        stem = f'wc{census_size}_wa{aggregation_size}'
        save_image(output / f'disparity_{stem}.png', disparity)
        display = np.rint(disparity * (255.0 / search_max)).astype(np.uint8)
        save_image(output / f'disparity_view_{stem}.png', display)
        save_image(output / f'valid_{stem}.png', valid.astype(np.uint8) * 255)
        result = {
            'census_size': census_size,
            'aggregation_size': aggregation_size,
            'geometry_reference': bad_pixel_rate(disparity, reference, evaluation_mask),
        }
        experiments.append(result)
        print(json.dumps(result), flush=True)
    return experiments


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--scale', type=float, default=0.5,
                        help='0.5 gives quarter total pixels; use 0.25 for quarter width/height')
    parser.add_argument('--baseline', type=float, default=0.12, help='Camera separation in scene units')
    args = parser.parse_args()
    if not np.isfinite(args.baseline) or args.baseline <= 0:
        parser.error('Baseline must be positive and finite')
    start = time.perf_counter()
    with open('data/data.obj', 'rb') as file:
        scene = pickle.load(file, encoding='latin1')
    _, _, original_height, original_width = scene[0].flatten()
    height, width = int(original_height * args.scale), int(original_width * args.scale)
    K = scale_intrinsics(scene[2], args.scale)
    # Require exact resizing so K and image boundaries scale by the same factor.
    if (height < 20 or width < 20 or height != original_height * args.scale
            or width != original_width * args.scale):
        parser.error('Scale must produce integer dimensions of at least 20 pixels')
    assert np.allclose(width / K[0, 0], original_width / scene[2][0, 0])
    assert np.allclose(height / K[1, 1], original_height / scene[2][1, 1])
    assert np.allclose(K[:2, 2] / [width, height], scene[2][:2, 2] / [original_width, original_height])
    points = np.hstack((scene[4], scene[3]))
    z_min, z_max = float(points[2].min()), float(points[2].max())
    # Left camera center is (0,0,0); right is (B,0,0). World-to-camera t=-C.
    left_t, right_t = np.zeros(3), np.array([-args.baseline, 0, 0])
    sample = points[:3, ::1000]
    left_uv = project(sample, K, left_t)
    right_uv = project(sample, K, right_t)
    vertical_error = float(np.max(np.abs(left_uv[1] - right_uv[1])))
    assert vertical_error < 1e-10
    assert np.allclose(left_uv[0] - right_uv[0], K[0, 0] * args.baseline / sample[2])
    disparity_min = K[0, 0] * args.baseline / z_max
    disparity_max = K[0, 0] * args.baseline / z_min
    # Include one extra pixel above the geometric maximum for rounding.
    search_max = int(np.ceil(disparity_max)) + 1
    if search_max >= width - 14:
        parser.error('Baseline is too large for this image width')
    output = Path('output/fish') / f'scale_{args.scale:g}_baseline_{args.baseline:g}'
    output.mkdir(parents=True, exist_ok=True)
    views, depths = render_views(points, K, args.baseline, height, width, output)
    reference, common = reference_from_depth(depths[0], depths[1], K[0, 0], args.baseline, search_max)
    np.save(output / 'reference_disparity.npy', reference)
    np.save(output / 'left_depth.npy', depths[0])
    save_image(output / 'evaluation_mask.png', common.astype(np.uint8) * 255)
    experiments = run_matching(*views, reference, common, search_max, output)
    report = {
        'scale': args.scale,
        'width': width,
        'height': height,
        'K': K.tolist(),
        'baseline_scene_units': args.baseline,
        'left_translation': left_t.tolist(),
        'right_translation': right_t.tolist(),
        'rotation': np.eye(3).tolist(),
        'scene_depth_range': [z_min, z_max],
        'geometric_disparity_range': [disparity_min, disparity_max],
        'search_range': [0, search_max],
        'search_minimum_depth': K[0, 0] * args.baseline / search_max,
        'max_vertical_projection_error': vertical_error,
        'rendered_pixels': [int(np.isfinite(depth).sum()) for depth in depths],
        'results': experiments,
        'seconds': time.perf_counter() - start,
    }
    (output / 'metrics.json').write_text(json.dumps(report, indent=2) + '\n')
    print(f'Saved {output}; total {report["seconds"]:.2f}s', flush=True)


if __name__ == '__main__':
    main()
