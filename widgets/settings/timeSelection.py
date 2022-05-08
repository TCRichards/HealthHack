from enum import Enum


class logTime(Enum):
    DATE = 1,
    DATE_AND_TIME = 2

    @staticmethod
    def maplogTimeToEnum(timeStr):
        timeMap = {'Track Date Only': logTime.DATE,
                   'Track Date and Time': logTime.DATE_AND_TIME}
        return timeMap[timeStr]

    def toString(self):
        if self == logTime.DATE:
            return 'Track Date Only'
        elif self == logTime.DATE_AND_TIME:
            return 'Track Date and Time'
