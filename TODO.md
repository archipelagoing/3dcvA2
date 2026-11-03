# 3D Computer Vision — Homework 2 TODO

Last updated: 2026-11-03.

## Current state

This repository contains the CS 532 Homework 2 handouts, Teddy stereo inputs,
and an Open3D rendering starter script. The assignment requires census-transform
stereo matching on Teddy (40 points) and on a rendered fish scene (60 points).
The optional bonus covers plane estimation and homography warping.

The code and handouts have been inspected. No implementation has been run or
validated. No stereo implementation, generated results, report, or dependency
manifest is present. `scale_intrinsics()` is a placeholder. The renderer expects
`data/data.obj`, which is absent from this checkout.

## Next steps

1. Recover the HW1 fish point-cloud input and establish a reproducible Python environment.
2. Implement census-transform stereo and evaluate all four Teddy parameter combinations.
3. Adapt the renderer to produce a rectified fish stereo pair and justify the camera geometry.
4. Run fish stereo, inspect the outputs, and prepare the report and submission files.
5. Attempt the bonus only after the required work is complete.

## Reference files and constraints

- `cs532f27_hw2 (1).pdf`: main assignment and submission requirements.
- `HW2Bonus-1 (1).pdf`: optional bonus requirements.
- `dolly_zoom_fast-1.py`: rendering starter; imports NumPy, OpenCV, SciPy, and Open3D.
- `teddy/teddyL.pgm`, `teddy/teddyR.pgm`: stereo image pair.
- `teddy/disp2.pgm`: ground-truth disparity image.
- `teddy 2.zip`: supplied data archive.
- `README.md`: currently only a short project description.
- Handout deadline: November 5 at 6:00 PM; the body does not state a year or timezone.
  Confirm the current deadline in Canvas. Late penalty: 3% per partial 24-hour period.
- Internet use is allowed, but searching for previous solutions or answers to the
  specific assignment questions is prohibited. Understand all submitted work.

## 1. Inputs and setup

- [x] 1a — Identify the assignment requirements and available starter files.
- [x] 1b — Confirm the extracted Teddy input filenames are present.
- [ ] 1c — Verify Teddy image dimensions, readability, and left/right ordering.
- [ ] 1d — Recover the HW1 fish scene as `data/data.obj` or document an explicit replacement path.
- [ ] 1e — Inspect the loaded scene structure, point coordinates, colors, intrinsics, and units.
- [ ] 1f — Create a reproducible environment and record working dependency versions.
- [ ] 1g — Verify Open3D offscreen rendering works on the intended machine.
- [ ] 1h — Document commands and input/output paths in the README.

Progress: File presence and source inspection completed on 2026-11-03. Teddy
contents, rendering support, and runtime dependencies have not been verified.
The fish input is the main blocker for Problem 2 and the bonus.

## 2. Problem 1 — Teddy stereo (40 points)

- [ ] 2a — Implement the census transform for window sizes `Wc = 3` and `Wc = 7`.
- [ ] 2b — Save a census visualization for each size, scaling the specified possible
      Hamming-value range to `[0, 255]`; set invalid census borders to black.
- [ ] 2c — Explain whether the census visualizations look alike and why.
- [ ] 2d — Compute matching costs using Hamming distance across disparities `0` through `63`.
- [ ] 2e — Aggregate costs over windows `WA = 5` and `WA = 9`.
- [ ] 2f — Select each pixel's disparity with winner-take-all matching.
- [ ] 2g — Produce all four disparity maps for `(Wc, WA) = (3,5), (3,9), (7,5), (7,9)`.
- [ ] 2h — Set pixels whose aggregation windows cross image boundaries to black;
      explicitly handle invalid correspondences at shifted image borders.
- [ ] 2i — Convert ground-truth values by dividing by 4 and rounding to the nearest integer.
- [ ] 2j — Compute and record the bad-pixel percentage for each parameter combination:
      `100 * count(abs(predicted - ground_truth) > 1) / evaluated_pixel_count`.
- [ ] 2k — Document the evaluation mask and denominator, including treatment of borders
      and any invalid ground-truth values; confirm ambiguities with course guidance.

Progress: No stereo code or measured error rates are present. A disparity error
of exactly one level is acceptable under the handout's metric.

## 3. Problem 2 — Fish stereo (60 points)

- [ ] 3a — Implement `scale_intrinsics()` and scale image dimensions and intrinsics
      consistently to preserve horizontal and vertical field of view.
- [ ] 3b — Resolve what “¼ of the default size” means in course guidance before choosing
      the scale: quarter width/height and quarter total pixel count are different.
- [ ] 3c — Ensure rendered images have no 2D maximum-filter hole filling. The current
      starter imports `maxfilt` but does not call it; verify any reused HW1 code too.
- [ ] 3d — Adapt the camera path to render two rectified views with parallel camera axes
      and a horizontal baseline, using consistent intrinsics.
- [ ] 3e — Keep focal length fixed between the stereo views; remove the dolly-zoom
      focal-length changes from the stereo capture path.
