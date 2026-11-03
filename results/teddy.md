# Teddy stereo results

Generated with `.venv/bin/python scripts/run_teddy.py` on 2026-11-03.
Disparities searched: 0–63 inclusive. No smoothing or postprocessing was applied.

## Method

For each census window, compare every neighbor with the center using `<`, omit
its center, and pack the comparisons in row-major order into a 64-bit integer.
There are eight bits for Wc=3 and 48 bits for Wc=7. Match a left pixel at x to
right pixel x-d, count differing bits, and sum those costs over the aggregation
window. Choose the minimum-cost disparity; ties use the smallest disparity.

Only candidates with complete census and aggregation neighborhoods in both images
are considered. The combined margin is `Wc//2 + WA//2`. Border pixels with no
candidate are zero. Near the left edge, only disparities with valid right-image
support compete, so the search is truncated there. Saved validity masks distinguish
an invalid zero from a real zero disparity.

Ground truth is `floor(stored_value / 4 + 0.5)`: nearest-integer rounding with
half-integers rounded upward. A pixel is bad only when absolute error is greater
than one. An error of exactly one is acceptable.

## Error rates

| Wc | WA | Full image, % | Valid output and nonzero GT, % | Shared interior and nonzero GT, % |
| --- | --- | ---: | ---: | ---: |
| 3 | 5 | 27.9911 | 24.2913 | 18.8012 |
| 3 | 9 | 24.4480 | 18.9177 | 13.1459 |
| 7 | 5 | 24.1807 | 18.6372 | 12.8687 |
| 7 | 9 | 24.5031 | 17.2949 | 11.6175 |

- **Full image:** all 168,750 pixels, including black output borders and stored
  ground-truth zeros. This is the literal whole-image calculation without a mask.
- **Valid output and nonzero GT:** exclude output borders with no valid candidate
  and, by explicit evaluation assumption, stored ground-truth zeros. Denominators
  are 160,440; 157,207; 157,207; and 154,005 respectively.
- **Shared interior and nonzero GT:** evaluate the same 131,311 pixels for every
  setting. Use rows `[7,368)` and columns `[70,443)` with stored GT > 0. These
  bounds provide full support for all 64 disparities under all four settings.
  This avoids comparing settings on different pixel populations.

The handout does not explicitly specify an invalid-GT mask or the treatment of
output borders in the error denominator. Excluding ground-truth zeros is an
assumption, not a confirmed course rule. All three calculations are retained;
confirm the intended convention before choosing the report's headline metric.
Raw counts and measured runtimes are in `output/teddy/metrics.json`.

## Census visualizations

Images show the descriptor's Hamming distance from the all-zero descriptor:
its set-bit count. Scale the entire possible range, 0–8 or 0–48, to 0–255 rather
than stretching by each image's observed extrema. Invalid census borders are black.
This is an explicit interpretation of the handout's Hamming-range wording.

The two sizes show similar edges and texture because both summarize the center's
relative brightness within its neighborhood. They are not identical: a 7×7 window
uses more spatial context and has 49 possible counts, whereas 3×3 has only nine.
Set-bit count is only a visualization; matching uses the complete descriptor.
Two descriptors can have equal set-bit counts yet nonzero pairwise Hamming distance.

## Output files and observations

All images are under `output/teddy/` (generated locally, excluded from Git):

- `census_left_wc3.png`, `census_left_wc7.png`, and corresponding right-view images.
- `disparity_wc*_wa*.png`: raw disparity values 0–63.
- `disparity_view_wc*_wa*.png`: display scaling 0–63 to 0–255.
- `valid_wc*_wa*.png` and `common_evaluation_mask.png`: explicit masks.
- `metrics.json`: exact errors, denominators, and runtimes.

Visual review of all four disparity views and both left census images found
recognizable scene structure and the expected black borders. Larger windows
reduce speckle but blur boundaries and mix neighboring depths. Errors remain near
occlusions, repeated texture, and the left edge. The shared-interior metric favors
7×7 census with 9×9 aggregation; the full-image metric favors 7×7 with 5×5 because
larger black borders are penalized. This difference is why the denominator matters.

## Verification

`.venv/bin/python scripts/check_stereo.py` passed hand-computed census bits,
48-bit Hamming counts, integral sums checked against direct summation, identical
and shifted pairs for all four settings, border masks, the error threshold, and
WTA compared with independent nested-loop pixel comparisons on small random images.
These checks establish the implementation's local behavior, not a course-approved
benchmark score or a completed final report.
