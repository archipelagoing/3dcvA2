"""Detect planes, render their inliers, and compare a bird's-eye homography warp."""
import json
import pickle
import sys
from pathlib import Path
import cv2
import numpy as np

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / 'src'))
from planes import ransac_plane, fit_plane, look_at, plane_homography, warp_bilinear
from pointcloud_renderer import render_pointcloud, scale_intrinsics
from run_teddy import save_image


def save_rgb(path, image):
    save_image(path, cv2.cvtColor(image, cv2.COLOR_RGB2BGR))


def main():
    output = Path('output/bonus')
    output.mkdir(parents=True, exist_ok=True)
    with open('data/data.obj', 'rb') as file:
        scene = pickle.load(file, encoding='latin1')
    points = np.hstack((scene[4], scene[3]))
    remaining = np.ones(points.shape[1], bool)
    K = scale_intrinsics(scene[2], 0.25)
    height, width = 512, 768
    rng = np.random.default_rng(532)
    threshold = 0.025
    detected = []
    ground = None
    for number in range(1, 9):
        available = np.flatnonzero(remaining)
        chosen = rng.choice(available, min(30000, len(available)), replace=False)
        plane, trials = ransac_plane(points[:3, chosen].T, rng, threshold)
        inliers = remaining & (np.abs(plane[:3] @ points[:3] + plane[3]) < threshold)
        # Refine on the full consensus, then classify all remaining points again.
        plane = fit_plane(points[:3, inliers].T)
        inliers = remaining & (np.abs(plane[:3] @ points[:3] + plane[3]) < threshold)
        positions = points[:3, inliers]
        center = np.median(positions, axis=1)
        is_ground = abs(plane[1]) > 0.85 and center[1] > 0
        sample_fraction = float((np.abs(plane[:3] @ points[:3, chosen] + plane[3]) < threshold).mean())
        description = {'sample_inlier_fraction': sample_fraction,
                       'estimated_sampling_success': 1-(1-sample_fraction**3)**trials,
                       'number': number, 'plane': plane.tolist(), 'inliers': int(inliers.sum()),
                       'ransac_trials': trials, 'median_position': center.tolist(), 'ground_candidate': bool(is_ground)}
        detected.append(description)
        print(json.dumps(description), flush=True)
        # Render the remaining cloud so earlier planes really are removed.
        colors = points[:, remaining].copy()
        colors[3:, inliers[remaining]] = np.array([0., 1., 0.])[:, None]
        image, _ = render_pointcloud(colors, K, np.eye(3), np.zeros(3), height, width)
        save_rgb(output / f'plane_{number}_inliers.png', image)
        if is_ground and ground is None:
            ground = (plane.copy(), positions.copy(), number)
        remaining[inliers] = False
        if number >= 3 and ground is not None:
            break
    if ground is None:
        raise RuntimeError('No ground candidate found; inspect detected planes before choosing another prior')
    plane, ground_points, ground_number = ground
    # A ground candidate must be supported by its position and the rendered image,
    # not normal orientation alone. Save evidence for inspection.
    target = np.median(ground_points, axis=1)
    target -= (plane[:3] @ target + plane[3]) * plane[:3]
    # Fit the robust ground footprint inside the bird's-eye frame with a margin.
    trial_R = look_at(target + plane[:3], target)
    offsets = trial_R @ (ground_points - target[:, None])
    span = np.quantile(np.abs(offsets[:2]), 0.98, axis=1)
    camera_height = float(max(K[0, 0]*span[0]/(width*0.40), K[1, 1]*span[1]/(height*0.40), 5.0))
    center_b = target + plane[:3] * camera_height
    R_b = look_at(center_b, target)
    t_b = -R_b @ center_b
    image_a, depth_a = render_pointcloud(points, K, np.eye(3), np.zeros(3), height, width)
    image_b, depth_b = render_pointcloud(points, K, R_b, t_b, height, width)
    H = plane_homography(K, K, R_b, t_b, plane)
    warped, warp_valid = warp_bilinear(image_a, H, height, width)
    save_rgb(output / 'image_a.png', image_a)
    save_rgb(output / 'birdseye_b.png', image_b)
    save_rgb(output / 'warped_a.png', warped)
    save_rgb(output / 'birdseye_comparison.png', np.hstack((image_b, warped)))
    save_image(output / 'warp_valid.png', warp_valid.astype(np.uint8)*255)
    # Project points EXACTLY on the fitted plane, independent of image rasterization.
    sample = ground_points[:, ::max(1, ground_points.shape[1]//1000)].copy()
    sample -= plane[:3, None]*(plane[:3] @ sample + plane[3])
    uv_a = K @ sample
    uv_b = K @ (R_b @ sample + t_b[:, None])
    via_H = H @ uv_a
    geometric_error = float(np.max(np.abs(via_H[:2]/via_H[2] - uv_b[:2]/uv_b[2])))
    assert geometric_error < 1e-7
    assert np.allclose(R_b @ R_b.T, np.eye(3)) and np.isclose(np.linalg.det(R_b), 1)
    assert np.allclose(R_b[2], -plane[:3])
    report = {'threshold_scene_units': threshold, 'sample_size': 30000, 'max_trials': 2000,
              'confidence': 0.999, 'seed': 532, 'planes': detected, 'ground_plane_number': ground_number,
              'ground_plane': plane.tolist(), 'K': K.tolist(), 'R_a': np.eye(3).tolist(), 't_a': [0,0,0],
              'R_b': R_b.tolist(), 't_b': t_b.tolist(), 'camera_center_b': center_b.tolist(),
              'target': target.tolist(), 'height_above_ground': camera_height, 'H_a_to_b': H.tolist(),
              'max_plane_projection_error_pixels': geometric_error,
              'image_b_rendered_pixels': int(np.isfinite(depth_b).sum()),
              'warp_mapped_pixels': int(warp_valid.sum())}
    (output / 'metrics.json').write_text(json.dumps(report, indent=2)+'\n')
    print(f'PASS: planar projection error {geometric_error:.3g} pixels; saved {output}', flush=True)


if __name__ == '__main__':
    main()
