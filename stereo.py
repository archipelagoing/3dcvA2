"""Census-transform stereo matching for rectified grayscale images."""
import numpy as np

# Counting one byte at a time also works on NumPy versions without bitwise_count.
BIT_COUNTS = np.array([value.bit_count() for value in range(256)], dtype=np.uint8)


def census_transform(image, window_size):
    """Encode whether each neighbor is darker than the center (center excluded)."""
    if image.ndim != 2:
        raise ValueError('Expected a grayscale image')
    if window_size < 3 or window_size % 2 == 0 or window_size**2 - 1 > 64:
        raise ValueError('Use an odd census window with at most 64 neighbors')
    height, width = image.shape
    if min(height, width) < window_size:
        raise ValueError('Image is smaller than the census window')
    radius = window_size // 2
    center = image[radius:height-radius, radius:width-radius]
    descriptor = np.zeros(center.shape, dtype=np.uint64)
    for dy in range(-radius, radius + 1):
        for dx in range(-radius, radius + 1):
            if dx == 0 and dy == 0:
                continue
            neighbor = image[radius+dy:height-radius+dy, radius+dx:width-radius+dx]
            descriptor = (descriptor << np.uint64(1)) | (neighbor < center).astype(np.uint64)
    result = np.zeros(image.shape, dtype=np.uint64)
    result[radius:height-radius, radius:width-radius] = descriptor
    return result


def hamming_distance(left, right):
    different_bits = np.ascontiguousarray(left ^ right)
    bytes_per_pixel = different_bits.view(np.uint8).reshape(different_bits.shape + (8,))
    return BIT_COUNTS[bytes_per_pixel].sum(axis=-1, dtype=np.int32)


def census_visualization(descriptors, window_size):
    """Show the number of set bits, mapped from 0..(Wc²-1) to 0..255.

    A descriptor is a bit string, not an intensity. Its distance from an all-zero
    descriptor gives a scalar visualization without discarding most of its bits.
    """
    counts = hamming_distance(descriptors, np.zeros_like(descriptors))
    return np.rint(counts * (255.0 / (window_size**2 - 1))).astype(np.uint8)


def window_sum(values, window_size):
    """Sum complete square windows using an integral image; borders stay zero."""
    radius = window_size // 2
    integral = np.pad(values.astype(np.int64), ((1, 0), (1, 0))).cumsum(0).cumsum(1)
    sums = (integral[window_size:, window_size:] - integral[:-window_size, window_size:]
            - integral[window_size:, :-window_size] + integral[:-window_size, :-window_size])
    result = np.zeros(values.shape, dtype=np.int64)
    result[radius:values.shape[0]-radius, radius:values.shape[1]-radius] = sums
    return result


def match_stereo(left, right, census_size, aggregation_size, max_disparity=63):
    """Return disparity and validity mask. Search x_right = x_left - disparity.

    Every candidate must contain complete census AND aggregation neighborhoods
    in both images. Ties prefer the smaller disparity. Invalid output is zero;
    use the separate mask to distinguish it from a valid zero disparity.
    """
    if left.shape != right.shape or left.ndim != 2:
        raise ValueError('Stereo inputs must be equally sized grayscale images')
    if aggregation_size < 1 or aggregation_size % 2 == 0:
        raise ValueError('Aggregation size must be positive and odd')
    if not 0 <= max_disparity < left.shape[1]:
        raise ValueError('Disparity range must fit inside the image width')
    margin = census_size // 2 + aggregation_size // 2
    height, width = left.shape
    if 2 * margin >= min(height, width):
        raise ValueError('Image is too small for the combined neighborhoods')
    left_census = census_transform(left, census_size)
    right_census = census_transform(right, census_size)
    best_cost = np.full(left.shape, np.iinfo(np.int64).max)
    disparity = np.zeros(left.shape, dtype=np.uint16)
    valid = np.zeros(left.shape, dtype=bool)
    for shift in range(max_disparity + 1):
        if shift + margin >= width - margin:
            break
        cost = np.zeros(left.shape, dtype=np.int32)
        cost[:, shift:] = hamming_distance(left_census[:, shift:], right_census[:, :width-shift])
        total = window_sum(cost, aggregation_size)
        candidate = np.zeros(left.shape, dtype=bool)
        candidate[margin:height-margin, shift+margin:width-margin] = True
        better = candidate & (total < best_cost)
        best_cost[better] = total[better]
        disparity[better] = shift
        valid |= candidate
    return disparity, valid


def bad_pixel_rate(disparity, ground_truth, mask):
    count = int(mask.sum())
    if not count:
        raise ValueError('Evaluation mask contains no pixels')
    bad = int(((np.abs(disparity.astype(float) - ground_truth) > 1) & mask).sum())
    return {'bad_pixels': bad, 'evaluated_pixels': count, 'error_percent': 100.0 * bad / count}
