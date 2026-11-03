# Assignment 2 TODO

Last updated: 2026-11-03.

Teddy stereo, fish stereo, and the bonus are implemented and tested. The repo now
has root-level Python files and two folders: `data/` and `results/`.
Run `.venv/bin/python -B run.py` to repeat the checks, experiments, and reports.
The cleanup preserved the previous numerical results and selected image bytes.

The minimal submission is now in `handin/`; see `handin/RUN.txt`. It contains
only six Python files, requested figures, reports/measurements, and the four inputs.

## Next steps

1. Confirm the Teddy evaluation convention (2k) and quarter-resolution wording (3b).
2. Add identification if required and check Canvas file organization (5f).
3. Visually review the relocated reports and create a fresh ZIP of the simplified layout.
4. Submit and verify the receipt (5i). These external steps are for the student.

## 1. Inputs and setup

- [x] 1a — Identify the assignment requirements and available starter files.
- [x] 1b — Confirm the extracted Teddy input filenames are present.
- [x] 1c — Verify Teddy image dimensions, readability, and left/right ordering.
- [x] 1d — Recover the HW1 fish scene as `data/data.obj` or document an explicit replacement path.
- [x] 1e — Inspect scene structure, coordinates, colors, and intrinsics; document
      the unit convention (scene units; physical scale is not supplied).
- [x] 1f — Create a reproducible environment and record working dependency versions.
- [x] 1g — Verify image rendering on the intended machine using a compatible
      backend (NumPy CPU projection verified; Open3D is unsupported on this Mac).
- [x] 1h — Document commands and input/output paths in the README.

## 2. Problem 1 — Teddy stereo (40 points)

- [x] 2a — Implement the census transform for window sizes `Wc = 3` and `Wc = 7`.
- [x] 2b — Save a census visualization for each size, scaling the specified possible
      Hamming-value range to `[0, 255]`; set invalid census borders to black.
- [x] 2c — Explain whether the census visualizations look alike and why.
- [x] 2d — Compute matching costs using Hamming distance across disparities `0` through `63`.
- [x] 2e — Aggregate costs over windows `WA = 5` and `WA = 9`.
- [x] 2f — Select each pixel's disparity with winner-take-all matching.
- [x] 2g — Produce all four disparity maps for `(Wc, WA) = (3,5), (3,9), (7,5), (7,9)`.
- [x] 2h — Set pixels whose aggregation windows cross image boundaries to black;
      explicitly handle invalid correspondences at shifted image borders.
- [x] 2i — Convert ground-truth values by dividing by 4 and rounding to the nearest integer.
- [x] 2j — Compute and record the bad-pixel percentage for each parameter combination:
      `100 * count(abs(predicted - ground_truth) > 1) / evaluated_pixel_count`.
- [ ] 2k — Document the evaluation mask and denominator, including treatment of borders
      and any invalid ground-truth values; confirm ambiguities with course guidance.

## 3. Problem 2 — Fish stereo (60 points)

- [x] 3a — Implement `scale_intrinsics()` and scale image dimensions and intrinsics
      consistently to preserve horizontal and vertical field of view.
- [ ] 3b — Resolve what “¼ of the default size” means in course guidance before choosing
      the scale: quarter width/height and quarter total pixel count are different.
- [x] 3c — Ensure rendered images have no 2D maximum-filter hole filling. The current
      starter imports `maxfilt` but does not call it; verify any reused HW1 code too.
- [x] 3d — Adapt the camera path to render two rectified views with parallel camera axes
      and a horizontal baseline, using consistent intrinsics.
- [x] 3e — Keep focal length fixed between the stereo views; remove the dolly-zoom
      focal-length changes from the stereo capture path.
- [x] 3f — Inspect scene depths and select a baseline and disparity search range.
- [x] 3g — Explain the choices with `d = fx * baseline / Z`, using consistent units,
      and report the minimum and maximum depths covered by the search.
- [x] 3h — Check camera translation conventions and disparity sign with a known 3D point.
- [x] 3i — Save both RGB views and verify channel order before grayscale conversion.
- [x] 3j — Convert to grayscale with `0.30 * R + 0.59 * G + 0.11 * B`.
- [x] 3k — Run the Problem 1 stereo method using a suitable fish disparity range.
- [x] 3l — Save the fish disparity maps and document the selected window parameters.

## 4. Validation

- [x] 4a — Confirm identical left/right inputs have zero matching cost at disparity zero.
- [x] 4b — Confirm a controlled horizontal shift of N pixels produces zero matching
      cost at disparity N wherever corresponding windows are valid.
