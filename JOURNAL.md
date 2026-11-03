# Homework 2 Work Log

One entry per work session, oldest first. Each entry lists the [TODO.md](TODO.md)
items covered, what was tried, what worked, and what did not work.
Entries 01–03 were reconstructed from the recorded work on 2026-11-03.

## 01 — Repository review and checklist setup
Date: 2026-11-03
TODO items covered: 1a–1b; requirements identified for sections 2–6.

### What was tried
- Read the README, rendering starter, and both homework handouts.
- Inventoried the repository and replaced the generic checklist with assignment tasks.

### What worked
- Identified the required Teddy and fish stereo deliverables and optional bonus.
- Confirmed the Teddy files were present.
- Created [TODO.md](TODO.md) and the reusable [journal prompt](JOURNAL_PROMPT.md).

### What did not work
- PDF extraction through `pypdf` failed because the package was missing; `pdftotext`
  successfully read the handouts instead.
- The fish input was absent, and `scale_intrinsics()` was unfinished.
- No runtime workflow was verified during this session.

## 02 — Input recovery, environment setup, and rendering check
Date: 2026-11-03
TODO items covered: 1c–1h; checklist task labels added throughout sections 1–6.

### What was tried
- Compared Teddy inputs with the ZIP and checked three same-row patch matches.
- Located the HW1 fish input and copied it into `data/data.obj`.
- Inspected cloud shapes, coordinates, colors, and camera intrinsics.
- Created a Python 3.12 environment and installed the required libraries.
- Ran dependency checks and a small Open3D render inside and outside the sandbox.
- Added [input checks](scripts/check_inputs.py), a [rendering check](scripts/check_renderer.py),
  [pinned dependencies](requirements.txt), and [setup instructions](README.md).

### What worked
- All Teddy files are readable, 450 × 375 uint8, and byte-identical to the ZIP.
  Left/right/ground-truth ranges are 0–254, 0–255, and 0–211.
- Patch centers `(200,150)`, `(300,200)`, `(150,250)` yielded disparities 17, 33, 19,
  close to ground-truth values 17.25, 32.75, 19.25. This supports left/right ordering;
  it is not a full stereo evaluation.
- Recovered the 267 MiB scene from the local HW1 project. It contains 54,795
  foreground points and 5,786,684 background points; XYZ values are finite and
  RGB values are within `[0,1]`.
- Scene image size is 3072 × 2048. Intrinsics are `fx=2759.5`, `fy=2764.2`,
  `cx=1520.7`, `cy=1006.8`. Foreground Z is 3.8663–4.2190; background Z is
  4.7902–9.6567 in unconfirmed scene units.
- Installed NumPy 2.5.4, OpenCV 5.0.0.93, SciPy 1.18.1, and Open3D 0.19.0.
  `.venv/bin/python -m pip check` reported no broken requirements.
- `.venv/bin/python scripts/check_inputs.py` passed. Tasks 1c, 1d, 1f, and 1h
  were marked complete. Local data and generated outputs were excluded from Git.

### What did not work
- The default Python 3.14 lacked the required libraries; setup used Python 3.12.
- Dependency downloads failed under sandbox network restrictions; the permitted
  outside-sandbox installation succeeded.
- A render attempt made before installation finished failed to import Open3D.
- After installation, the sandboxed render exited with status 134. Outside the
  sandbox, Open3D raised `EGL Headless is not supported on this platform` when
  creating `OffscreenRenderer(160, 120)` on Intel macOS. No image was produced.
- Task 1g remains incomplete. Task 1e remains incomplete because physical scene
  units are unconfirmed. The full fish renderer was not run.

## 03 — Investigating the rendering failure and supplied alternative
Date: 2026-11-03
TODO items covered: investigation of 1g and the rendering requirements in section 3.

### What was tried
- Rechecked the HW2 and HW1 handouts and the original HW1 Python starter.
- Checked Open3D 0.19.0 source for the reported error.

### What worked
- Established that the failing Open3D headless path is Linux-specific in that version.
- Confirmed the failure affects fish image generation and rendering for the bonus;
  Teddy stereo uses supplied images and can proceed independently.
- Found a NumPy-based `PointCloud2Image()` in the original HW1 starter. Its
  `pyrender` viewer is optional; image projection itself does not use Open3D.
