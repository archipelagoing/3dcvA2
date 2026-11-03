# Bonus: plane estimation and a bird's-eye homography

## Run

```sh
.venv/bin/python scripts/check_bonus.py
.venv/bin/python scripts/run_bonus.py
.venv/bin/python scripts/build_bonus_report.py
```

All images and exact parameters are in `output/bonus/`. A separate three-page
report is `output/pdf/homework2_bonus.pdf`. The required report is unchanged.

## Plane detection

Use `n.X + d = 0`, with unit-length n. Minimal samples contain three noncollinear
points; SVD of their homogeneous 3 x 4 matrix yields the plane null space.
Distance is `abs(n.X+d)` in scene units. Threshold: 0.025; fixed seed: 532.

For speed, score hypotheses on 30,000 randomly selected remaining points. The
adaptive budget targets 0.999 all-inlier-sample probability with a 100-trial
floor and 2,000-trial cap. Confidence is a sampling-budget heuristic, not a
certificate of correct geometry. Refine the sample consensus twice with covariance
least squares, classify the full remaining cloud, refine on that full consensus,
and classify again. Remove the final consensus before detecting the next plane.

| Plane | Inliers from remaining full cloud | Trials | Visual interpretation |
| --- | ---: | ---: | --- |
| 1 | 2,356,913 | 102 | Background wall |
| 2 | 854,217 | 486 | Ground |
| 3 | 407,538 | 2,000 | Parts of the fountain facade |

Current inliers are green; previously removed planes are absent. The ground
candidate uses `abs(n_y)>0.85` and positive median y (the original camera has
image y downward); the rendered second consensus visibly covers the floor.
A plane need not be a single connected surface, and threshold choice affects
which nearby points join its consensus. A deterministic rerun reproduced the results.

Ground parameters in the original world/reference-camera coordinates:

```text
n = (0.0046342223, -0.9987125937, 0.0505141478)
d = 1.5832364608
```

## Bird's-eye pose

Render image A with `Ra=I`, `ta=0`, at 768 x 512. Use
`fx=689.875`, `fy=691.05`, `cx=380.175`, `cy=251.70`.
Project the median ground position onto the plane for the target. Camera B sits
8.93276 scene units along n above it, looking along -n. Its orientation is a
proper rotation with world-x projected into the ground tangent as image-right.
Height frames the 98th-percentile ground footprint with a margin.

```text
Cb = (0.29739521, -7.04416896, 6.19717004)
Rb = [[ 0.99998926,  0.00462831, -0.00023410],
      [ 0.00000000, -0.05051469, -0.99872332],
      [-0.00463422,  0.99871259, -0.05051415]]
tb = -Rb Cb = (-0.26333871, 5.83342421, 7.34952321)
```

## Homography and comparison

Because A is the world frame, the plane-induced A-to-B mapping is
`H = Kb (Rb - tb n^T/d) Ka^-1`. The minus sign follows from `n.X+d=0`.
Use inverse mapping and manually implemented four-neighbor bilinear interpolation.
No library homography estimator or warp is used. Samples outside A remain black.

The direct B render and warped A are saved separately and side by side. Ground
features align geometrically, while the raised fountain is stretched into the
floor by the homography. One plane homography cannot reproduce off-plane parallax.
The overhead render has sparse surfaces and large holes because the single-view
point cloud lacks the newly visible geometry. The warp interpolates existing pixels
and can look denser even though it gives incorrect geometry for raised objects.

Exact points placed on the fitted plane agree under direct projection and H to
within 3.84e-13 pixels. This does not imply whole-image photometric agreement:
noise, finite inlier tolerance, interpolation, visibility, and off-plane geometry
all affect the actual images.

## Verification

Checks cover exact planes, noisy planes with outliers, collinear rejection,
rotation handedness, homography sign invariance and point projection, and identity,
translated, and half-pixel bilinear warps. All passed. The three inlier renders,
side-by-side comparison, and every rendered bonus PDF page were visually reviewed.