- [x] 4c — Check census descriptors and Hamming costs on a small hand-computed example.
- [x] 4d — Check border handling and aggregation alignment for each window size.
- [x] 4e — Verify ground-truth conversion and bad-pixel threshold on known values.
- [x] 4f — Check stereo rectification by comparing vertical coordinates of projected points.
- [x] 4g — Verify resized intrinsics preserve the field of view.
- [x] 4h — Inspect all saved census images, stereo views, and disparity maps for scaling,
      cropping, color-order, and invalid-region problems.
- [x] 4i — Run the complete workflow from documented commands and retain measured results.

## 5. Report and submission

- [x] 5a — Include both Teddy census visualizations and the required appearance discussion.
- [x] 5b — Include four Teddy disparity maps and their bad-pixel percentages.
- [x] 5c — Include fish disparity results and justify baseline, disparity range, and
      corresponding depth limits.
- [x] 5d — Keep explanatory text to at most one page, as specified by the handout.
- [x] 5e — Package source code excluding libraries, points used in computation, resulting
      images, and the PDF report into the requested ZIP submission.
- [ ] 5f — Include code and output images/videos separately as requested; confirm Canvas
      upload organization (local source/output directories are packaged; remaining
      Canvas confirmation is delegated to the student).
- [x] 5g — Verify the submission contains required inputs and reproducible instructions,
      and excludes environment folders and machine-specific clutter.
- [x] 5h — Review the final PDF and open the packaged images/videos before submission
      (reports reviewed; selected outputs checked against the earlier verified package).
- [ ] 5i — Submit through Canvas and verify the uploaded files and receipt.

## 6. Optional bonus — Plane estimation and homography

- [x] 6a — Implement RANSAC plane estimation using three 3D points per minimal sample;
      obtain plane parameters from their homogeneous-coordinate null space.
- [x] 6b — Explain the distance threshold, iteration budget, sampling, and inlier criteria.
- [x] 6c — Recolor detected inliers green and render a result image.
- [x] 6d — Remove those inliers and repeat twice to obtain three plane-result images.
- [x] 6e — Continue if necessary until one detected plane is the ground plane.
- [x] 6f — Report the ground plane parameters `(n, d)` and their coordinate convention.
- [x] 6g — Render image A from a chosen pose `[Ra, ta]`.
- [x] 6h — Select a bird's-eye pose `[Rb, tb]` with optical axis parallel to the ground
      plane normal and suitable framing, then render image B.
- [x] 6i — Compute the plane-induced homography and warp image A into B's viewpoint.
- [x] 6j — Account for the coordinate frame in which the plane and camera poses are defined.
- [x] 6k — Compare rendered B and warped A side by side and explain differences.

## Evidence and conventions

- **Setup:** `data/` contains the three Teddy images and the trusted HW1 scene.
  Use scene units consistently; physical metre units are unconfirmed.
- **Teddy:** `results/teddy_metrics.json` retains full-image, valid-output, and
  shared-interior errors. Shared-interior scores are 18.8012%, 13.1459%, 12.8687%,
  11.6175% for (3,5), (3,9), (7,5), (7,9). The best refinement scores 8.6756%;
  required unfiltered outputs remain separate.
- **Fish:** `results/fish_metrics.json` records calibration, poses, baseline 0.12,
  disparity search 0–44, and depth-derived diagnostic results. Scale 0.5 means
  quarter total pixels; the alternative interpretation remains a course question.
- **Bonus:** `results/bonus_metrics.json` records three planes, with the ground
  found second. Tests include exact/noisy plane fits and plane-homography projection.
- **Reports:** `results/report.pdf` and `results/bonus.pdf`. Each has one page of
  explanatory text followed by figures. The reports have been rendered and reviewed.
- **Cleanup:** The full simplified run passed and metrics reproduced. Duplicate
  archives, extracted checkouts, image copies, temporary files, and packaging
  helpers were removed. A temporary backup was made before deletion, but it is no longer present
  at the later status check. Recreate the submission ZIP from the current layout.
- **Submission:** The current repository contains the needed source, inputs, and
  results. Old ZIP copies are no longer available locally; create a new ZIP and
  do not upload `.git/` or `.venv/`.
  Course confirmation and Canvas submission have not been performed.

## Maintenance

Keep the existing labels. Check tasks only with evidence, and record each work
session in JOURNAL.md with what was tried, what worked, and what did not work.