- Confirmed HW2 requests reusing the HW1 renderer and disabling maximum filtering.
  Neither inspected handout gives a Mac-specific renderer instruction.

### What did not work
- No replacement renderer was implemented or tested during this investigation.
  The NumPy path is a candidate, not a verified fix; 1g remains open.

## 04 — Simplifying the work log
Date: 2026-11-03
TODO items covered: documentation maintenance; no implementation tasks attempted.

### What was tried
- Reorganized the journal around work sessions and updated the reusable prompt.

### What worked
- Each session now lists the TODO items covered, attempts, successes, and failures.
- Preserved the recorded findings and unfinished work without marking new tasks complete.

### What did not work
- No execution failures occurred during this documentation update.

## 05 — Reviewing the HW1 context
Date: 2026-11-03
TODO items covered: context review for 1g and section 3; no implementation attempted.

### What was tried
- Reviewed the local HW1 README, notes, Python starter instructions, and source references.
- Checked whether the added context specifies a Mac-only setup or a verified solution.

### What worked
- The original Python instructions call for running `SampleCameraPath.py` from
  its data directory, using NumPy, OpenCV, and SciPy for image generation.
- The original NumPy renderer remains the supplied alternative to investigate.
  The optional `pyrender` viewer is separate from point projection.

### What did not work
- The reviewed instructions do not provide a Mac-specific command or confirm that
  the renderer has been tested on this machine. HW1 documentation describes its
  notebook as an unfinished scaffold, so it does not establish a working solution.
- No new HW1 attachment appeared inside this repository during this review;
  the reviewed context was the existing sibling `cs532hw1` project.
- Rendering and physical-unit checks remain open; no TODO completion status changed.

## 06 — Completing inputs and setup with CPU rendering
Date: 2026-11-03
TODO items covered: 1e, 1g, 1h; section 1 completed with documented conventions.

### What was tried
- Searched the HW1 text and source materials for physical-unit documentation.
- Adapted HW1's NumPy pinhole projection into [a reusable CPU renderer](src/pointcloud_renderer.py).
  Used nearest-depth visibility rather than input-order overwriting and zero-based pixels.
- Preserved the original Open3D check as `scripts/check_open3d_renderer.py`.
- Ran `.venv/bin/python scripts/check_renderer.py` against synthetic points and
  the recovered real scene, then opened the resulting PNG for visual review.

### What worked
- Synthetic checks passed for occlusion, behind-camera and out-of-frame rejection,
  horizontal camera translation, and RGB channel order.
- Full scene rendering passed: 3072 × 2048 with 5,837,992 occupied pixels;
  load/render/write took 3.91 seconds. Saved PNG readback matched the RGB array exactly.
- [The output](output/fish_setup_check.png) visibly depicts the fish and fountain.
  Black uncovered regions remain; no maximum filtering or hole filling was applied.
- Documented the working command, camera conventions, input/output locations, and
  visibility behavior in README. Task 1g now measures successful rendering using
  a compatible backend rather than requiring Open3D specifically.
- Task 1e now records the defensible convention: lengths are in scene units,
  consistently shared by points, translation, depth, and baseline. Physical units
  are not needed for disparity when baseline and depth use the same scale.

### What did not work
- No authoritative physical-unit statement was found; a metres assumption is not
  justified. Revised 1e to document that limitation instead of claiming confirmation.
- Open3D's previously recorded platform failure remains unresolved; CPU rendering
  bypasses it. No new Open3D success is claimed.
- The original dolly-zoom sequence, reduced-resolution stereo pair, and disparity
  pipeline were not attempted in this session; those remain later work.

## 07 — Implementing and evaluating Teddy stereo
Date: 2026-11-03
TODO items covered: 2a–2k, 4a–4e; partial visual review for 4h.

### What was tried
- Implemented readable census, Hamming distance, window sums, winner-take-all
  matching, and error calculation in [src/stereo.py](src/stereo.py).
- Added [a Teddy runner](scripts/run_teddy.py) and [independent small checks](scripts/check_stereo.py).
- Ran the checks, then all four (Wc, WA) combinations over disparities 0–63.
- Compared whole-image errors, valid-known-truth errors, and an identical shared
  interior for all settings. Inspected four disparity views and two left census images.

