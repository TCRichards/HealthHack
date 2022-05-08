from enum import Enum


class LogTime(Enum):
    DATE = 1,
    DATE_AND_TIME = 2

    @staticmethod
    def mapLogTimeToEnum(timeStr):
        timeMap = {'Track Date Only': LogTime.DATE,
                   'Track Date and Time': LogTime.DATE_AND_TIME}
        return timeMap[timeStr]

    def toString(self):
        if self == LogTime.DATE:
            return 'Track Date Only'
        elif self == LogTime.DATE_AND_TIME:
            return 'Track Date and Time'
