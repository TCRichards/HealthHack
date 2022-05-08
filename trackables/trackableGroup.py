from trackables.trackables.trackable import Trackable
import numpy as np
import pandas as pd


# Class wrapping a collection of trackables for running statistical tests
# For now, groups can only contain 1 or 2 trackables
class TrackableGroup:

    def __init__(self, dependentT, independentT=None):
        # Store one dependent trackable at a time
        self.dependentT = dependentT

        # Independent trackables may be None if only a single Trackable is stored
        self.independentT = independentT

        # Use these fields to determine when cached results are valid
        self.frequency = None
        self.grouping = None
        self.lastDateRange = None
        self.lastFillStrats = None

    # @brief This is the meat and potatoes function where a trackable with correct properties is computed for analysis
    def updateCalculation(self, freq, groupMethods, fillStrats, dateRange, useCache=False):
        if len(self.getTrackables()) > 1:
            Trackable.alignDatesTrimming(self.getTrackables())

        sameDates = self.lastDateRange is not None and len(self.lastDateRange) == len(dateRange) and np.all(self.lastDateRange == dateRange)
        if useCache and sameDates and freq == self.frequency and groupMethods == self.grouping and fillStrats == self.lastFillStrats:
            return

        self.frequency = freq
        self.grouping = groupMethods
        self.lastDateRange = dateRange
        self.lastFillStrats = fillStrats

        # Use the appropriate fill strategy from the list for each trackable
        for t in self.getTrackables():
            # Single Tracakble
            if self.independentT is None:
                strat = fillStrats[0]
                group = groupMethods[0]
            elif t == self.independentT:
                strat = fillStrats[1]
                group = groupMethods[1]
            else:
                strat = fillStrats[2]
                group = groupMethods[2]

            t.updateCalculation(freq, group, strat, dateRange)

    # Returns all of the associated trackables without preference for order
    def getTrackables(self):
        if self.independentT is None:
            return [self.dependentT]
        return [self.dependentT, self.independentT]

    # Convsider a group invalid if there are no overlap in dates -- since this is called after
    # aligning dates, equivalent to zero range
    def isValid(self):
        return all([len(t.getProcessedScores()) != 0 for t in self.getTrackables()])

    # If there is more than 1 trackable in this group, returns the date range that corresponds to their overlap
    def getBoundsForDateRange(self):
        lowDate = max([t.rawData.index[0] for t in self.getTrackables()])
        highDate = min([t.rawData.index[-1] for t in self.getTrackables()])
        return pd.date_range(start=lowDate, end=highDate)
