from stats.fillStrategy import FillStrategy
from stats.frequency import Frequency, GroupingMethod

import pandas as pd
import numpy as np
from copy import deepcopy as copy
from abc import ABC

from trackables.variableCategories.trackType import TrackType


class Trackable(ABC):
    def __init__(
        self,
        name,
        df=pd.DataFrame({'Score': []}),
        fillStrategy=FillStrategy.ZEROS,
        frequency=Frequency.DAILY,
    ):
        self.name = name
        # rawData always stays at the finest frequency
        self.rawData = df.dropna()  # Remove all NaN rows
        self.frequency = frequency
        self.grouping = GroupingMethod.AVERAGE
        # fillEmpty is a tuple of the form (Whether or not to fill, with what value to fill)
        self.fillStrategy = fillStrategy
        # Create a separate entry that will store trimmed sections of the data
        self.currentDateRange = pd.date_range(self.rawData.index[0], self.rawData.index[-1]) if len(self.rawData) > 0 else None
        # The last date range that was used when setting frequency
        # Used to determine when cached frequency calculation is valid

        self.processedData = copy(self.rawData)
        # Fills in missing dates and combines entries so dates are unique
        if len(self.getRawScores()) > 0:
            self.combineDuplicateDates()
            self.fillEmptyDates()

    # Raw scores are used internally for maintaining all of the tracked data, even if not used ASAP
    def getRawScores(self):
        return self.rawData["Score"].to_numpy()

    def getRawDates(self):
        return self.rawData.index.to_list()

    # @brief collect the dates for which there is no data
    def getMissingDates(self):
        wholeRange = pd.date_range(self.rawData.index[0], self.rawData.index[-1])
        missing = np.array([])
        for date in wholeRange:
            if date not in self.rawData.index:
                missing = np.append(date, missing)
        return missing[::-1]    # Reverse the array so that it's in ascending order

    # Processed values define the data range that can be accessed from within a trackable group -- stores
    # the limits over which all included trackables overlap
    def getProcessedScores(self):
        return self.processedData["Score"].to_numpy()

    def getProcessedDates(self):
        return self.processedData.index.to_list()

    # Values over the selected dates store the current selection as made from the analyze window's trackDateWidget
    # Used immediately for plotting and analysis
    def getSelectedDateScores(self):
        # To avoid having data at the front of the range getting cut off when grouped, add an offset
        if self.frequency == Frequency.DAILY:
            return self.getScoresOverDateRange(self.currentDateRange)
        elif self.frequency == Frequency.WEEKLY:
            return self.getScoresOverDateRange(
                pd.date_range(start=self.currentDateRange[0] - pd.Timedelta(6, unit='d'), end=self.currentDateRange[-1]))
        elif self.frequency == Frequency.MONTHLY:
            return self.getScoresOverDateRange(
                pd.date_range(start=self.currentDateRange[0] - pd.Timedelta(self.currentDateRange[0].day - 1, unit='d'), end=self.currentDateRange[-1]))

    def getSelectedDates(self):
        if self.frequency == Frequency.DAILY:
            return self.getDatesOverRange(self.currentDateRange)
        elif self.frequency == Frequency.WEEKLY:
            return self.getDatesOverRange(
                pd.date_range(start=self.currentDateRange[0] - pd.Timedelta(7, unit='d'), end=self.currentDateRange[-1]))
        elif self.frequency == Frequency.MONTHLY:
            return self.getDatesOverRange(
                pd.date_range(start=self.currentDateRange[0] - pd.Timedelta(self.currentDateRange[0].day, unit='d'), end=self.currentDateRange[-1]))

    def getDatesOverRange(self, pdDateRange):
        return self.processedData.loc[pdDateRange[0]:pdDateRange[-1]].index.to_numpy()

    def getScoresOverDateRange(self, pdDateRange):
        return self.processedData.loc[pdDateRange[0]:pdDateRange[-1]]['Score'].to_numpy()

    # @brief return true if the processedData in the current date range has any missing data
    # this should only return true when the "Don't Fill" strategy is used to handle missing data
    def selectedRangeHasNaN(self):
        selData = self.processedData.loc[self.currentDateRange[0]:self.currentDateRange[-1]]
        return len(selData[selData["Score"].isna()]) > 0

    # @brief returns true if the trackable contains any missing dates in the range nominalDateRange
    # if nominalDateRange is not provided, we look over the trackable's entire date range
    def hasMissingDates(self, nominalDateRange=None):
        if nominalDateRange is None:
            nominalDateRange = pd.date_range(
                start=self.rawData.index[0], end=self.rawData.index[-1]
            )
            recordedDates = self.rawData.index
        else:
            try:
                recordedDates = self.rawData.loc[nominalDateRange[0]:nominalDateRange[-1]].index
            # If the recorded dates are missing part of the nominal date range (causing KeyError),
            # then it's missing data by definition
            except KeyError:
                return True
        return bool(len(nominalDateRange.difference(recordedDates)))

    def setFillStrategy(self, strat):
        self.fillStrategy = strat

    # ===================== Methods to deal with trackable's dates ==================

    # Takes a list of trackables and shifts each one's date range to match
    # Creating the SMALLEST range of dates allowed -- no new entries are created
    @staticmethod
    def alignDatesTrimming(trackableList):
        # To avoid pointless expansions over empty data after repeated calls, find the first and last NONZERO element
        startDates = []
        endDates = []
        for t in trackableList:
            startDates.append(t.rawData.index[0])
            endDates.append(t.rawData.index[-1])

        # Look only at the smallest nonzero window
        date_range = pd.date_range(max(startDates), min(endDates))

        for t in trackableList:
            t.shiftProcessedDataDates(date_range)

    # Takes a list of trackables and shifts each one's date range to match, creating the LARGEST
    # Range of dates allowed, filling new entries with 0's
    @staticmethod
    def alignDatesExpanding(trackableList):
        # To avoid pointless expansions over empty data after repeatd calls, find the first and last NONZERO element
        startDates = []
        endDates = []
        for t in trackableList:
            nonzeroIdxs = np.nonzero(t.getRawScores())[0]
            startDates.append(t.data.index[nonzeroIdxs[0]])
            endDates.append(t.data.index[nonzeroIdxs[-1]])
        date_range = pd.date_range(min(startDates), max(endDates))

        for t in trackableList:
            t.setFillStrategy(FillStrategy.ZERO)
            t.shiftProcessedDataDates(date_range)

    # Combines entries in the dataframe to enforce unique data identifiers
    def combineDuplicateDates(self):
        if self.getTrackType() == TrackType.TIME:
            return

        df = self.processedData
        # Dataframe with only rows with duplicate dates
        duplicates = df[df.index.duplicated()]
        for duplicate in duplicates.iterrows():
            duplicateDate = duplicate[0]
            # Read the values of each duplicate
            origArr = df.at[duplicateDate, "Score"]
            numDuplicates = len(origArr)
            # Combine all entries into a single row and set all others to 0
            totalCount = np.sum(origArr)
            combinedArr = np.array([totalCount] + ([0] * (numDuplicates - 1)))
            df.at[duplicateDate, "Score"] = combinedArr

        # Removes the duplicate rows
        self.processedData = df.loc[~df.index.duplicated(keep="first")]

    # Do the two trackables' dates overlap at all, or do they occur over disjoint date ranges?
    def overlaps(self, other):
        d1, d2 = self.getRawDates(), other.getRawDates()
        start1, end1 = d1[0], d1[-1]
        start2, end2 = d2[0], d2[-1]
        # Fast, but assumes that the dates are ordered
        return (start1 < start2 and end1 > end2) or (start1 > start2 and end1 < end2)

    # Sets the trackable's currentDateRange property
    # If using weekly grouping, starts the date range on the Monday prior to first measurement
    def setCurrentDateRange(self, startDate, endDate):
        if self.frequency == Frequency.DAILY:
            self.currentDateRange = pd.date_range(startDate, endDate)
        elif self.frequency == Frequency.WEEKLY:
            # Need to count each week from the start (Monday), not end
            # TODO: Check if the last period is cut off because it's not always on a Monday
            daysPastMonday = pd.to_datetime(startDate).dayofweek
            self.currentDateRange = pd.date_range(
                startDate - pd.Timedelta(daysPastMonday, unit="d"),
                endDate,
                freq="W-Mon",
            )
        elif self.frequency == Frequency.MONTHLY:
            # Need to count each month from the beginning, not end
            monthEnds = pd.date_range(startDate, endDate, freq="M")
            # Also need to include the end for the month currently in progress
            daysInLastMonth = pd.Period(
                "{}/{}/{}".format(endDate.month, endDate.day, endDate.year)
            ).days_in_month
            lastDay = pd.to_datetime(
                "{}/{}/{}".format(endDate.month, daysInLastMonth, endDate.year)
            )
            monthEnds = monthEnds.append(pd.DatetimeIndex([lastDay]))
            self.currentDateRange = monthEnds - np.array(
                [pd.Timedelta(end.day - 1, unit="d") for end in monthEnds]
            )

    # Shifts self.processedData to the specified date range and fills missing data using self.fillStrategy
    def shiftProcessedDataDates(self, pdDateRange):
        # Change how we deal with missing data based on selection
        if self.fillStrategy == FillStrategy.NONE:
            self.processedData = self.processedData.reindex(
                pdDateRange, method=None)
        elif self.fillStrategy == FillStrategy.ZEROS:
            self.processedData = self.processedData.reindex(
                pdDateRange, fill_value=0)

        # Filling with the mean or any method that uses 'fill_value' instead of 'method' must be handled different for times
        elif self.fillStrategy == FillStrategy.MEAN_INCLUSIVE or self.fillStrategy == FillStrategy.MEAN_EXCLUSIVE:
            dataInRange = self.getScoresOverDateRange(pdDateRange)
            if self.getTrackType() == TrackType.TIME:
                meanTimeStr = self.getMeanStrOverDateRange(pdDateRange)
                baselineDateStr = self.processedData['Score'][0].date().strftime('%Y/%m/%d ')
                self.processedData = self.processedData.reindex(pdDateRange, fill_value=pd.Timestamp(baselineDateStr + meanTimeStr))

            else:
                # To get the mean over the entire range, not only days with measurements we first need to fill with zeros
                if self.fillStrategy == FillStrategy.MEAN_INCLUSIVE:
                    totalValue = dataInRange.sum()
                    meanValue = totalValue / (pdDateRange[-1] - pdDateRange[0]).days
                    self.processedData = self.processedData.reindex(
                        pdDateRange, fill_value=meanValue)
                else:
                    # Default calculation of mean does not consider missing dates
                    meanValue = self.getMeanOverDateRange(pdDateRange)
                    self.processedData = self.processedData.reindex(
                        pdDateRange, fill_value=meanValue)

        elif self.fillStrategy == FillStrategy.FORWARD:
            self.processedData = self.processedData.reindex(
                pdDateRange, method='ffill')
        elif self.fillStrategy == FillStrategy.BACKWARD:
            self.processedData = self.processedData.reindex(
                pdDateRange, method='bfill')
        else:
            raise ValueError(
                'Attempting to fill values in trackale with invalid strategy {}'.format(self.fillStrategy))

    # @brief Fill processedData with values according to strategy determined by self.fillStrategy
    # Equivalent to shiftProcessedDataDates called over the entire date range
    def fillEmptyDates(self):
        date_range = pd.date_range(
            self.processedData.index[0], self.processedData.index[-1])
        # Reindex to fill in missing dates with 0's
        self.shiftProcessedDataDates(date_range)

    # Sets how many measurements to include for each data point in the analysis
    # @param frequency how often to sample data
    # @param grouping whether to sum or average results
    # @param useCache if True, if the frequency and grouping are unchanged this is a no-op
    # @param clean set to False if self.processedData has already been copied and cleaned from rawData, else do them now
    def updateCalculation(self, frequency, grouping, fillStrat, dateRange):
        self.fillStrategy = fillStrat
        self.processedData = copy(self.rawData)
        if dateRange is not None:
            self.combineDuplicateDates()
            self.shiftProcessedDataDates(dateRange)

        self.setFrequency(frequency, grouping)

    def setFrequency(self, frequency, grouping):
        self.frequency = frequency
        self.grouping = grouping
        if frequency == Frequency.DAILY:
            pass
        elif frequency == Frequency.WEEKLY:
            self.processedData = self.getWeeklyData(grouping=grouping)
        elif frequency == Frequency.MONTHLY:
            self.processedData = self.getMonthlyData(grouping=grouping)

    # Perform a running average over each week and returns a new dataframe
    # With these values
    # The resulting data is grouped by weeks starting on Monday.  I add padding so that the displayed mean and sum
    # values for the first and last week are correct
    # It's the caller's responsibility to set processedData to rawData and clean it first
    def getWeeklyData(self, grouping=GroupingMethod.AVERAGE):
        df = pd.DataFrame()
        daysPastMonday = self.processedData.index[0].dayofweek
        dataToSample = copy(self.processedData)

        padDates = pd.date_range(start=(dataToSample.index[0] - pd.Timedelta(daysPastMonday, unit='d')),
                                 end=dataToSample.index[0] - pd.Timedelta(1, unit='d'))

        # Need to pre-pad data with average value to not change average
        if daysPastMonday > 0:
            firstWeekAvg = self.getMeanOverDateRange(pd.date_range(dataToSample.index[0], dataToSample.index[7 - daysPastMonday]))
            padValue = firstWeekAvg if grouping == GroupingMethod.AVERAGE else 0
            padding = pd.DataFrame(
                data={'Score': [padValue] * len(padDates)}, index=padDates)
            dataToSample = pd.concat([padding, dataToSample])

        # The first of each month included in the range
        results = []
        weekFirsts = pd.date_range(
            start=dataToSample.index[0], end=dataToSample.index[-1], freq='7D')
        for first in weekFirsts:
            last = first + pd.Timedelta(6, unit='d')
            dataInWeek = dataToSample.loc[first:last]
            if grouping == GroupingMethod.AVERAGE:
                results.append(self.getMeanForData(dataInWeek['Score']))
            else:
                results.append(np.sum(dataInWeek['Score']))

        df = pd.DataFrame(index=weekFirsts, data={'Score': results})

        # NaNs are being implicitly converted to zeros, which is a bug.
        # Manually replace any entries that contained a NaN with NaN
        nanDates = dataToSample[np.isnan(dataToSample['Score'])].index
        # First Monday of each week
        for date in df.index:
            thisWeek = pd.date_range(date, date + pd.to_timedelta(6, unit='d'))
            if np.any([n in thisWeek for n in nanDates]):
                df['Score'].loc[date] = np.nan

        # Dates after end of range are represented by NaNs followed by a single value
        # df = df.dropna()

        # NaNs are being implicitly converted to zeros, which is a bug.
        # This only matters when "Don't Fill" is the grouping strategy
        # Manually replace any entries that contained a NaN with NaN
        nanDates = dataToSample[np.isnan(dataToSample['Score'])].index
        # First Monday of each week
        for date in df.index:
            thisWeek = pd.date_range(date, date + pd.to_timedelta(6, unit='d'))
            if np.any([n in thisWeek for n in nanDates]):
                df['Score'].loc[date] = np.nan

        # Merge the last two elements if the last one is there by error
        try:
            if df.index[-1] - df.index[-2] > pd.to_timedelta(7, unit='d'):
                df['Score'][-2] += df['Score'][-1]
                df = df.drop(df.index[-1])
        except IndexError:
            pass

        return df

    def getMonthlyData(self, grouping=GroupingMethod.AVERAGE):
        df = pd.DataFrame()
        firstDayOfMonth = self.processedData.index[0].day
        dataToSample = copy(self.processedData)

        padDates = pd.date_range(start=(dataToSample.index[0] - pd.Timedelta(firstDayOfMonth - 1, unit='d')),
                                 end=dataToSample.index[0] - pd.Timedelta(1, unit='d'))

        # Need to pre-pad data with average value to not change average
        if firstDayOfMonth > 0:
            firstMonthDf = dataToSample[(
                dataToSample.index.month == dataToSample.index[0].month)]
            padValue = np.mean(firstMonthDf['Score']) if grouping == GroupingMethod.AVERAGE else 0
            padding = pd.DataFrame(
                data={'Score': [padValue] * len(padDates)}, index=padDates)
            dataToSample = pd.concat([padding, dataToSample])

        results = []
        monthFirsts = pd.date_range(
            start=dataToSample.index[0], end=dataToSample.index[-1], freq='MS')
        for first in monthFirsts:
            last = first + pd.Timedelta(first.days_in_month - 1, unit='d')
            dataInMonth = dataToSample.loc[first:last]
            if grouping == GroupingMethod.AVERAGE:
                results.append(self.getMeanForData(dataInMonth['Score']))
            else:
                results.append(np.sum(dataInMonth['Score']))
        df = pd.DataFrame(index=monthFirsts, data={'Score': results})

        # NaNs are being implicitly converted to zeros, which is a bug.
        # This only matters when "Don't Fill" is the grouping strategy
        # Manually replace any entries that contained a NaN with NaN
        nanDates = dataToSample[np.isnan(dataToSample['Score'])].index
        # First day of each month
        for date in df.index:
            thisMonth = pd.date_range(date, date + pd.to_timedelta(date.daysinmonth - 1, unit='d'))
            if np.any([n in thisMonth for n in nanDates]):
                df['Score'].loc[date] = np.nan

        return df

    def isAnalyzable(self):
        return len(self.getProcessedScores()) > 2

    # @brief adds the new entry to the existing trackable
    # @param value to be added in 'Score' field
    # @param date string in format %m/%d/%Y to add
    # @param time to add, can be None or a string in '%HH:%MM' format
    def addEntry(self, value, date, time):
        date = pd.to_datetime(date, format="%m/%d/%Y")
        if time is None:
            newEntry = pd.DataFrame({"Date": [date], "Score": [value]})
        else:
            time = pd.to_datetime(time, format="%H:%M").time()
            newEntry = pd.DataFrame({"Date": [date], "Time": [time], "Score": [value]})
        newEntry = newEntry.set_index("Date")
        self.rawData = self.rawData.append(newEntry, sort=True)
        self.processedData = copy(self.rawData)

        # Fills in missing dates and combines entries so dates are unique
        if len(self.getRawScores()) > 0:
            self.combineDuplicateDates()
            self.fillEmptyDates()
