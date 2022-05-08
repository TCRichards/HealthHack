import numpy as np

from stats.test import Test


# Welltory's heuristic to determine correlation -- counts the number of times that two variables change in the same diretion and looks for extremes
# May not work for binary causes, since these have many days without a change
class ContinuousImpactTest(Test):

    def __init__(self):
        super().__init__('Impact', 'Binary Impact', False)

    def runValidTestForLag(self, dependentT, independentT, lag=1):

        # Tracks the number of times cause and result change in the same direction
        sameCounts = 0
        indData = independentT.getSelectedDateScores()
        depData = dependentT.getSelectedDateScores()

        numTests = len(depData) - lag
        if numTests < 3:
            return (0, 0)

        lastCause = indData[0]
        lastResult = depData[lag]

        for i in range(1, numTests):
            thisCause = indData[i]
            thisResult = depData[i + lag]
            if np.sign(thisCause - lastCause) == np.sign(thisResult - lastResult):
                sameCounts += 1

        sameProb = sameCounts / numTests
        # scale this to -1 for sameProb=0 and +1 for sameProb=1
        correlation = (sameProb - 0.5) * 2
        return correlation, -1


# More useful heuristic for correlation when dealing with causes that have a signification portion of 0's
class BinaryImpactTest(Test):

    def __init__(self):
        super().__init__('Impact', 'Binary Impact', False)

    def runValidTestForLag(self, dependentT, independentT, lag=1):

        # Tracks the direction in which self.dependentT changes when self.independent is 1 vs 0
        zeroCount = 0
        nonzeroCount = 0
        zeroChanges = 0
        nonzeroChanges = 0

        # Select measurements such that the cause happens lagDays days earlier than the result
        indData = independentT.getSelectedDateScores()
        depData = dependentT.getSelectedDateScores()

        lastResult = depData[lag]

        for i in range(1, len(depData) - lag):
            thisCause = indData[i]
            thisResult = depData[i + lag]
            changeSign = np.sign(thisResult - lastResult)

            if thisCause == 0:
                zeroCount += 1
                zeroChanges += changeSign
            else:
                nonzeroCount += 1
                nonzeroChanges += changeSign

        # Probability between -1 and 1 dictating direction of change
        scaledZeros = zeroChanges / zeroCount
        scaledNonzeros = nonzeroChanges / nonzeroCount

        # Size of correlation depends on the relative probabilities
        correlation = (scaledNonzeros - scaledZeros) / 2
        return correlation, -1


# Wrapper over whichver impact test is needed
class ImpactTest:

    def __init__(self, isBinary=False):
        self.impactTest = BinaryImpactTest() if isBinary else ContinuousImpactTest()
        self.name = self.impactTest.name
        self.displayName = self.impactTest.displayName
        self.isSymmetric = self.impactTest.isSymmetric

    def runTestForLag(self, dependentT, independentT, lagDays):
        return self.impactTest.runTestForLag(dependentT, independentT, lagDays)

    def runTestOverRange(self, dependentT, independentT, minLag=0, maxLag=3):
        return self.impactTest.runTestOverRange(dependentT, independentT, minLag, maxLag)
