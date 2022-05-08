from enum import Enum


class TrackType(Enum):
    EMPTY = 0
    CONTINUOUS = 1
    BINARY = 2
    TIME = 3
    DATE = 4
    DURATION = 5  # Used for sleep data that is reported in seconds
    LIST = 6

    # A string that contains one character for each starting five minutes of the sleep period,
    # so that the first period starts from sleep.bedtime.start: - '1' = deep (N3)
    # sleep - '2' = light (N1 or N2) sleep - '3' = REM sleep - '4' = awake
    HYPNOGRAM = 7   # Niche, but hypnograms don't adhere by other analyses

    # Used for hr_5min -- record the average hr in each 5 minute window
    CONTINUOUS_5_MIN_WINDOW = 8
