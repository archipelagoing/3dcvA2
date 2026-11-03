# 3D Computer Vision — Homework 2 TODO

Last updated: 2026-11-03.

## Current state

This repository contains the CS 532 Homework 2 handouts, Teddy stereo inputs,
and an Open3D rendering starter script. The assignment requires census-transform
stereo matching on Teddy (40 points) and on a rendered fish scene (60 points).
The optional bonus covers plane estimation and homography warping and is now
implemented, tested, and documented in a separate report.

The inputs have been inspected and the fish scene recovered from HW1. A Python
3.12 environment and pinned dependency manifest are present. Teddy and fish stereo
are implemented and evaluated. The NumPy CPU renderer is verified on this Mac;
Open3D offscreen rendering remains unsupported. Intrinsic scaling is implemented.
The fish input is at `data/data.obj`. Output review and the five-page report are
complete under the documented assumptions. The assignment is not finished:
course conventions need confirmation by the student. The complete workflow
passed, and the local submission ZIP passed archive and extracted-run verification.
Canvas checks and submission are reserved for the student.

## Next steps

1. Confirm Teddy evaluation-mask conventions for the final report (2k).
2. Confirm the resolution interpretation (3b).
3. Student: confirm Canvas upload organization and add identification if required (5f).
4. Student: submit the verified files through Canvas and check the receipt (5i).
5. Use the bonus-inclusive ZIP if submitting section 6; retain the required-only
   package as a separate artifact.

## Reference files and constraints

- `cs532f27_hw2 (1).pdf`: main assignment and submission requirements.
- `HW2Bonus-1 (1).pdf`: optional bonus requirements.
- `dolly_zoom_fast-1.py`: rendering starter; imports NumPy, OpenCV, SciPy, and Open3D.
- `teddy/teddyL.pgm`, `teddy/teddyR.pgm`: stereo image pair.
- `teddy/disp2.pgm`: ground-truth disparity image.
- `teddy 2.zip`: supplied data archive.
- `README.md`: environment, input conventions, and verified execution commands.
- Handout deadline: November 5 at 6:00 PM; the body does not state a year or timezone.
  Confirm the current deadline in Canvas. Late penalty: 3% per partial 24-hour period.
- Internet use is allowed, but searching for previous solutions or answers to the
  specific assignment questions is prohibited. Understand all submitted work.

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

Progress (2026-11-03): Section 1 is complete with the documented scene-unit
convention. `scripts/check_inputs.py` passed. The CPU renderer passed synthetic
occlusion, clipping, translation, and RGB checks, then rendered the full fish
scene to `output/fish_setup_check.png` (3072 × 2048; 5,837,992 occupied pixels;
3.91 seconds including load/write). PNG readback matched exactly and visual
inspection confirmed the fish scene. No maximum filtering is applied. The CPU
renderer adapts the HW1 projection approach with a nearest-depth buffer and
zero-based pixels. Original Open3D failure evidence is retained separately in
`scripts/check_open3d_renderer.py`. See JOURNAL.md entry 06.

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

Progress (2026-11-03): Implemented `src/stereo.py` and `scripts/run_teddy.py`.
All four runs completed and small independent checks passed. Census images,
raw/display disparity maps, masks, and `metrics.json` are in `output/teddy/`.
See `results/teddy.md` for the method, visualization explanation, exact metric
conventions, and results. Shared-interior errors: 18.8012%, 13.1459%, 12.8687%,
11.6175% in (3,5), (3,9), (7,5), (7,9) order. Full-image errors are also recorded.
Three optional refinements were also compared with the unchanged (7,9) baseline;
see `results/teddy_improvements.md`. Left/right checking plus row filling reduced
shared-interior error to 8.6756% and full-image error to 20.5055%. These are
separate experiments, not replacements for the required plain WTA results.
The refinement script now runs only consistency/filling; other attempts are
commented, and the original comparison metrics are preserved.
Task 2k remains open only for confirmation of the instructor's evaluation-mask
convention; the implemented masks and denominators are documented.

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

Progress (2026-11-03): `scripts/run_fish.py` rendered a 1536 × 1024 pair at
baseline 0.12 and ran all four window combinations with disparity search 0–44.
The geometry and image-readback checks passed; see `results/fish.md` for camera
matrices, depth limits, assumptions, and diagnostic results. Outputs are under
`output/fish/scale_0.5_baseline_0.12/`. No maximum filtering is applied. Task 3b
remains open for course confirmation; default scale 0.5 means quarter total pixels,
while configurable scale 0.25 means quarter width/height. The original dolly-zoom
sequence remains separate and unverified.

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

Progress (2026-11-03): `scripts/check_stereo.py` passed census, Hamming,
aggregation, identical/shifted inputs, borders, independent brute-force WTA, and
bad-pixel threshold checks. Fish geometry checks also passed (4f–4g).
All four Teddy census visualizations, four Teddy disparity views, both fish
RGB/grayscale views, and four fish disparity views were reviewed in the rendered
report. Automated checks covered 36 saved images: dimensions, binary masks,
disparity ranges, grayscale conversion, and census borders. Evidence is recorded
in `output/report_review.json`. Tasks 4h–4i are complete. `scripts/verify_workflow.py` ran all eight stages
in order successfully; the optional `--bonus` extension also passed all eleven
stages. Exit codes, timings, and individual logs are saved under
`output/verification/`. The rebuilt PDF pages match the reviewed pages exactly.

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
      (PDF reviewed; packaged images decoded and checksums matched reviewed originals).
