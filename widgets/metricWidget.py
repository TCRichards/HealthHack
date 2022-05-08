from PyQt5.QtWidgets import *
from PyQt5.QtGui import *
from PyQt5.QtCore import *

import numpy as np
import pandas as pd

from stats.frequency import Frequency
from stats.test import Test
from widgets.util.centeredComboBox import LabeledCenteredComboBox
from widgets.util.coloredWidgets import *
from widgets.util.centeredLabel import CenteredLabel
from widgets.util.centeredSpinBox import LabeledCenteredSpinBox

from widgets.testPanels import *


'''
Widget that contains a user interface for exploring the quantitative
trends in single variables and the relationships between multiple variables
'''


class MetricWidget(QWidget):

    def __init__(self, analyzeWindow):
        super().__init__()

        self.masterLayout = QVBoxLayout()
        self.masterLayout.setAlignment(Qt.AlignTop)
        self.setLayout(self.masterLayout)
        self.setSizePolicy(QSizePolicy.Preferred, QSizePolicy.MinimumExpanding)

        self.dateRangeLabel = CenteredLabel('Selected Dates: ')
        self.dateRangeLabel.setFont(QFont('Arial', 11))
        self.masterLayout.addWidget(self.dateRangeLabel)

        self.layout = QHBoxLayout()
        self.layout.setAlignment(Qt.AlignTop)
        mainWidget = QWidget()
        self.masterLayout.addWidget(mainWidget)
        mainWidget.setLayout(self.layout)

        # Devote area for trackables analyzed
        self.trackableHomePanel = TrackableHomePanel()
        self.testsHomePanel = TestsHomePanel()
        self.layout.addWidget(self.trackableHomePanel)
        self.layout.addWidget(self.testsHomePanel)

        self.analyzeWindow = analyzeWindow

    # @brief Deletes all current UI elements, then creates new ones for currently selected trackable group
    def updatePanels(self):
        self.trackableHomePanel.clear()
        self.testsHomePanel.clear()

        trackableGroup = self.analyzeWindow.getCurrentTrackables()
        trackables = trackableGroup.getTrackables()
        self.setDateRangeText(trackables[0].getSelectedDates())

        self.trackableHomePanel.updateFromGroup(trackableGroup)
        self.testsHomePanel.updateFromGroup(trackableGroup)

    # @brief Sets the text of the QLabel displaying the date range over which analysis is being done
    def setDateRangeText(self, dates):
        startString = pd.to_datetime(dates[0]).strftime('%m/%d/%Y')
        endString = pd.to_datetime(dates[-1]).strftime('%m/%d/%Y')
        self.dateRangeLabel.setText(
            f'Dates Used in Analysis: {startString} to {endString}')

    # @brief Changes label text and shows/hides test label based on 1 vs. >1 trackables
    def setPluralization(self, numTrackables):
        self.trackableHomePanel.setPlural(numTrackables > 1)
        self.testsHomePanel.setVisible(numTrackables > 1)


# UI element displaying each trackable being analyzed along with simple metrics
class TrackableMetricsPanel(QWidget):

    def __init__(self, trackable, showDependentText=False, isDependent=False):
        super().__init__()
        self.setSizePolicy(QSizePolicy.MinimumExpanding, QSizePolicy.Minimum)
        self.trackable = trackable

        self.layout = QVBoxLayout()
        self.setLayout(self.layout)

        if showDependentText:
            typeLabel = CenteredLabel(
                ('Dependent ' if isDependent else 'Independent ') + 'Variable')
            typeLabel.setFont(QFont('Arial', 15))
            self.layout.addWidget(typeLabel)

        nameLabel = CenteredLabel(trackable.name)
        nameLabel.setFont(QFont('Arial', 13))
        self.layout.addWidget(nameLabel)

        # Don't show any metrics if data is missing
        if trackable.selectedRangeHasNaN():
            missingLabel = CenteredLabel('Statistics are unavailable when data in the selected range is Missing.\nTo view statistics, narrow the date range or select a fill strategy.')
            self.layout.addWidget(missingLabel)
            return

        # Depending on the trackable type, this may be a float (for numeric) or a string (for time)
        mean = self.getMean()
        stdev = self.getStdev()

        meanLabel = CenteredLabel('Mean: ' + mean)
        self.layout.addWidget(meanLabel)

        stdevLabel = CenteredLabel('Standard Deviation: ' + stdev)
        self.layout.addWidget(stdevLabel)

    # Calculates the mean of the currently selected trackable over the range selected in the analyzeWindow
    def getMean(self):
        return self.trackable.getCurrentMeanStr()

    def getStdev(self):
        return self.trackable.getCurrentStdevStr()


