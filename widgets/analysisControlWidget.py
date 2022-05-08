from PyQt5.QtWidgets import *
from PyQt5.QtGui import *
from PyQt5.QtCore import *

import pandas as pd
import os
from util.dbInterface import DBInterface

from widgets.trackDateWidget import TrackDateWidget
from widgets.comboType import ComboType
from widgets.util.variate import Variate
from widgets.comboBoxWidget import ComboBoxWidget
from widgets.util.labeledHorizontalButtons import LabeledHorizontalButtons
from widgets.util.centeredLabel import CenteredLabel
from widgets.util.coloredWidgets import *

from trackables.trackableManager import TrackableManager as TM
from trackables.trackableGroup import TrackableGroup
from trackables.variableCategories.trackType import TrackType

from stats.frequency import Frequency, GroupingMethod
from stats.fillStrategy import FillStrategy
from util.paths import processedDataDir


class AnalysisControlWidget(LightGrayWidget):
    def __init__(self, analyzeWindow):
        super().__init__()
        self.analyzeWindow = analyzeWindow

        # Layout defining the control panels on the left side with buttons
        self.controlLayout = QVBoxLayout()
        self.controlLayout.setAlignment(Qt.AlignTop)
        self.setLayout(self.controlLayout)

        # Instantiate all QWidgets
        self.changeVariateBut, self.variate = self.createChangeVariateButton()
        self.plotUpdateBut = self.createAnalysisUpdateButton()
        self.saveDataBut = self.createSaveDataButton()

        self.controlLayout.addWidget(self.changeVariateBut)
        self.controlLayout.addWidget(self.plotUpdateBut)
        self.controlLayout.addWidget(self.saveDataBut)

        # Since we use separate combo boxes depending on whether single vs. multivariable tracking, store each in
        # dictionaries accessed by the combotype
        self.ouraWidgets = {
            ComboType.SINGLE: self.createOuraCombo(ComboType.SINGLE),
            ComboType.X: self.createOuraCombo(ComboType.X),
            ComboType.Y: self.createOuraCombo(ComboType.Y),
        }

        self.categoryWidgets = {
            ComboType.SINGLE: self.createCategoryCombo(ComboType.SINGLE),
            ComboType.X: self.createCategoryCombo(ComboType.X),
            ComboType.Y: self.createCategoryCombo(ComboType.Y),
        }

        self.specificComboWidgets = {
            ComboType.SINGLE: self.createComboWidget(ComboType.SINGLE),
            ComboType.X: self.createComboWidget(ComboType.X),
            ComboType.Y: self.createComboWidget(ComboType.Y),
        }

        self.fillWidgets = {
            ComboType.SINGLE: self.createFillCombo(ComboType.SINGLE),
            ComboType.X: self.createFillCombo(ComboType.X),
            ComboType.Y: self.createFillCombo(ComboType.Y),
        }
        self.groupingWidgets = {
            ComboType.SINGLE: self.createGroupingButtons(),
            ComboType.X: self.createGroupingButtons(),
            ComboType.Y: self.createGroupingButtons(),
        }
        self.spacers = {
            ComboType.SINGLE: self.createSpacer(),
            ComboType.X: self.createSpacer(),
            ComboType.Y: self.createSpacer(),
        }
        # Shows the allow date range under each selected trackable
        self.dateDisplays = {
            ComboType.SINGLE: self.createDateDisplay(),
            ComboType.X: self.createDateDisplay(),
            ComboType.Y: self.createDateDisplay(),
        }

        # Only add oura ring combos if it successfully found data
        addOura = self.ouraWidgets[ComboType.SINGLE].combo.count() > 0
        catList = list(self.categoryWidgets.values())
        specificList = list(self.specificComboWidgets.values())
        ouraList = list(self.ouraWidgets.values())
        fillList = list(self.fillWidgets.values())
        groupList = list(self.groupingWidgets.values())
        dateList = list(self.dateDisplays.values())
        spacerList = list(self.spacers.values())

        for i in range(len(catList)):
            self.controlLayout.addWidget(catList[i].widget)
            self.controlLayout.addWidget(specificList[i].widget)

            if addOura:
                self.controlLayout.addWidget(ouraList[i].widget)

            self.controlLayout.addWidget(groupList[i])
            self.controlLayout.addWidget(fillList[i].widget)
            self.controlLayout.addWidget(dateList[i])

            # Add a blank space after each comboType's inputs to clearly differentiate
            self.controlLayout.addWidget(spacerList[i])

        self.frequencyCombo = self.createFrequencyCombo()
        self.controlLayout.addWidget(self.frequencyCombo.widget)

        self.trackDateWidget = TrackDateWidget(self)
        self.controlLayout.addWidget(self.trackDateWidget)

        # Instantiate the dual combos now even though not in use
        self.updateLayoutCombos()  # Start in the single combo mode

        self.currentTrackables = None
        self.updateSelectedTrackables()

        self.trackDateWidget.addFunctionOnChange(
            self.updateTrackableDateSelection)

        self.updateTrackableDateSelection()

    # Called whenever one of the combo boxes is updated -> changes the currentTrackables member
    # That stores the reference that plotWidget and metricWidget reference
    def updateSelectedTrackables(self):
        if self.variate == Variate.UNIVARIATE:
            curTrackable = self.getSelectedTrackable(ComboType.SINGLE)
            if curTrackable is not None:
                self.currentTrackables = TrackableGroup(curTrackable)
                self.updateFillCombo(curTrackable, ComboType.SINGLE)
                self.updateGroupingOptions(ComboType.SINGLE)
                self.updateDateDisplays(curTrackable, ComboType.SINGLE)

        elif self.variate == Variate.BIVARIATE:
            independent = self.getSelectedTrackable(ComboType.X)
            dependent = self.getSelectedTrackable(ComboType.Y)
            if dependent is not None and independent is not None:
                self.updateFillCombo(independent, ComboType.X)
                self.updateFillCombo(dependent, ComboType.Y)
                self.updateDateDisplays(independent, ComboType.X)
                self.updateDateDisplays(dependent, ComboType.Y)
                self.updateGroupingOptions(ComboType.X)
                self.updateGroupingOptions(ComboType.Y)
                self.currentTrackables = TrackableGroup(dependent, independent)

            self.enableUpdateButtonIfValidSelection()

        self.toggleAllGroupingWidgets()
        # When we break out of the getSelectedTracakble() function because the combo is empty it will throw an exception
        try:
            self.trackDateWidget.setTrackableDateRange()
        except AttributeError:
            pass

    # Returns the selected trackable from the given comboBox
    def getSelectedTrackable(self, comboType):
        comboText = self.specificComboWidgets[comboType].getSelectedText()
        # Since this may be called when combos are cleared and no inputs are selected, just ignore
        if comboText == "":
            return
        if self.categoryWidgets[comboType].getSelectedText() == "Oura Ring":
            ouraComboText = self.ouraWidgets[comboType].getSelectedText()
            if ouraComboText == "":
                return
            trackable = TM.instance().getOuraTrackableFromName(
                comboText.lower(), ouraComboText
            )
        else:
            trackable = TM.instance().getTrackableFromName(comboText)
        return trackable

    def enableUpdateButtonIfValidSelection(self):
        if self.currentTrackables.isValid():
            self.plotUpdateBut.setEnabled(True)
            self.plotUpdateBut.setText("Update Analysis")
        else:
            self.plotUpdateBut.setEnabled(False)
            self.plotUpdateBut.setText("Invalid Selection")

    # Shifts the dates of all selected trackables to the range selected by trackDateWidget
    def updateTrackableDateSelection(self):
        validDates, startDate, endDate = self.trackDateWidget.getSelectedStartEndDates()
        # Disable the update button if the date selection is invalid
        self.plotUpdateBut.setEnabled(validDates)
        self.plotUpdateBut.setText("Update Analysis" if validDates else "Invalid Dates Selected")
        if not validDates:
            return

        comboTypes = (
            [ComboType.SINGLE]
            if len(self.currentTrackables.getTrackables()) == 1
            else [ComboType.Y, ComboType.X])

        for i, t in enumerate(self.currentTrackables.getTrackables()):
            t.setCurrentDateRange(startDate, endDate)
            self.updateFillCombo(
                t, comboTypes[i], dateRange=pd.date_range(startDate, endDate))

    # Switches the display between tracking a single variable and dual variables on button press
    def switchPlotMode(self):
        if self.variate == Variate.UNIVARIATE:
            self.variate = Variate.BIVARIATE
            self.changeVariateBut.setText("Switch to Single-Variable Tracking")
        elif self.variate == Variate.BIVARIATE:
            self.variate = Variate.UNIVARIATE
            self.changeVariateBut.setText("Switch To Multi-Variable Tracking")
        self.updateLayoutCombos()
        self.updateSelectedTrackables()

    def createChangeVariateButton(self):
        changeVariateBut = QPushButton("Switch To Multi-Variable Tracking", self)
        changeVariateBut.clicked.connect(self.switchPlotMode)
        variate = Variate.UNIVARIATE
        return changeVariateBut, variate

    def createAnalysisUpdateButton(self):
        analysisUpdateButton = QPushButton("Update Anlysis", self)
        analysisUpdateButton.clicked.connect(self.updateAnalysisWidgets)
        return analysisUpdateButton

    def createSaveDataButton(self):
        saveDataButton = QPushButton("Export to CSV", self)
        saveDataButton.clicked.connect(self.saveCurrentData)
        return saveDataButton

    # @brief update the selected dates and then pass control to analyzeWindow to handle
    # plot and metric widget
    def updateAnalysisWidgets(self):
        # Update trackable calculations (unless cached calculation is still valid)
        freq = self.getSelectedFrequency()
        validDates, startDate, endDate = self.trackDateWidget.getSelectedStartEndDates()
        # Disable the update button if the date selection is invalid
        self.plotUpdateBut.setEnabled(validDates)
        self.plotUpdateBut.setText("Update Analysis" if validDates else "Invalid Dates Selected")
        if not validDates:
            return

        dateRange = pd.date_range(startDate, endDate)
        # Collect the fill selection for each widget, even if not used
        fillStrats = [
            FillStrategy.mapStratStringToEnum(f.combo.currentText())
            for f in self.fillWidgets.values()
        ]

        groupMethods = [
            GroupingMethod.mapGroupingStringToEnum(
                g.buttons.checkedButton().text())
            for g in self.groupingWidgets.values()
        ]

        self.currentTrackables.updateCalculation(
            freq, groupMethods, fillStrats, dateRange)
        # Update the rest of the widgets
        # self.updateTrackableDateSelection()
        self.analyzeWindow.updateAnalysisWidgets()

    # @brief open a file explorer dialog and prompt the user to save
    # the cleaned data that is currently stored in self.currentTrackables
    def saveCurrentData(self):
        for t in self.currentTrackables.getTrackables():
            question = "Save Location for " + t.name
            defaultSaveName = os.path.join(processedDataDir, (t.name + '_processed.csv'))

            options = QFileDialog.Options()
            options |= QFileDialog.DontUseNativeDialog

            saveDialog = QFileDialog()
            saveDialog.setOptions(options)
            saveDialog.setDirectory(processedDataDir)
            saveDialog.setFilter(saveDialog.filter() | QDir.Hidden)

            savePath = saveDialog.getSaveFileName(self, question, defaultSaveName,
                                                   'All Files (*);;CSV Files (*.csv)', options=options)[0]

            if savePath != '':
                DBInterface.saveTrackable(t, savePath)

    def createFrequencyCombo(self):
        frequencies = [d.toString() for d in Frequency.list()]
        freqComboWidget = ComboBoxWidget("Set Measurement Frequency", frequencies)
        # This single frequency selector controls whether to activate all grouping widgets
        freqComboWidget.combo.currentIndexChanged.connect(self.toggleAllGroupingWidgets)
        return freqComboWidget

    # Enable / disable any grouping widgets that are relevant to display
    def toggleAllGroupingWidgets(self):
        def hideWidget(c):
            self.groupingWidgets[c].setVisible(False)

        def showWidget(c):
            self.groupingWidgets[c].setVisible(True)
            self.updateGroupingOptions(c)

        activeCombos = [ComboType.SINGLE] if self.variate == Variate.UNIVARIATE else [ComboType.X, ComboType.Y]
        showAny = self.getSelectedFrequency() in [Frequency.WEEKLY, Frequency.MONTHLY]
        if not showAny:
            for c in ComboType.list():
                hideWidget(c)
            return

        for c in ComboType.list():
            if c in activeCombos:
                showWidget(c)
            else:
                hideWidget(c)

    def updateGroupingOptions(self, comboType):
        trackable = self.getSelectedTrackable(comboType)
        if trackable is None:
            return

        allowSum = trackable.getTrackType() != TrackType.TIME
        self.groupingWidgets[comboType].setIdxEnabled(1, allowSum)
        if not allowSum:
            self.groupingWidgets[comboType].setIdxChecked(0, True)

    def createGroupingButtons(self):
        buttonWidget = LabeledHorizontalButtons(
            "How to Group Measurements",
            [g.toString() for g in GroupingMethod.getDefaultGroupingMethods()],
            exclusive=True,
            setFirstChecked=True,
            funcOnClick=None,
        )
        buttonWidget.setVisible(False)
        return buttonWidget

    # Creates the combo box defining which single variable to track
    def createComboWidget(self, comboType):
        currentCategory = self.categoryWidgets[comboType].getSelectedText()
        trackables = TM.instance().getAnalyzableTrackablesOfCategory(currentCategory)
        trackableNames = [t.name for t in trackables]
        comboWidget = ComboBoxWidget(
            "{}Variable to Track".format(
                comboType.getLabelText()), trackableNames
        )
        # Since this combo is also used to store the oura ring's categories,
        # it needs to update the the ouraCombo
        comboWidget.addFunctionOnChange(
            lambda: self.updateSingleComboOnChange(comboType)
        )
        return comboWidget

    # Updates the selected trackables which impacts the date range
    # Also deals with the dependent ouraCombo if that is selected
    def updateSingleComboOnChange(self, comboType):
        # Since this is also triggered when the combo is cleared, check that we're not calling it with
        # no selected items
        if self.specificComboWidgets[comboType].combo.count():
            self.updateOuraCombo(comboType)
            self.updateSelectedTrackables()

    def getSelectedFrequency(self):
        try:
            selectedFrequencyStr = self.frequencyCombo.combo.currentText()
            return Frequency.mapFreqStringToEnum(selectedFrequencyStr)
        except AttributeError:
            return Frequency.DAILY

    # Creates the combo box defining which category of trackable to select from
    def createCategoryCombo(self, comboType):
        categories = TM.instance().getCategories()
        catComboWidget = ComboBoxWidget(
            "{}Category to Explore".format(
                comboType.getLabelText()), categories
        )

        # When the category is changed, instantaneously update the selections available to the singleCombo
        def updateComboChoices():
            category = catComboWidget.getSelectedText()
            if (
                category != "Oura Ring"
            ):  # Oura ring has nested categories so handle separately
                trackables = TM.instance().getAnalyzableTrackablesOfCategory(category)
                names = [t.name for t in trackables]
                self.hideOuraCombo(comboType)
            else:
                names = ["Readiness", "Sleep", "Activity"]

            # Need to update the single combo before updating ouraCombo
            self.specificComboWidgets[comboType].setItems(names)
            if category == "Oura Ring":
                self.showOuraCombo(comboType)
                self.updateOuraCombo(comboType)

        catComboWidget.addFunctionOnChange(updateComboChoices)
        return catComboWidget

    # Creates a combo box whose list of items corresponds to each Oura category type
    # 'readiness', 'sleep', or 'activity'
    def createOuraCombo(self, comboType):
        # Assume that the default category is readiness
        trackableNames = [
            t.name
            for t in TM.instance().getAnalyzableOuraTrackablesOfCategory("readiness")
        ]
        ouraComboWidget = ComboBoxWidget(
            "{}Oura Readiness Variables".format(comboType.getLabelText()),
            trackableNames,
        )
        ouraComboWidget.setVisible(False)
        ouraComboWidget.addFunctionOnChange(self.updateSelectedTrackables)
        return ouraComboWidget

    # Make the additional Oura combo box invisible
    def hideOuraCombo(self, comboType):
        self.controlLayout.removeWidget(self.ouraWidgets[comboType])
        self.ouraWidgets[comboType].setVisible(False)

    # Make the additional Oura combo box visible
    def showOuraCombo(self, comboType):
        self.controlLayout.addWidget(self.ouraWidgets[comboType])
        self.ouraWidgets[comboType].setVisible(True)

    # This method will be called every time the singleCombo is changed
    # We only want it to do anything if the catCombo is on 'Oura Ring'
    def updateOuraCombo(self, comboType):
        trackCategory = self.categoryWidgets[comboType].getSelectedText()
        if trackCategory != "Oura Ring":
            return
        ouraCategory = self.specificComboWidgets[comboType].getSelectedText().lower()
        trackables = TM.instance().getAnalyzableOuraTrackablesOfCategory(ouraCategory)
        names = [t.name for t in trackables]
        self.ouraWidgets[comboType].setItems(names)
        self.ouraWidgets[comboType].setText(
            "Oura {} Variable".format(ouraCategory.capitalize())
        )

    # Creates a combo box whose list of items corresponds to each Oura category type
    # 'readiness', 'sleep', or 'activity'
    def createFillCombo(self, comboType):
        # Assume that the default category is readiness
        fillOptions = [f.toString()
                       for f in FillStrategy.getDefaultStrategies()]
        fillComboWidget = ComboBoxWidget(
            "How to Deal with Missing Data", fillOptions)
        fillComboWidget.setVisible(False)
        fillComboWidget.addFunctionOnChange(
            lambda: self.updateFillStrategy(comboType))
        return fillComboWidget

    # Make the additional Oura combo box invisible
    def hideFillCombo(self, comboType):
        self.controlLayout.removeWidget(self.fillWidgets[comboType])
        self.fillWidgets[comboType].setVisible(False)

    # Make the additional Oura combo box visible
    def showFillCombo(self, comboType, trackType):
        fillToChange = self.fillWidgets[comboType]
        # Only update entries if there's a change to avoid overriding current selection
        if trackType == TrackType.TIME:
            fillOptions = [f.toString()
                           for f in FillStrategy.getTimeStrategies()]
        else:
            fillOptions = [f.toString()
                           for f in FillStrategy.getDefaultStrategies()]

        currentItems = set([self.fillWidgets[comboType].combo.itemText(i) for i in range(self.fillWidgets[comboType].combo.count())])
        if set(fillOptions) == currentItems:
            return

        # Need to temporarily disconnect the update signal to change items
        fillToChange.disconnectSignals()
        fillToChange.combo.clear()
        fillToChange.combo.addItems(fillOptions)
        fillToChange.addFunctionOnChange(
            lambda: self.updateFillStrategy(comboType))

        self.controlLayout.addWidget(fillToChange)
        fillToChange.setVisible(True)

    def updateFillStrategy(self, comboType):
        trackableToUpdate = self.getSelectedTrackable(comboType)
        stratText = self.fillWidgets[comboType].getSelectedText()
        strat = FillStrategy.mapStratStringToEnum(stratText)
        trackableToUpdate.setFillStrategy(strat)

    def updateFillCombo(self, trackable, comboType, dateRange=None):
        if trackable.hasMissingDates(nominalDateRange=dateRange):
            self.showFillCombo(comboType, trackable.getTrackType())
            self.updateFillStrategy(comboType)
        else:
            self.hideFillCombo(comboType)

    # Creates two combo boxes on distinct widgets for analyzing dual variables
    def createDualCombos(self):
        trackableNames = [t.name for t in TM.instance().trackables]
        xComboWidget = ComboBoxWidget(
            "Adjust Independent Parameter", trackableNames)
        yComboWidget = ComboBoxWidget(
            "Adjust Dependent Parameter", trackableNames)

        return xComboWidget, yComboWidget

    # @brief Return a QWidget that can stretch in the Y direction to place
    # between combo boxes for different sections
    def createSpacer(self):
        spacer = LightGrayWidget()
        spacer.setAutoFillBackground(True)
        spacer.setMinimumSize(0, 25)
        spacer.setMaximumSize(0, 30)
        spacer.setSizePolicy(QSizePolicy.Minimum, QSizePolicy.Preferred)
        return spacer

    def createDateDisplay(self):
        dateLabel = CenteredLabel('')
        dateLabel.setFont(QFont('Arial', 8))
        return dateLabel

    def updateDateDisplays(self, trackable, comboType):
        minDateStr = trackable.rawData.index[0].strftime('%m/%d/%Y')
        maxDateStr = trackable.rawData.index[-1].strftime('%m/%d/%Y')
        rangeStr = f'{trackable.name} has data between {minDateStr} and {maxDateStr}'
        self.dateDisplays[comboType].setText(rangeStr)

    # Adds whichever combo boxes are relevant to the control panel
    def updateLayoutCombos(self):
        if self.variate == Variate.UNIVARIATE:
            removedTypes = [ComboType.X, ComboType.Y]
            addedTypes = [ComboType.SINGLE]
        else:
            removedTypes = [ComboType.SINGLE]
            addedTypes = [ComboType.X, ComboType.Y]

        for removal in removedTypes:
            self.controlLayout.removeWidget(self.categoryWidgets[removal])
            self.controlLayout.removeWidget(self.specificComboWidgets[removal])

            self.categoryWidgets[removal].setVisible(False)
            self.specificComboWidgets[removal].setVisible(False)
            self.fillWidgets[removal].setVisible(False)
            self.spacers[removal].setVisible(False)
            self.dateDisplays[removal].setVisible(False)

        for addition in addedTypes:
            self.controlLayout.addWidget(self.categoryWidgets[addition])
            self.controlLayout.addWidget(self.specificComboWidgets[addition])

            self.categoryWidgets[addition].setVisible(True)
            self.specificComboWidgets[addition].setVisible(True)
            self.fillWidgets[addition].setVisible(True)
            self.spacers[addition].setVisible(True)
            self.dateDisplays[addition].setVisible(True)

        # To avoid lingering oura combos after change explicitly hide all unless Oura ring is the currently selected category
        for comboType in ComboType.list():
            if comboType in removedTypes or self.categoryWidgets[comboType].combo.currentText() != 'Oura Ring':
                self.hideOuraCombo(comboType)
            else:
                self.showOuraCombo(comboType)

    def getCurrentTrackables(self):
        return self.currentTrackables
