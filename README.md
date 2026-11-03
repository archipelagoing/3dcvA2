# 3D Computer Vision — Homework 2

Census-transform stereo matching on Teddy and a rendered fish point-cloud scene.
See [TODO.md](TODO.md) for requirements and progress, and [JOURNAL.md](JOURNAL.md)
for evidence, discoveries, and decisions.

## Environment

The local environment uses Python 3.12 on Intel macOS. From the repository root:

```sh
python3.12 -m venv .venv
.venv/bin/python -m pip install -r requirements.txt
.venv/bin/python -m pip check
```

`requirements.txt` records the full installed environment. Its platform-specific
packages may require adjustment on other operating systems.

## Inputs

- `teddy/teddyL.pgm` and `teddy/teddyR.pgm`: 450 × 375, 8-bit grayscale views.
- `teddy/disp2.pgm`: ground truth, same dimensions; divide by 4 and round for evaluation.
- `teddy 2.zip`: source archive; extract it if the `teddy/` folder is absent.
- `data/data.obj`: local copy of the HW1 fish scene, excluded from version control.
  Recover it from the original HW1 data folder when setting up another checkout.
  This is a Python pickle, not a text mesh file; load only the trusted course input.

The fish input contains five entries: image bounds/size, a two-value window
setting, a 3 × 3 intrinsic matrix, a 6 × N foreground cloud, and a 6 × N background
cloud. Cloud rows are XYZ followed by normalized RGB. Physical units are not
confirmed by the supplied materials: use **scene units** consistently for XYZ,
camera translation, depth, and stereo baseline. Do not assume metres. Disparity
`fx * baseline / Z` is unaffected by a common change of length units.

Run `.venv/bin/python scripts/check_inputs.py` to repeat the input inspection
and three illustrative left/right patch checks. These are not stereo evaluation.

## Rendering check

```sh
.venv/bin/python scripts/check_renderer.py
```

This runs the NumPy CPU renderer adapted from HW1, with no OpenGL dependency.
It checks synthetic occlusion, clipping, translation, and RGB order, then renders
the real scene to `output/fish_setup_check.png` at 3072 × 2048. The PNG is read
back and compared exactly. This command passed on the local Mac; the saved scene
was also inspected visually.

The reusable implementation is `src/pointcloud_renderer.py`. It uses zero-based
image pixels, `Xcamera = R @ Xworld + t`, and `P = K [R | t]`. For camera center C,
`t = -R @ C`. It keeps the nearest positive-depth point at each rounded pixel;
this replaces HW1's input-order overwrite behavior. It leaves empty pixels black
and applies no maximum filter or hole filling. The original viewport offsets of
one pixel are not used by this zero-based renderer.

Open3D 0.19.0 offscreen rendering still fails on this Mac with
`EGL Headless is not supported on this platform`. The original diagnostic is
preserved as `scripts/check_open3d_renderer.py`; it is not required for CPU rendering.
The full dolly-zoom sequence and rectified stereo capture have not been verified.

The original Open3D starter (currently unsupported on this Mac) can be invoked from the repository root:

```sh
.venv/bin/python dolly_zoom_fast-1.py
```

It expects `data/data.obj` and writes `SampleOutput0.jpg` through
`SampleOutput39.jpg` plus `dolly_zoom.mp4` in the current directory. The full
sequence has not been validated. `scale_intrinsics()` is now implemented, but this original
script does not produce a rectified stereo pair. Use the CPU fish runner below.

## Assignment references

- `cs532f27_hw2 (1).pdf`: main requirements and submission instructions.
- `HW2Bonus-1 (1).pdf`: optional RANSAC and plane-induced homography work.

## Teddy stereo

Run from the repository root:

```sh
.venv/bin/python scripts/check_stereo.py
.venv/bin/python scripts/run_teddy.py
```

The first command checks small known examples and an independent brute-force
reference. The second evaluates all four census/aggregation window combinations,
writing images, validity masks, and measured errors into `output/teddy/`.
See [results/teddy.md](results/teddy.md) for results and evaluation assumptions.
The reusable matching code is [src/stereo.py](src/stereo.py).

Run the selected refinement (left/right consistency plus filling):

```sh
.venv/bin/python scripts/try_teddy_improvements.py
```

See [the comparison](results/teddy_improvements.md). Outputs are saved separately
under `output/teddy_improvements/`; the required baseline is preserved. The
median and uniqueness attempts remain commented in the script. New metrics go
to `best_metrics.json`, preserving the earlier comparison.

## Fish stereo

```sh
.venv/bin/python scripts/check_fish_geometry.py
.venv/bin/python scripts/run_fish.py
```

Default output: `output/fish/scale_0.5_baseline_0.12/`. This renders a rectified
1536 × 1024 pair and runs the four unfiltered matching configurations. See
[results/fish.md](results/fish.md) for the baseline, depth limits, calibration,
resolution assumption, and diagnostic results. The default uses quarter total
pixels; `--scale 0.25` selects quarter width/height if required by course guidance.
`--baseline` uses scene units. No maximum filtering is applied.

The final report, full artifact review, and submission remain unfinished.