class AbstractHomePanel(QWidget):

    def __init__(self, bannerText):
        super().__init__()
        self.fullLayout = QVBoxLayout()
        self.fullLayout.setAlignment(Qt.AlignTop)
        self.setLayout(self.fullLayout)

        self.banner = CenteredLabel(bannerText)
        self.banner.setFont(QFont('Arial', 15))
        self.fullLayout.addWidget(self.banner)

        self.homePanel = QWidget()
        self.homeLayout = QHBoxLayout()
        self.homeLayout.setAlignment(Qt.AlignTop)
        self.homePanel.setLayout(self.homeLayout)
        self.fullLayout.addWidget(self.homePanel)

        self.activePanels = []

    # @brief abstract method used to update displayed panels based on selected group
    def updateFromGroup(self, trackableGroup):
        ...

    # @brief change behavior based on whether multiple trackables are being analyzed
    def setMultiple(self, isMultiple):
        ...

    def addPanel(self, newPanel):
        self.homeLayout.addWidget(newPanel)
        self.activePanels.append(newPanel)

    def clear(self):
        for panel in self.activePanels:
            self.homeLayout.removeWidget(panel)
            # this needs to be called for garbage collection to occur
            panel.setParent(None)


# UI element containing a set of TrackableMetricsPanels
class TrackableHomePanel(AbstractHomePanel):

    def __init__(self):
        super().__init__('Active Variable')
        self.setSizePolicy(QSizePolicy.Minimum, QSizePolicy.Minimum)

    def updateFromGroup(self, trackableGroup):
        multiple = trackableGroup.independentT is not None
        self.setMultiple(multiple)
        if multiple:
            tPanel = TrackableMetricsPanel(
                trackableGroup.independentT, showDependentText=True, isDependent=False)
            self.addPanel(tPanel)

        dependentVar = trackableGroup.dependentT
        tPanel = TrackableMetricsPanel(
            dependentVar, showDependentText=multiple, isDependent=True)
        self.addPanel(tPanel)

    def setMultiple(self, isMultiple):
        self.banner.setText(
            'Active Variables' if isMultiple else 'Active Variable')