### What worked
- Small checks passed: hand-computed bits, 48-bit counts, direct versus integral
  sums, identical/shifted images, border handling, brute-force WTA, and error threshold.
- All four Teddy runs completed in about one second each. Generated census images
  for both views, raw/display disparity maps, masks, and exact counts in
  `output/teddy/metrics.json`.
- Shared-interior bad-pixel rates were 18.8012%, 13.1459%, 12.8687%, 11.6175%
  for (3,5), (3,9), (7,5), (7,9), using the same 131,311 pixels.
- Full-image rates were 27.9911%, 24.4480%, 24.1807%, 24.5031% respectively.
- Larger windows visibly reduced speckle. Recorded the census visualization
  interpretation, output conventions, assumptions, and comparisons in
  [results/teddy.md](results/teddy.md). Completed 2a–2j and 4a–4e.

### What did not work
- Results are imperfect near occlusions, repeated textures, and borders. No
  postprocessing was used to hide these errors.
- The handout does not fully specify the evaluation denominator or invalid-GT
  treatment. Excluding stored GT zeros is an explicit assumption, not a confirmed
  instruction. Task 2k remains open for course confirmation, despite documented masks.
- The best window setting changes when black borders are counted. Retained all
  metric variants rather than presenting a masked score as a whole-image score.
- The final report, fish stereo, and complete-workflow verification remain unfinished.

## 08 — Trying three independent Teddy refinements
Date: 2026-11-03
TODO items covered: optional improvements related to 2f–2j and 4h; 2k still open.

### What was tried
- Compared 3×3 median filtering, left/right consistency plus row filling, and
  10% uniqueness filtering plus the same row filling against the unchanged (7,9) baseline.
- Fixed parameters before evaluating ground truth; used identical evaluation masks
  across predictions and kept rejected/filled pixels in every denominator.
- Ran the existing stereo checks and added synthetic refinement checks. Inspected
  all three resulting disparity views.

### What worked
- All three methods reduced error. Shared-interior rates were 11.6175% baseline,
  11.4453% median, 8.6756% consistency/fill, and 10.1568% uniqueness/fill.
- Full-image rates were 24.5031%, 24.3674%, 20.5055%, and 23.3920% respectively.
- Consistency/fill was strongest: about 25.3% fewer shared-interior bad pixels.
  It retained 93.85% of interior matches before filling; the final score still
  includes all 131,311 interior evaluation pixels.
- Recorded methods, parameters, denominators, and limitations in
  [results/teddy_improvements.md](results/teddy_improvements.md). Saved separate
  experimental images, trust masks, and counts in `output/teddy_improvements/`.
- Preserved the required unfiltered outputs and original matching implementation.

### What did not work
- A new small-image uniqueness test exposed a loop that searched beyond the
  image width and raised a broadcasting error. Added the complete-window bound
  and reran the experiment successfully.
- Median filtering provided only a small gain. Row filling introduced horizontal
  streaks and can erase thin foreground detail; visual cleanliness is not proof
  of correct depth everywhere.
- These gains were measured on Teddy only and do not establish performance on
  unseen data. They are optional additions, not the required plain WTA comparison.
- Course evaluation-mask conventions remain unconfirmed; no task was marked
  complete solely on the basis of a lower masked score.

## 09 — Keeping the best refinement active
Date: 2026-11-03
TODO items covered: refinement cleanup related to 2f–2j; documentation maintenance.

### What was tried
- Simplified the refinement script to run left/right consistency plus filling only.
- Kept the median and uniqueness implementations, imports, invocation examples,
  and uniqueness checks as comments with their measured outcomes.
- Replaced the multi-variant loop with one prediction and updated README and results notes.

### What worked
- Active synthetic checks passed. The best-only run reproduced 11,392 bad interior
  pixels (8.6756%) and 34,603 full-image bad pixels (20.5055%), unchanged from the comparison.
- New runs save `best_metrics.json`, leaving the earlier `metrics.json` comparison intact.
- The required unfiltered homework runner remains separate and unchanged.
- Journal entry 08 already recorded all three experiments; this entry records their cleanup.

### What did not work
- No new failures occurred. Commented attempts do not execute unless deliberately
  restored along with their commented imports.
- Previously documented row-filling artifacts and evaluation-mask uncertainty remain.

