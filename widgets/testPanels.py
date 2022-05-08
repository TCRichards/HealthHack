from PyQt5.QtWidgets import *
from PyQt5.QtGui import *
from PyQt5.QtCore import *

import numpy as np

from widgets.util.centeredLabel import CenteredLabel
from trackables.variableCategories.trackType import TrackType

from stats.grangerTest import GrangerTest
from stats.pearsonTest import PearsonTest
from stats.impactTest import ImpactTest


# PyQt doesn't seem to allow multiple inheritance to this class is abstract in name only
# Interface for the UI element wrapping an individual test's results
class AbstractTestPanel(QWidget):

    def __init__(self, test, lagRange, trackableGroup):
        super().__init__()
        self.test = test
        self.trackableGroup = trackableGroup

        self.lagRange = lagRange

        self.layout = QVBoxLayout()
        self.setLayout(self.layout)

        self.nameLabel = CenteredLabel(test.displayName)
        self.nameLabel.setFont(QFont('Arial', 13))
        self.layout.addWidget(self.nameLabel)

        # Temporarily disable tests when working with times (try this out later)
        if any([t.getTrackType() == TrackType.TIME for t in trackableGroup.getTrackables()]):
            failLabel = CenteredLabel('Tests are Disabled for Time Data')
            failLabel.setFont(QFont('Arial', 12))
            self.layout.addWidget(failLabel)
        elif any([len(t.getSelectedDateScores()) < 5 for t in trackableGroup.getTrackables()]):
            failLabel = CenteredLabel(f'Not enough data to run {test.displayName} test')
            failLabel.setFont(QFont('Arial', 12))
            self.layout.addWidget(failLabel)
        else:
            self.displayResults()

    def displayResults(self):
        dep = self.trackableGroup.dependentT
        indep = self.trackableGroup.independentT

        r2s, ps = self.test.runTestOverRange(
            dep, indep, minLag=self.lagRange[0], maxLag=self.lagRange[-1])

        if r2s not in [False, [False]]:

            resultsHeaderStr = 'Results From {}\n'.format(
                self.test.displayName)
            resultsHeaderLabel = CenteredLabel(resultsHeaderStr)
            resultsHeaderLabel.setFont(QFont('Arial', 12))
            freq = self.trackableGroup.frequency
            resultsLabelWidget = self.convertTestResultsToLabelWidget(
                r2s, ps, freq, minLag=self.lagRange[0], maxLag=self.lagRange[-1])
            self.layout.addWidget(resultsLabelWidget)

    # @brief converts results from a test to a set of formatted strings to display
    # Each input may be a float or a list of floats
    def convertTestResultsToLabelWidget(self, r2, p, freq, minLag=0, maxLag=1):
        lagRange = np.arange(minLag, maxLag + 1)
        if not isinstance(r2, list):
            r2 = [r2]
            p = [p]

        background = QWidget()
        backgroundLayout = QHBoxLayout()
        background.setLayout(backgroundLayout)
        for i in range(len(r2)):
            miniBackground = QWidget()
            miniLayout = QVBoxLayout()
            miniBackground.setLayout(miniLayout)
            backgroundLayout.addWidget(miniBackground)

            lagLabel = CenteredLabel('Lag = {} {}:'.format(
                lagRange[i], freq.toQuantity()))
            magnitudeLabel = CenteredLabel('Magnitude = {:.2f}'.format(r2[i]))
            pLabel = CenteredLabel('p Value = {:.2f}\n'.format(p[i]))
            # Color text according to whether it's significant / large
            magnitudeLabel.setAutoFillBackground(True)
            magnitudeLabel.setPalette(self.getColorForMagnitude(r2[i]))

            pLabel.setAutoFillBackground(True)
            pLabel.setPalette(self.getColorForpValue(p[i]))

            for label in [lagLabel, magnitudeLabel, pLabel]:
                miniLayout.addWidget(label)

        return background

    # @brief Implement some color coding to help visualize significance
    def getColorForMagnitude(self, magnitude, weakThreshold=0.3, strongThreshold=0.7):
        palette = QPalette()
        textColor = Qt.black
        if magnitude > strongThreshold:
            textColor = Qt.green
        elif magnitude < weakThreshold:
            textColor = Qt.red
        palette.setColor(QPalette.WindowText, textColor)
        return palette

    def getColorForpValue(self, p, strongThreshold=0.2, weakThreshold=0.4):
        palette = QPalette()
        textColor = Qt.black
        if p < strongThreshold:
            textColor = Qt.green
        elif p > weakThreshold:
            textColor = Qt.red
        palette.setColor(QPalette.WindowText, textColor)
        return palette


class GrangerCausalityPanel(AbstractTestPanel):

    def __init__(self, lagRange, trackableGroup):
        super().__init__(GrangerTest(), lagRange, trackableGroup)


class LinearRegressionPanel(AbstractTestPanel):

    def __init__(self, lagRange, trackableGroup):
        super().__init__(PearsonTest(), lagRange, trackableGroup)


class ImpactPanel(AbstractTestPanel):

    def __init__(self, lagRange, trackableGroup):
        testType = 'Binary' if all([t.getTrackType(
        ) == TrackType.BINARY for t in trackableGroup.getTrackables()]) else 'Continuous'

        super().__init__(ImpactTest(testType == 'Binary'), lagRange, trackableGroup)