# UI element containing a set of TestsPanels
class TestsHomePanel(AbstractHomePanel):

    def __init__(self):
        super().__init__('Tests')
        self.setSizePolicy(QSizePolicy.MinimumExpanding,
                           QSizePolicy.MinimumExpanding)

        # Holder for spinners to set min / max lag
        self.spinnerWidget = QWidget()
        self.spinnerLayout = QHBoxLayout()
        self.spinnerWidget.setLayout(self.spinnerLayout)
        self.fullLayout.addWidget(self.spinnerWidget)

        self.minLagSpinner = LabeledCenteredSpinBox(
            self.spinnerWidget, 'Minimum Lag')
        self.minLagSpinner.spin.setRange(0, 10)
        self.minLagSpinner.spin.setValue(0)
        self.minLagSpinner.spin.valueChanged.connect(self.updateMinLag)

        self.maxLagSpinner = LabeledCenteredSpinBox(
            self.spinnerWidget, 'Maximum Lag')
        self.maxLagSpinner.spin.setRange(0, 10)
        self.maxLagSpinner.spin.setValue(5)
        self.maxLagSpinner.spin.valueChanged.connect(self.updateMaxLag)

        self.spinnerLayout.insertWidget(0, self.minLagSpinner)
        self.spinnerLayout.insertWidget(1, self.maxLagSpinner)

        # Add a combo box to select which test results to actively display
        self.whichTestComboBox = LabeledCenteredComboBox(self, 'Select Test')
        self.whichTestComboBox.addItems(Test.getTestNames())
        self.whichTestComboBox.combo.currentTextChanged.connect(
            self.updateActiveTest)
        self.fullLayout.addWidget(self.whichTestComboBox)

        # Where to place test results -- stored in testPanels
        self.testsPanel = QWidget()
        self.testsLayout = QHBoxLayout()
        self.testsPanel.setLayout(self.testsLayout)
        self.fullLayout.addWidget(self.testsPanel)

        self.grangerPanel, self.linearRegressionPanel, self.impactPanel = None, None, None
        self.activeTest = None
        self.explanationLabel = None

    # @brief For the provided trackable group add UI elements for each test being performed
    # TODO: Automatically select between binary impact and continuous imact based on trackable types
    def updateFromGroup(self, trackableGroup):
        for panel in [self.grangerPanel, self.linearRegressionPanel, self.impactPanel]:
            if panel is not None:
                self.testsLayout.removeWidget(panel)
                panel.setParent(None)

        multi = len(trackableGroup.getTrackables()) > 1
        self.setMultiple(multi)

        if multi:
            lagRange = self.getSelectedRange()
            self.grangerPanel = GrangerCausalityPanel(lagRange, trackableGroup)
            self.linearRegressionPanel = LinearRegressionPanel(
                lagRange, trackableGroup)
            self.impactPanel = ImpactPanel(
                lagRange, trackableGroup)

            self.updateActiveTest()

    # Updates which test to display based on combo box selection
    def updateActiveTest(self):
        nameToPanelMap = {'Pearson': self.linearRegressionPanel,
                          'Granger': self.grangerPanel,
                          'Impact': self.impactPanel
                          }
        if self.activeTest is not None:
            self.testsLayout.removeWidget(nameToPanelMap[self.activeTest])
            nameToPanelMap[self.activeTest].setParent(None)
            self.testsLayout.removeWidget(self.explanationLabel)
            self.explanationLabel.setParent(None)

        self.activeTest = self.whichTestComboBox.currentText()
        self.explanationLabel = self.makeExplanationLabel(
            nameToPanelMap[self.activeTest])
        self.fullLayout.insertWidget(4, self.explanationLabel)
        self.testsLayout.addWidget(nameToPanelMap[self.activeTest])

    # Explains what the test results show in terms of variables and lag
    # I'll need another tooltip or something to teach how to interpret p value and magnitude
    def makeExplanationLabel(self, activePanel):
        trackableGroup = activePanel.trackableGroup
        independentName = trackableGroup.independentT.name
        dependentName = trackableGroup.dependentT.name

        timeWord = 'Months'
        if trackableGroup.frequency == Frequency.WEEKLY:
            timeWord = 'Weeks'
        elif trackableGroup.frequency == Frequency.DAILY:
            timeWord = 'Days'

        relationshipWord = 'Causes' if self.activeTest == 'Granger' else 'Is Correlated With'
        nowWord = 'Today' if trackableGroup.frequency == Frequency.DAILY else 'This Week'

        expl = 'How to Interepret Test Results:\n{} {} {} {} \'Lag\' {} Later'.format(
            independentName, nowWord, relationshipWord, dependentName, timeWord
        )
        return CenteredLabel(expl)

    def updateMinLag(self):
        newMin = self.minLagSpinner.spin.value()
        if self.maxLagSpinner.spin.value() < newMin:
            self.maxLagSpinner.spin.setValue(newMin)

    def updateMaxLag(self):
        newMax = self.maxLagSpinner.spin.value()
        if self.minLagSpinner.spin.value() > newMax:
            self.minLagSpinner.spin.setValue(newMax)

    def getSelectedRange(self):
        return np.arange(self.minLagSpinner.spin.value(), self.maxLagSpinner.spin.value() + 1)

    # @brief equivalent to a setVisible method for the class
    def setMultiple(self, show):
        self.banner.setVisible(show)
        self.minLagSpinner.setVisible(show)
        self.maxLagSpinner.setVisible(show)
        self.whichTestComboBox.setVisible(show)
