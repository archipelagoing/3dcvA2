"""Render a small synthetic cloud to verify offscreen rendering independently of scene data."""
from pathlib import Path
import cv2
import numpy as np
import open3d as o3d

cloud = o3d.geometry.PointCloud()
x, y = np.meshgrid(np.linspace(-0.4, 0.4, 25), np.linspace(-0.3, 0.3, 19))
cloud.points = o3d.utility.Vector3dVector(np.column_stack((x.ravel(), y.ravel(), np.full(x.size, 2.0))))
cloud.colors = o3d.utility.Vector3dVector(np.tile([1.0, 0.2, 0.1], (x.size, 1)))
renderer = o3d.visualization.rendering.OffscreenRenderer(160, 120)
material = o3d.visualization.rendering.MaterialRecord()
material.shader = 'defaultUnlit'
renderer.scene.set_background(np.array([0., 0., 0., 1.]))
renderer.scene.add_geometry('cloud', cloud, material)
renderer.setup_camera(o3d.camera.PinholeCameraIntrinsic(160, 120, 150., 150., 80., 60.), np.eye(4))
image = np.asarray(renderer.render_to_image())
assert image.shape[:2] == (120, 160), image.shape
assert np.any(image[..., 0] > image[..., 1] + 20), 'Expected red cloud was not rendered'
Path('output').mkdir(exist_ok=True)
assert cv2.imwrite('output/renderer_check.png', cv2.cvtColor(image, cv2.COLOR_RGB2BGR))
print('PASS: rendered synthetic cloud to output/renderer_check.png')