## 10 — Rendering and matching the fish stereo pair
Date: 2026-11-03
TODO items covered: 3a–3l, 4f–4g, partial 4h. Task 3b remains open for confirmation.

### What was tried
- Implemented calibration scaling in the CPU renderer and original starter.
- Added [the fish runner](scripts/run_fish.py) with configurable scale and baseline.
  Used scale 0.5 (quarter total pixels), shared intrinsics, parallel axes, and
  camera centers (0,0,0) and (0.12,0,0) in scene units.
- Chose baseline from scene depth and a target maximum disparity near 43 pixels;
  searched 0–44 with the unfiltered Problem 1 matcher for all four window settings.
- Checked known-point geometry, calibration scaling, RGB order, and grayscale
  weights, and inspected both RGB views and the (3,9) disparity display.

### What worked
- [Geometry checks](scripts/check_fish_geometry.py) passed, including scale 0.5
  and 0.25, field of view, unchanged source K, rectification, sign, and RGB weights.
- Rendered the 1536 × 1024 stereo pair without maximum filtering or hole filling.
  Sampled vertical projections matched exactly. Expected disparities were
  17.1456–42.8241 pixels for scene depths 3.8663–9.6567.
- Ran all four configurations in about 33.5 seconds including rendering. The
  warning-free rerun reproduced the first run's counts exactly.
- Against the depth-derived diagnostic reference, errors on the same 1,379,716
  masked pixels were 0.7700%, 0.2253%, 0.3017%, 0.2886% for (3,5), (3,9), (7,5), (7,9).
- Saved RGB/grayscale pairs, masks, raw/display disparities, depth/reference arrays,
  and metrics under `output/fish/scale_0.5_baseline_0.12/`. Documented geometry and
  limitations in [results/fish.md](results/fish.md) and execution in README.

### What did not work
- First-run visibility checking subtracted infinite depth entries and produced a
  runtime warning. Restricted subtraction to finite candidates, then reran with
  warnings treated as errors; the rerun passed.
- The point cloud cannot render previously hidden surfaces, leaving holes beside
  the fish and other depth edges. These remain visible and unfilled.
- The reference comes from the same renderer's depth, uses a visibility mask, and
  is not independent ground truth or comparable to Teddy's whole-image error.
- The handout's resolution wording remains ambiguous. Quarter total pixels is a
  documented assumption; the alternate scale is configurable but was not run on
  the real scene this session. Task 3b stays open.
- Full individual artifact review, the final report, and submission remain unfinished.

## 11 — Reconciling the checklist with completed work
Date: 2026-11-03
TODO items covered: 4h, 5a–5d; reviewed remaining status in 2k, 3b, 4i, 5e–5i, and section 6.

### What was tried
- Compared the checklist with the existing report, recorded image checks, and
  prior visual review. The checklist had remained unchanged during the earlier
  request to leave Markdown files untouched.
- Updated the stale status descriptions and README's completion wording.

### What worked
- Confirmed `output/pdf/homework2_report.pdf` exists. The previously reviewed
  five-page report has one explanatory page and four figure pages containing
  the required Teddy and fish results. Marked 5a–5d complete.
- The previous PDF-page review covered all census/stereo/disparity figures;
  `output/report_review.json` records additional checks of 36 output images.
  Marked 4h complete using that existing evidence, not a newly claimed run.
- Updated next steps to complete workflow verification, resolve course conventions,
  and build and review the submission package.

### What did not work
- Checklist status had fallen behind the implementation and report work. This
  entry reconciles that history; it does not claim those stages ran this session.
- The assignment remains unfinished: 2k and 3b await confirmation, 4i has no single
  complete-run verification, and 5e–5i await packaging, review, and submission.
- PDF review alone does not complete 5h because the packaged files do not yet
  exist. The optional bonus remains unimplemented. No upload was performed.

## 12 — Verifying the workflow and preparing the submission ZIP
Date: 2026-11-03
TODO items covered: 4i, 5e–5h; course confirmation and 5i handed back to the student.

### What was tried
- Added `scripts/verify_workflow.py` to run all eight documented stages in order
  with per-stage logs and a machine-readable result file.
- Rebuilt the PDF and rendered all pages; compared them with the reviewed page images.
- Added `scripts/package_submission.py` and built the local ZIP with source,
  trusted inputs, separate output directories, report, run instructions, and hashes.
