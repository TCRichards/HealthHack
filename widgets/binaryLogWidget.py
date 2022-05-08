from trackables.trackables.trackableFactories import UserFactory
from trackables.variableCategories.trackType import TrackType
from widgets.baseLogWidget import BaseLogWidget
from widgets.settings.logTime import LogTime

from PyQt5.QtWidgets import *
from PyQt5.QtGui import *
from PyQt5.QtCore import *
import util.settings as set

import pandas as pd
from util.dbInterface import DBInterface


class BinaryLogWidget(BaseLogWidget):

    def __init__(self, panelName, checkboxItems, trackedTime, scoreWord, isBinary):
        super().__init__(panelName, checkboxItems, trackedTime, scoreWord, isBinary)
        self.checkboxItems = checkboxItems

        self.spreadsheetButton = QPushButton('Open Selected Spreadsheet')
        self.spreadsheetButton.clicked.connect(self.openSelectedSheets)
        self.spreadsheetButton.setEnabled(False)
        self.layout.addWidget(self.spreadsheetButton)

        self.logButton = QPushButton('Log Selected', self)
        self.logButton.clicked.connect(self.logSelected)
        self.layout.addWidget(self.logButton)

        self.buttonGroup = QButtonGroup()
        self.buttonGroup.setExclusive(False)
        for idx, name in enumerate(checkboxItems):
            newButton = QCheckBox(name, self)
            self.buttonGroup.addButton(newButton, idx)
            self.layout.addWidget(newButton)
            newButton.clicked.connect(self.updateOpenSpreadsheetButton)

    # This function gathers the checked boxes and calls the provided logFunc
    # to store them in a spreadsheet
    def logSelected(self):
        date, time = self.getSelectedDateAndTime()

        while True:  # Read the state of all checked buttons
            supIdx = self.buttonGroup.checkedId()
            if supIdx == -1:    # If no buttons are checked
                break
            checkedBut = self.buttonGroup.checkedButton()
            selection = checkedBut.text()
            self.saveItem(selection, 1, date, time)
            checkedBut.setChecked(False)
            self.updateSavedTrackable(selection, 1, date, time)
        set.settings.setAnalysisAndHeatmapUpdated()

    def openSelectedSheets(self):
        for button in self.buttonGroup.buttons():
            if button.isChecked():
                self.openSheet(button.text())
        set.settings.setAnalysisAndHeatmapUpdated()

    # Data for the binaryLogWidget is all stored in a single Excel sheet
    # where each item in the checkbox has a separate sheetName
    def getTrackables(self):
        # Iterate through all of the sheets until no more remain
        allTrackables = []
        for name in self.checkboxItems:
            try:
                df = pd.read_csv(self.getSpreadsheetPath(name))
                df['Date'] = df['Date'].apply(
                    lambda x: DBInterface.convertToDateTime(x, '%m/%d/%Y'))
                if self.trackedTime == LogTime.DATE_AND_TIME:
                    df['Time'] = df['Time'].apply(
                        lambda x: DBInterface.convertToDateTime(x, '%H:%M'))
                df = df.set_index('Date')
                df.sort_index(inplace=True)

                scoreDf = df.rename(columns={self.scoreWord: 'Score'})
                trackType = TrackType.BINARY if self.isBinary else TrackType.CONTINUOUS
                nextTrackable = UserFactory.create(name, scoreDf, trackType, self.trackedTime)
                allTrackables.append(nextTrackable)

            # If this is our first time creating the data, make a new csv
            except FileNotFoundError:
                if self.trackedTime == LogTime.DATE_AND_TIME:
                    newDf = pd.DataFrame(
                        data={'Date': 'Date', 'Time': 'Time', self.scoreWord: self.scoreWord}, index=[0])
                else:
                    newDf = pd.DataFrame(
                        data={'Date': 'Date', self.scoreWord: self.scoreWord}, index=[0])
                DBInterface.append_df_to_csv(self.getSpreadsheetPath(name), newDf)
        return allTrackables

    def updateOpenSpreadsheetButton(self):
        numSelected = sum([int(b.isChecked()) for b in self.buttonGroup.buttons()])
        self.spreadsheetButton.setText('Open Selected Spreadsheet' + ('s' if numSelected > 1 else ''))
        self.spreadsheetButton.setEnabled(numSelected > 0)
