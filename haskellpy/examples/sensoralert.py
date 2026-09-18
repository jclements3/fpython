"""sensoralert.py -- smooth a sensor stream with a 3-wide moving average,
then report each consecutive run of over-threshold readings as (start, len)."""
from haskell import windows, groupBy, enum

READINGS = [10, 11, 30, 32, 31, 12, 9, 40, 41, 10]
THRESHOLD = 20

# --- imperative ---
def alerts_imp(xs, n, threshold):
    smoothed = []
    for i in range(len(xs) - n + 1):
        window = xs[i:i + n]
        smoothed.append(sum(window) / n)
    flags = [v > threshold for v in smoothed]
    runs, i = [], 0
    while i < len(flags):
        if flags[i]:
            start = i
            while i < len(flags) and flags[i]:
                i += 1
            runs.append((start, i - start))
        else:
            i += 1
    return runs

# --- functional ---
def alerts_fn(xs, n, threshold):
    smoothed = [sum(w) / n for w in windows(n, xs)]
    flagged = [(i, v > threshold) for i, v in enum(smoothed)]
    groups = groupBy(lambda a, b: a[1] == b[1], flagged)
    return [(g[0][0], len(g)) for g in groups if g[0][1]]

# --- demo ---
if __name__ == "__main__":
    a, b = alerts_imp(READINGS, 3, THRESHOLD), alerts_fn(READINGS, 3, THRESHOLD)
    assert a == b, (a, b)
    print("alert runs (start, length):", b)
    print("sensoralert: both agree")