- [ ] 5i — Submit through Canvas and verify the uploaded files and receipt.

Progress (2026-11-03): `output/pdf/homework2_report.pdf` exists and contains
one page of explanation/results followed by four figure pages. It includes
census visualizations and discussion, all four Teddy disparity maps/error rates,
and the fish views/maps with baseline, calibration, disparity range, and depth
justification. All five rendered PDF pages were visually reviewed; no clipping
was found. Rebuild with `scripts/build_report.py`. Tasks 5a–5d are complete.
The report retains the assumptions pending 2k/3b; revise it if course guidance
changes them and add student identification if required. Built `output/submission/homework2_submission.zip` (142.5 MiB), containing
source directories, required course inputs, separate generated outputs, the PDF,
RUNNING.txt instructions, workflow logs, and a SHA-256 manifest. CRC and all
85 packaged-file hashes passed; all packaged images decoded successfully.
The extracted-copy workflow passed all eight stages and reproduced numerical
metrics exactly (excluding runtimes). Evidence: `output/verification/package_check.json`.
The rebuilt PDF rendered identically to the reviewed five pages. Tasks 5e, 5g,
and 5h are complete. Task 5f is locally prepared but awaits student confirmation
of Canvas organization. Nothing has been uploaded.
Per the latest instruction, course confirmation and Canvas submission are for
the student to handle.

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

Progress (2026-11-03): All bonus steps are implemented in `src/planes.py` and
`scripts/run_bonus.py`. Detected three sequential planes with 2,356,913; 854,217;
and 407,538 inliers. The second is the visually confirmed ground. Its unit plane
is n=(0.00463422,-0.99871259,0.05051415), d=1.58323646 in the original camera
frame. Green inlier renders show earlier planes removed. Rendered image A and a
bird's-eye image B, implemented plane-induced H and manual bilinear inverse
warping, and saved a side-by-side comparison. Exact plane-point projection agrees
to 3.84e-13 pixels. Tests, deterministic rerun, and all eleven full-workflow stages
passed. Three bonus PDF pages were visually reviewed. See `results/bonus.md`,
`output/bonus/metrics.json`, and `output/pdf/homework2_bonus.pdf`.
The overhead render has missing surfaces and sparse points; the homography
incorrectly flattens off-plane fountain geometry. These are explained rather than
hidden. `output/submission/homework2_submission_with_bonus.zip` (147.8 MiB)
passed CRC, all 104 file hashes, and image decoding. An extracted copy reran the
bonus checks, rendering, and report successfully, reproducing exact metrics and
PNG bytes. Evidence: `output/verification/bonus_package_check.json`.

## Blockers and decisions

- **Recovered input:** `data/data.obj` was copied from the local HW1 project;
  it is excluded from version control because it is approximately 267 MiB.
- **Rendering decision (2026-11-03):** Use verified NumPy CPU projection on this
  Mac. Open3D offscreen rendering remains unsupported and is optional.
- **Unit convention (2026-11-03):** Use scene units for XYZ, camera translation,
  depth, and baseline. Physical scale is unconfirmed; do not label results as metres.
  A common scaling of baseline and depth cancels in `d = fx * baseline / Z`.
- **Open question:** Confirm the intended resolution reduction for Problem 2.
- **Open question:** Confirm evaluation-mask conventions for Teddy where the
  handout does not explicitly define them.
- **Open question:** Confirm the deadline and submission organization in Canvas.
- **Bonus completion (2026-11-03):** Section 6 is complete. Extended eleven-stage
  workflow passed; bonus-inclusive ZIP and extracted bonus reproduction passed.
  The required-only ZIP is preserved separately.
- **Local package verification (2026-11-03):** All eight workflow stages passed
  in the repository and extracted ZIP; metrics reproduced. Archive path:
  `output/submission/homework2_submission.zip` (142.5 MiB).
- **Student handoff (2026-11-03):** Course convention checks, Canvas requirements,
  identification if required, and submission are reserved for the student.
- **Status reconciliation (2026-11-03):** Updated previously frozen checklist
  entries against the existing report and review evidence; unfinished validation,
  packaging, submission, and optional bonus tasks remain open.
- **Decision (2026-11-03):** Use `TODO.md` as the single project checklist,
  replacing the generic `todoSimple.md` template.

## Maintenance

- Keep checklist labels in section order (`1a`, `1b`, `2a`, and so on).
- Use `[x]` only when a task has supporting evidence; otherwise leave it unchecked.
- After each work session, add one JOURNAL.md entry listing TODO items covered,
  what was tried, what worked, and what did not work.
- After meaningful project changes, update the date, relevant tasks, progress
  notes, next steps, and blockers.
- Record actual commands, results, and output paths as verification becomes available.
- Keep optional work separate from required deliverables and preserve unresolved tasks.
- This checklist records planned work; it does not authorize unrelated execution.
