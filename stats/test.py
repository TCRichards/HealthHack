from abc import abstractmethod, ABC
from trackables.trackableGroup import TrackableGroup


class Test(ABC):

    def __init__(self, testName, displayName, isSymmetric):
        self.name = testName
        self.displayName = displayName
        self.isSymmetric = isSymmetric

    @abstractmethod
    # @return a single r^2 and p-value
    def runValidTestForLag(self, dependentT, independentT, lag=1):
        ...

    # Loudly fail if data is passed to test in bad format
    def runTestForLag(self, dependentT, independentT, lag=1):
        depScores = dependentT.getProcessedScores()
        indepScores = independentT.getProcessedScores()
        assert(not isinstance(depScores[0], str) and not isinstance(
            indepScores[0], str))
        assert(TrackableGroup(dependentT, independentT).isValid())
        return self.runValidTestForLag(dependentT, independentT, lag=lag)

    # @return a tuple containing a list of r^2 and a list of p-values for each lag tested
    # Default implementation is to just collect each day's results separately
    def runTestOverRange(self, dependentT, independentT, minLag=0, maxLag=3):
        r2_s, p_s = [], []
        for lag in range(minLag, maxLag):
            res = self.runTestForLag(dependentT, independentT, lag)
            r2_s.append(res[0])
            p_s.append(res[1])
        return r2_s, p_s

    def isSymmetric(self):
        return self.isSymmetric

    @staticmethod
    def getTestNames():
        return ['Pearson', 'Granger', 'Impact']
