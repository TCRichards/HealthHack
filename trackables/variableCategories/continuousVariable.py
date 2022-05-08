from trackables.variableCategories.variableCategory import VariableCategory
from trackables.variableCategories.trackType import TrackType
import numpy as np


class ContinuousVariable(VariableCategory):

    def getTrackType(self):
        return TrackType.CONTINUOUS

    def getMeanForData(self, data):
        return np.mean(data)

    def getStdevForData(self, data):
        return np.std(data)

    def getMeanStrForData(self, data):
        return '{:.2f}'.format(self.getMeanForData(data))

    def getStdevStrForData(self, data):
        return '{:.2f}'.format(self.getStdevForData(data))
        