- [ ] 3f — Inspect scene depths and select a baseline and disparity search range.
- [ ] 3g — Explain the choices with `d = fx * baseline / Z`, using consistent units,
      and report the minimum and maximum depths covered by the search.
- [ ] 3h — Check camera translation conventions and disparity sign with a known 3D point.
- [ ] 3i — Save both RGB views and verify channel order before grayscale conversion.
- [ ] 3j — Convert to grayscale with `0.30 * R + 0.59 * G + 0.11 * B`.
- [ ] 3k — Run the Problem 1 stereo method using a suitable fish disparity range.
- [ ] 3l — Save the fish disparity maps and document the selected window parameters.

Progress: The starter currently renders a dolly-zoom sequence, saves
`SampleOutput*.jpg`, and writes `dolly_zoom.mp4`. Its loop uses 40 frames despite
an outdated comment mentioning 75. These outputs have not been generated or
checked. A dedicated stereo capture path is still needed.

## 4. Validation

- [ ] 4a — Confirm identical left/right inputs have zero matching cost at disparity zero.
- [ ] 4b — Confirm a controlled horizontal shift of N pixels produces zero matching
      cost at disparity N wherever corresponding windows are valid.
- [ ] 4c — Check census descriptors and Hamming costs on a small hand-computed example.
- [ ] 4d — Check border handling and aggregation alignment for each window size.
- [ ] 4e — Verify ground-truth conversion and bad-pixel threshold on known values.
- [ ] 4f — Check stereo rectification by comparing vertical coordinates of projected points.
- [ ] 4g — Verify resized intrinsics preserve the field of view.
- [ ] 4h — Inspect all saved census images, stereo views, and disparity maps for scaling,
      cropping, color-order, and invalid-region problems.
- [ ] 4i — Run the complete workflow from documented commands and retain measured results.

Progress: No runtime checks or numerical results have been recorded. Source
inspection alone does not establish that the renderer or stereo pipeline works.

## 5. Report and submission

- [ ] 5a — Include both Teddy census visualizations and the required appearance discussion.
- [ ] 5b — Include four Teddy disparity maps and their bad-pixel percentages.
- [ ] 5c — Include fish disparity results and justify baseline, disparity range, and
      corresponding depth limits.
- [ ] 5d — Keep explanatory text to at most one page, as specified by the handout.
- [ ] 5e — Package source code excluding libraries, points used in computation, resulting
      images, and the PDF report into the requested ZIP submission.
- [ ] 5f — Include code and output images/videos separately as requested; confirm Canvas
      upload organization if the handout's wording is unclear.
- [ ] 5g — Verify the submission contains required inputs and reproducible instructions,
      and excludes environment folders and machine-specific clutter.
- [ ] 5h — Review the final PDF and open the packaged images/videos before submission.
- [ ] 5i — Submit through Canvas and verify the uploaded files and receipt.

Progress: No report or submission package exists. Listing submission here does
not perform or authorize an upload.

## 6. Optional bonus — Plane estimation and homography

- [ ] 6a — Implement RANSAC plane estimation using three 3D points per minimal sample;
      obtain plane parameters from their homogeneous-coordinate null space.
- [ ] 6b — Explain the distance threshold, iteration budget, sampling, and inlier criteria.
- [ ] 6c — Recolor detected inliers green and render a result image.
- [ ] 6d — Remove those inliers and repeat twice to obtain three plane-result images.
- [ ] 6e — Continue if necessary until one detected plane is the ground plane.
- [ ] 6f — Report the ground plane parameters `(n, d)` and their coordinate convention.
- [ ] 6g — Render image A from a chosen pose `[Ra, ta]`.
- [ ] 6h — Select a bird's-eye pose `[Rb, tb]` with optical axis parallel to the ground
      plane normal and suitable framing, then render image B.
- [ ] 6i — Compute the plane-induced homography and warp image A into B's viewpoint.
- [ ] 6j — Account for the coordinate frame in which the plane and camera poses are defined.
- [ ] 6k — Compare rendered B and warped A side by side and explain differences.

Progress: Optional and not started. Requires the missing HW1 scene and a working
renderer; prioritize the 100-point core assignment first.

## Blockers and decisions

- **Missing input:** `data/data.obj` is required by the current renderer.
- **Open question:** Confirm the intended resolution reduction for Problem 2.
- **Open question:** Confirm evaluation-mask conventions for Teddy where the
  handout does not explicitly define them.
- **Open question:** Confirm the deadline and submission organization in Canvas.
- **Decision (2026-11-03):** Use `TODO.md` as the single project checklist,
  replacing the generic `todoSimple.md` template.

## Maintenance

- Use `[x]` only when a task has supporting evidence; otherwise leave it unchecked.
- After meaningful project changes, update the date, relevant tasks, progress
  notes, next steps, and blockers.
- Record actual commands, results, and output paths as verification becomes available.
- Keep optional work separate from required deliverables and preserve unresolved tasks.
- This checklist records planned work; it does not authorize unrelated execution.
