from trackables.variableCategories.variableCategory import VariableCategory
from trackables.variableCategories.trackType import TrackType
import numpy as np
import pandas as pd


class TimeVariable(VariableCategory):

    def getTrackType(self):
        return TrackType.TIME

    def shiftOvernightTimes(self, timestamps):
        if len(timestamps) == 0:
            return
        # Count measurements that happen in window from 0-6am as belonging in the previous day
        # so their values be offset by a whole day
        hours = [p.hour for p in timestamps]
        if min(hours) <= 1 and max(hours) >= 23:
            # adjust the dates of the entries on the following day
            for i in range(len(hours)):
                # I could further tune measurements to be 'Morning', 'Night', or 'Any Time'
                if hours[i] <= 6:  # 4:00 is when oura defines a new day, but 6:00 seems reasonable
                    timestamps[i] += pd.Timedelta(1, unit='d')

    def getTimeAsSecondsInDateRange(self, timestamps):
        self.shiftOvernightTimes(timestamps)

        # Calculate mean by converting to seconds and back to datetime
        return [(24 * 3600 * (p.day - 1)) + p.second + (60 * p.minute) + (3600 * p.hour) for p in timestamps]

    def getMeanForData(self, data):
        # Explicitly cast to timestamps to enable analysis (no-op if already timestamp)
        data = [pd.Timestamp(y) for y in data]
        baselineDateStr = min([d.date() for d in data]).strftime('%Y/%m/%d ')
        totalSecs = self.getTimeAsSecondsInDateRange(data)
        meanTotalSecs = np.mean(totalSecs)
        meanHour = int(meanTotalSecs // 3600)
        meanMinute = int((meanTotalSecs - meanHour*3600) // 60)
        meanSecs = int(meanTotalSecs - meanHour*3600 - meanMinute*60)

        timeStr = f'{meanHour:02}:{meanMinute:02}:{meanSecs:02}'
        try:
            return pd.Timestamp(baselineDateStr + timeStr)
        except ValueError:
            print("VALUEERROR")

    def getStdevForData(self, data):
        data = [pd.Timestamp(y) for y in data]
        baselineDateStr = min([d.date() for d in data]).strftime('%Y/%m/%d ')
        totalSecs = self.getTimeAsSecondsInDateRange(data)
        stdevTotalSecs = np.std(totalSecs)
        stdevHour = int(stdevTotalSecs // 3600)
        stdevMinute = int((stdevTotalSecs - stdevHour*3600) // 60)
        stdevSecs = int(stdevTotalSecs - stdevHour*3600 - stdevMinute*60)

        timeStr = f'{stdevHour:02}:{stdevMinute:02}:{stdevSecs:02}'
        return pd.Timestamp(baselineDateStr + timeStr)

    def getMeanStrForData(self, data):
        return self.getMeanForData(data).strftime('%H:%M:%S')

    def getStdevStrForData(self, data):
        return self.getStdevForData(data).strftime('%H:%M:%S')
