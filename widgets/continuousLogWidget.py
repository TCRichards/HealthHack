from widgets.settings.logTime import LogTime
from trackables.trackables.trackableFactories import UserFactory
from trackables.variableCategories.trackType import TrackType
from PyQt5.QtWidgets import *
from PyQt5.QtGui import *
from PyQt5.QtCore import *

import pandas as pd
from util.dbInterface import DBInterface
from functools import partial

from widgets.baseLogWidget import BaseLogWidget
from widgets.util.centeredLabel import CenteredLabel
from widgets.util.centeredSpinBox import CenteredSpinBox

import util.settings as set


# Class that enables the user to log data into a spreadsheet using pre-defined buttons for each entry
class ContinuousLogWidget(BaseLogWidget):

    def __init__(self, panelName, buttonNameList, trackedTime, scoreWord, isBinary):
        super().__init__(panelName, buttonNameList, trackedTime, scoreWord, isBinary)
        self.buttonNames = buttonNameList

        self.spreadsheetButton = QPushButton('Open All Spreadsheets')
        self.spreadsheetButton.clicked.connect(self.openAllSheets)
        self.layout.addWidget(self.spreadsheetButton)

        buttons = []
        for i, buttonName in enumerate(buttonNameList):
            button = QPushButton('Log %s' % buttonName, self)
            button.clicked.connect(
                partial(lambda x: self.logOnPress(x), x=buttonName))
            self.layout.addWidget(button)
            buttons.append(button)

        valueLabel = CenteredLabel('Value to Track', self)
        self.layout.addWidget(valueLabel)

        valueSpinner = CenteredSpinBox(self)
        if self.isBinary:
            valueSpinner.setRange(0, 1)
        else:
            valueSpinner.setRange(1, 10)

        self.layout.addWidget(valueSpinner)

        self.valueSpinner = valueSpinner
        self.buttons = buttons

    # Each time one of the buttons is pressed, the program should open the panel's spreadsheet
    # at the page defined by the button's name and add a new entry based on the time selected
    def logOnPress(self, buttonName):
        date, time = self.dateTimeWidget.getSelectedDateAndTime()
        value = self.valueSpinner.value()
        self.saveItem(buttonName, value, date, time)
        self.updateSavedTrackable(buttonName, value, date, time)
        set.settings.setAnalysisAndHeatmapUpdated()

    # Loads trackables from the custom Excel sheet
    def getTrackables(self):
        allTrackables = []
        for name in self.buttonNames:
            try:
                df = pd.read_csv(self.getSpreadsheetPath(name))
                df['Date'] = df['Date'].apply(
                    lambda x: DBInterface.convertToDateTime(x, '%m/%d/%Y'))
                if self.trackedTime == LogTime.DATE_AND_TIME:
                    df['Time'] = df['Time'].apply(
                        lambda x: DBInterface.convertToDateTime(x, '%H:%M'))
                df = df.set_index('Date')
                df.sort_index(inplace=True)
                trackType = TrackType.BINARY if self.isBinary else TrackType.CONTINUOUS

                # Everything needs to be tabulated by the general 'Score' column name, not servings
                nextTrackable = UserFactory.create(name, df.rename(columns={
                                          self.scoreWord: 'Score'}), trackType, self.trackedTime)
                allTrackables.append(nextTrackable)

            except FileNotFoundError:
                newDf = pd.DataFrame(
                    data={'Date': 'Date', 'Time': 'Time', self.scoreWord: self.scoreWord}, index=[0])
                DBInterface.append_df_to_csv(self.getSpreadsheetPath(name), newDf)
        return allTrackables

    # @brief Opens the spreadsheet for ALL of the trackables hosted in this widget
    def openAllSheets(self):
        for trackName in self.buttonNames:
            self.openSheet(trackName)
        set.settings.setAnalysisAndHeatmapUpdated()
