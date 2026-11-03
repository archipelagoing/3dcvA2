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
cloud. Cloud rows are XYZ followed by normalized RGB. Physical units are unconfirmed.

## Rendering check

```sh
.venv/bin/python scripts/check_renderer.py
```

This independently checks Open3D offscreen rendering with a small synthetic cloud
and saves `output/renderer_check.png`. It does not validate the full fish scene.

The supplied renderer can be invoked from the repository root:

```sh
.venv/bin/python dolly_zoom_fast-1.py
```

It expects `data/data.obj` and writes `SampleOutput0.jpg` through
`SampleOutput39.jpg` plus `dolly_zoom.mp4` in the current directory. The full
sequence has not been validated. `scale_intrinsics()` remains unfinished, and
this script does not yet produce a rectified stereo pair.

## Assignment references

- `cs532f27_hw2 (1).pdf`: main requirements and submission instructions.
- `HW2Bonus-1 (1).pdf`: optional RANSAC and plane-induced homography work.

The main stereo implementation and report are still to be developed.
