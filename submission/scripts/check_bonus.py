"""Check plane fitting, RANSAC robustness, camera poses, and inverse warping."""
import sys
from pathlib import Path
import numpy as np
sys.path.insert(0, str(Path(__file__).resolve().parents[1] / 'src'))
from planes import plane_from_three, ransac_plane, look_at, plane_homography, warp_bilinear

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
