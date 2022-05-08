from enum import Enum


# Enum describing how to collect data points for points for display and analysis
class Frequency(Enum):
    DAILY = 1
    WEEKLY = 2
    MONTHLY = 3
    YEARLY = 4

    @staticmethod
    def mapFreqStringToEnum(freqStr):
        freqMap = {'Daily': Frequency.DAILY,
                   'Weekly': Frequency.WEEKLY,
                   'Monthly': Frequency.MONTHLY}
        return freqMap[freqStr]

    @staticmethod
    def list():
        return [Frequency.DAILY, Frequency.WEEKLY, Frequency.MONTHLY]

    def toString(self):
        if self == Frequency.DAILY:
            return 'Daily'
        if self == Frequency.WEEKLY:
            return 'Weekly'
        else:
            return 'Monthly'

    def toQuantity(self):
        if self == Frequency.DAILY:
            return 'Days'
        if self == Frequency.WEEKLY:
            return 'Weeks'
        else:
            return 'Months'


# Enum describing what method to use when grouping multiple data points together
# for trackables with WEEKLY or MONTHLY frequency
class GroupingMethod(Enum):
    AVERAGE = 1
    SUM = 2

    @staticmethod
    def mapGroupingStringToEnum(groupStr):
        groupMap = {'Sum Values': GroupingMethod.SUM,
                    'Average Values': GroupingMethod.AVERAGE}
        return groupMap[groupStr]

    @staticmethod
    def getDefaultGroupingMethods():
        return [GroupingMethod.AVERAGE, GroupingMethod.SUM]

    @staticmethod
    def getTimeGroupingMethods():
        return [GroupingMethod.AVERAGE]

    def toString(self):
        if self == GroupingMethod.SUM:
            return 'Sum Values'
        else:
            return 'Average Values'