- Extracted the ZIP and reran the entire workflow using the existing Python
  environment, then compared numerical metrics with the repository results.

### What worked
- Both complete runs passed all eight stages. The extracted copy reproduced
  Teddy, refinement, and fish numerical metrics exactly, excluding runtimes.
- All five rebuilt report pages matched the reviewed renderings pixel for pixel.
- Created `output/submission/homework2_submission.zip`: about 142.5 MiB, with
  85 hashed files plus the manifest. CRC, hashes, and image decoding passed.
  No installed environments, caches, or machine clutter were included.
- Marked 4i, 5e, 5g, and 5h complete. Source and output directories satisfy the
  local portion of 5f; its Canvas-organization confirmation remains open.
- Evidence is under `output/verification/`, including `workflow.json`, stage logs,
  and `package_check.json`. Updated README and TODO to reflect the actual handoff.

### What did not work
- Browser access was unavailable and native Chrome inspection timed out. Before
  the student asked to handle external checks personally, a connected email search
  found no matching course clarification. No messages were sent or files uploaded.
- Per the student's instruction, further course and Canvas checking stopped.
  Tasks 2k, 3b, the Canvas portion of 5f, and 5i remain for the student.
- The extracted verification reused the installed environment; it does not prove
  dependency installation on a different machine. Physical units and course
  assumptions remain documented, not independently confirmed.
- Student identification is not filled into the report. Add it if the course
  requires it. No bonus or video is included; the required stereo results are images.

## 13 — Completing the plane and homography bonus
Date: 2026-11-03
TODO items covered: 6a–6k; extended verification and refreshed bonus-inclusive packaging.

### What was tried
- Implemented three-point SVD plane hypotheses, RANSAC consensus scoring, covariance
  refinement, and sequential inlier removal in `src/planes.py` and `scripts/run_bonus.py`.
- Used threshold 0.025 scene units, seed 532, 30,000 sampled remaining points,
  adaptive confidence target 0.999, and a 2,000-trial cap.
- Selected the ground by orientation/position and confirmed it in the green render.
- Positioned a bird's-eye camera along the ground normal, rendered both poses,
  derived H from n.X+d=0, and implemented inverse bilinear warping manually.
- Ran synthetic checks, deterministic reruns, all eleven extended-workflow stages,
  rendered and reviewed the separate bonus PDF, and verified the packaged bonus.

### What worked
- Three planes had 2,356,913, 854,217, and 407,538 inliers. The second is the floor.
  Green renders show the wall, ground, and fountain-facade consensus with previous
  planes removed. Ground n=(0.00463422,-0.99871259,0.05051415), d=1.58323646.
- The second camera looks along -n from 8.93276 scene units above a ground target.
  Image B and warped A are saved separately and side by side under `output/bonus/`.
- Exact on-plane points agreed between H and direct projection within 3.84e-13 pixels.
  Tests passed for exact/noisy planes, outliers, degenerate samples, proper rotations,
  homography sign, and identity/translated/half-pixel interpolation examples.
- All eleven stages of `scripts/verify_workflow.py --bonus` passed. The three-page
  `output/pdf/homework2_bonus.pdf` was rendered and visually reviewed. The required
  report is unchanged; all explanation for the bonus is on its own first page.
- Created `output/submission/homework2_submission_with_bonus.zip` (147.8 MiB).
  CRC, 104 hashes, and image decoding passed. An extracted copy reran all three
  bonus commands and reproduced exact parameters and PNG bytes. Verification is
  recorded in `output/verification/bonus_package_check.json`.
- Checked all section 6 items, added the bonus explanation and images to README,
  and recorded details in `results/bonus.md`. Preserved the required-only archive.

### What did not work
- The bird's-eye render contains large holes and sparse surfaces because the
  single-view cloud lacks newly visible geometry. No invented geometry or hole
  filling was used to disguise this limitation.
- The ground homography stretches the raised fountain onto the floor. It cannot
  reproduce off-plane parallax, object height, or visibility changes. The comparison
  documents this expected limitation rather than claiming whole-image agreement.
- RANSAC's confidence target is a sampling heuristic subject to a trial cap and
  the chosen threshold; it is not proof that a visually meaningful plane was found.
- No new runtime/test failures occurred. Course conventions and Canvas submission
  remain with the student; no external checking or upload was performed.
