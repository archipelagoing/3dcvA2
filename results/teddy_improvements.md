# Three Teddy refinement experiments

Run `.venv/bin/python scripts/try_teddy_improvements.py` from the repository root.
The script now checks and runs only the best refinement: left/right consistency
plus filling. Median and uniqueness attempts are retained as commented code.
The table below preserves the earlier independent comparison. Original homework outputs remain
in `output/teddy/`; experimental outputs go to `output/teddy_improvements/`.

Parameters below were fixed before reading ground truth. This is an exploratory
comparison on Teddy, not evidence of improvement on an unseen stereo pair.

## What was tried

1. **3×3 median filter:** replace each baseline disparity with its neighborhood
   median. Restore the original invalid border to zero.
2. **Left/right consistency plus filling:** compute a right-to-left disparity map
   by mirroring both images and swapping their roles. Keep a left disparity only
   if its corresponding right pixel is valid and agrees within one disparity.
   Fill rejected pixels using the smaller disparity from their nearest trusted
   left/right neighbors in the same row. This favors background at occlusions.
3. **Uniqueness plus filling:** require the chosen cost to be at least 10% better
   than every competing cost outside its immediate ±1 disparity neighborhood.
   In code, reject when `alternative <= 1.10 * best`. Fill rejected matches with
   the same row-based rule used in experiment 2.

At row ends, filling uses the single available trusted neighbor. A row with no
trusted pixels retains its baseline values. None of the methods fills the original
invalid outer border. Methods 2 and 3 are filter-and-fill pipelines, not filters alone.

## Results

All methods are evaluated on the **same masks and denominators**. Rejected pixels
are filled and remain in the error calculation; no method improves its score by
excluding its rejected predictions.

| Method | Shared interior error, % | Valid output + nonzero GT error, % | Full-image error, % | Interior retained before filling, % |
| --- | ---: | ---: | ---: | ---: |
| Baseline (7,9) | 11.6175 | 17.2949 | 24.5031 | 100.00 |
| Median 3×3 | 11.4453 | 17.1449 | 24.3674 | 100.00 |
| Left/right check + fill | **8.6756** | **12.9041** | **20.5055** | 93.85 |
| Uniqueness + fill | 10.1568 | 16.0852 | 23.3920 | 92.20 |

Denominators: 131,311 shared-interior pixels, 154,005 valid-output/nonzero-GT
pixels, and 168,750 full-image pixels. See [baseline results](teddy.md) for mask
and rounding conventions. Exact comparison counts are in the original `metrics.json`. New best-only runs
write `best_metrics.json` so that comparison is not overwritten.

The strongest improvement is left/right checking plus filling: 2.9419 percentage
points, or about 25.3% fewer bad pixels, on the shared interior. It also improves
the full-image score by 3.9976 percentage points. Median filtering alone helps
slightly; it cannot reliably repair larger incorrect regions.

## Inspection and limitations

All three saved disparity views were inspected. Consistency checking and filling
clean up much of the speckle and the noisy left region. Row filling produces
horizontal streaks in some areas and can replace thin foreground details with
background. Uniqueness filtering leaves more incorrect regions than the
consistency method. Median filtering slightly smooths boundaries.

Keep these results separate from the required plain winner-take-all parameter
comparison. These extra operations are not explicitly requested by the handout.
Evaluation-mask confirmation remains open, and physical occlusions cannot be
fully resolved with local matching alone.

## Checks

The original `scripts/check_stereo.py` passed unchanged. The experimental script
also checks filling against a hand-computed row, preservation of rows with no
trusted matches, correspondence direction and threshold, and reverse matching
and uniqueness on a known shifted random image. A small-image test exposed a
uniqueness-loop bounds error; stopping when no complete window can fit fixed it.
