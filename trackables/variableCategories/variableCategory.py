from abc import ABC, abstractmethod


class VariableCategory(ABC):

    def __init__(self):
        pass

    @abstractmethod
    def getTrackType(self):
        ...

    @abstractmethod
    def getMeanForData(self, data):
        ...

    @abstractmethod
    def getStdevForData(self, data):
        ...
    
    @abstractmethod
    def getMeanStrForData(self, data):
        ...

    @abstractmethod
    def getStdevStrForData(self, data):
        ...

    def getMeanOverDateRange(self, pdDateRange):
        return self.getMeanForData(self.processedData.loc[pdDateRange[0]:pdDateRange[-1]]['Score'])

    def getStdevOverDateRange(self, pdDateRange):
        return self.getStdevForData(self.processedData.loc[pdDateRange[0]:pdDateRange[-1]]['Score'])

    def getCurrentMean(self):
        return self.getMeanOverDateRange(self.currentDateRange)

    def getCurrentStdev(self):
        return self.getStdevOverDateRange(self.currentDateRange)

    def getMeanStrOverDateRange(self, pdDateRange):
        return self.getMeanStrForData(self.processedData.loc[pdDateRange[0]:pdDateRange[-1]]['Score'])

    def getStdevStrOverDateRange(self, pdDateRange):
        return self.getStdevStrForData(self.processedData.loc[pdDateRange[0]:pdDateRange[-1]]['Score'])

    def getCurrentMeanStr(self):
        return self.getMeanStrOverDateRange(self.currentDateRange)

    def getCurrentStdevStr(self):
        return self.getStdevStrOverDateRange(self.currentDateRange)
