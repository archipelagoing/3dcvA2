# Fish stereo

Run from the repository root:

```sh
.venv/bin/python scripts/check_fish_geometry.py
.venv/bin/python scripts/run_fish.py
```

Outputs: `output/fish/scale_0.5_baseline_0.12/`.

## Resolution and calibration

The default interprets “¼ resolution” as **one quarter of the pixel count**:
3072 × 2048 becomes 1536 × 1024, with linear scale 0.5. The handout does not
explicitly resolve this wording; confirm the interpretation before submission.
For quarter width and height instead, run `scripts/run_fish.py --scale 0.25`;
that option is available but this session evaluated only scale 0.5.

Scale the first two rows of K, including focal lengths and principal point:

```text
K = [[1379.75,    0,    760.35],
     [   0,   1382.10,  503.40],
     [   0,      0,      1   ]]
```

Scaling width/fx, height/fy, and normalized principal-point coordinates equally
preserves horizontal and vertical field of view. Checks also verify scaled
projections and that the input K is unchanged. `scale_intrinsics()` is implemented
in the CPU renderer and the original Open3D starter; the latter remains unsupported
on this Mac and is not the execution path used here.

## Camera geometry and search range

Both cameras have R=I and share the same K. Left center is `(0,0,0)`, right center
is `(0.12,0,0)` in scene units. With `Xcamera = R Xworld + t`, their translations
are `(0,0,0)` and `(-0.12,0,0)`. There is no dolly zoom or focal-length change.

The baseline was chosen to keep the near object around 43 disparity pixels while
limiting viewpoint change and newly uncovered holes. With the observed nearest
Z of 3.8663, a target maximum disparity near 43 implies B≈0.1205; use B=0.12.
All lengths use the same unconfirmed scene units; no physical metre claim is made.

Using `d = fx * B / Z` and `fx * B = 165.57`:

- Scene depth range: 3.8663–9.6567 scene units.
- Geometric disparity range: 17.1456–42.8241 pixels.
- Search: integer disparities 0–44, with an extra pixel above ceil(maximum).
- Positive continuous disparity up to 44 covers depths from 3.7630 toward infinity.
  Disparity 1 corresponds to depth 165.57; disparity 0 represents the infinite-depth
  limit. Integer estimates also include quantization around each disparity.

Both vertical projections match exactly for sampled points; horizontal displacement
agrees with `fx * B / Z` and has the correct positive left-minus-right sign.
The left camera projects a point at Z=4 with displacement 41.3925 pixels relative
to the right camera. The ray geometry, not observed error rates, determined B.

## Rendering and matching

The CPU point renderer keeps the nearest visible positive-depth point per pixel.
It performs no maximum filter, interpolation, or hole filling. Empty pixels stay
black. Saved RGB PNGs are read back to verify channel order before grayscale:
`gray = round(0.30 R + 0.59 G + 0.11 B)`.

The same unfiltered census/Hamming/window-sum/WTA method as Problem 1 runs for
all four required window combinations. Teddy's optional postprocessing is not
applied. Save raw uint16 disparity PNGs and separately scaled display PNGs.

## Diagnostic results

A reference disparity is computed from the rendered left depth buffer, not from
matching intensities. This is a renderer-derived consistency check, not independent
measured ground truth or a directly comparable Teddy score.

The diagnostic mask requires finite left and corresponding right depth, agreement
within 1% of left depth after nearest-pixel correspondence, and a common complete
search interior. It includes 1,379,716 pixels for every setting. Pixel error >1
is bad, using the continuous geometric reference without rounding.

| Wc | WA | Bad pixels | Diagnostic error, % |
| --- | --- | ---: | ---: |
| 3 | 5 | 10,624 | 0.7700 |
| 3 | 9 | 3,108 | 0.2253 |
| 7 | 5 | 4,163 | 0.3017 |
| 7 | 9 | 3,982 | 0.2886 |

Finite rendered coverage: 1,461,612 left pixels and 1,435,731 right pixels out of
1,572,864. Correspondence masking excludes holes and many occlusions; this is not
whole-image accuracy. Shared source colors and geometry make this synthetic pair
much easier than independently photographed Teddy views.

## Files and visual review

- `left_rgb.png`, `right_rgb.png`, `left_gray.png`, `right_gray.png`.
- Render masks, matching validity masks, and the diagnostic evaluation mask.
- `disparity_wc*_wa*.png` and `disparity_view_wc*_wa*.png` for all four settings.
- `left_depth.npy`, `reference_disparity.npy`, and exact geometry/results in `metrics.json`.

The RGB pair and the (3,9) display map were inspected. The foreground fish has
higher disparity than the distant wall. Holes at newly exposed edges are expected:
the original cloud cannot supply surfaces hidden in its source view. Remaining
errors cluster around those holes and boundaries. Not all saved artifacts have
received individual visual inspection yet.

## Checks and limitations

Geometry checks passed for scale 0.5 and 0.25, field of view, rectification,
disparity sign, RGB weights, and invalid scales. The actual run asserts the same
rectification/scaling properties and checks saved RGB images exactly. The first
run exposed a warning from subtracting infinite depth entries; visibility checking
was changed to compare finite depths only, then rerun with warnings treated as errors.

Course confirmation of resolution wording is still pending. This document contains
the material for the fish report section, not the final submitted report.
