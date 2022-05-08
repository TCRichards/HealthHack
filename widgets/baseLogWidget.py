from PyQt5.QtWidgets import *
from PyQt5.QtGui import *
from PyQt5.QtCore import *

import pandas as pd
from xlrd import XLRDError
import os
from abc import abstractmethod
from zipfile import BadZipFile  # Protects against erorr from corrupted spreadsheet

from widgets.dateTimeWidget import DateTimeWidget
from widgets.util.centeredLabel import CenteredLabel
from widgets.settings.logTime import LogTime
import trackables.trackableManager as manager

from util.paths import dataDir
from util.dbInterface import DBInterface


class BaseLogWidget(QWidget):

    # Panel for all kinds of illicit Behaviors
    def __init__(self, panelName, trackableNames, trackedTime, scoreWord, isBinary):
        super().__init__()
        self.panelName = panelName
        self.scoreWord = scoreWord
        self.isBinary = isBinary
        self.trackedTime = trackedTime

        self.layout = QVBoxLayout()
        self.layout.setAlignment(Qt.AlignTop)
        self.setLayout(self.layout)

        self.label = CenteredLabel(panelName, self)
        self.label.setFont(QFont('Arial', 13, QFont.Bold))
        self.layout.addWidget(self.label)

        # Add label that displays recent history
        self.historyLabel = HistoryLabel(self)
        self.refreshHistoryLabel()
        self.layout.addWidget(self.historyLabel)

        self.dateTimeWidget = DateTimeWidget(trackedTime)
        self.layout.addWidget(self.dateTimeWidget.panel)

        # Make sure that the logging sheet contains tab for data and create if not
        for i in trackableNames:
            try:
                pd.read_csv(self.getSpreadsheetPath(i))
            # If the category of trackables or specific trackable within category has not yet been created
            except (FileNotFoundError, KeyError, XLRDError, BadZipFile):
                # Make the new sheet
                if trackedTime == LogTime.DATE_AND_TIME:
                    df = pd.DataFrame({
                        'Date': ['Date'],
                        'Time': ['Time'],
                        scoreWord: [scoreWord]
                    })
                else:
                    df = pd.DataFrame({
                        'Date': ['Date'],
                        scoreWord: [scoreWord]
                    })

                DBInterface.append_df_to_csv(self.getSpreadsheetPath(i), df)

    def getSpreadsheetPath(self, trackableName):
        return os.path.join(self.getPanelDataPath(), trackableName + '.csv')

    def getPanelDataPath(self):
        return os.path.join(dataDir, self.panelName)

    def getSelectedDateAndTime(self):
        return self.dateTimeWidget.getSelectedDateAndTime()

    def getHistoryFilePath(self):
        return os.path.join(self.getPanelDataPath(), self.panelName + '_log.txt')

    @abstractmethod
    def getTrackables(self):
        ...

    # @brief after logging a trackable, we need to update its current representation for use ASAP
    def updateSavedTrackable(self, trackableName, servings, date, time):
        trackable = manager.TrackableManager.instance().getTrackableFromName(trackableName)
        trackable.addEntry(servings, date, time)

    # Default implementation for saving an item in a spreadsheet
    # Works for checkbox and button implementation, where the box/button
    # name corresponds to the the sheet name in a master spreadsheet
    def saveItem(self, name, servings, date, time):
        if time is None:
            nextRow = pd.DataFrame({
                'Date': [date],
                self.scoreWord: [servings]
            })
            msg = '{} logged for {}'.format(name, date)

        else:
            nextRow = pd.DataFrame({
                'Date': [date],
                'Time': [time],
                self.scoreWord: [servings]
            })
            msg = '{} logged for {} {}'.format(name, time, date)

        self.writeEntry(msg)
        try:
            DBInterface.append_df_to_csv(self.getSpreadsheetPath(name), nextRow)
        except PermissionError:
            print('ERROR! CLOSE THE OPEN SPREADSHEET BEFORE LOGGING DATA')
            return False
        return True

    def openSheet(self, trackableName):
        sheetPath = self.getSpreadsheetPath(trackableName)
        try:
            os.startfile(sheetPath)
        except FileNotFoundError:
            print('Unable to open spreadsheet {}'.format(sheetPath))

    def refreshHistoryLabel(self):
        try:
            with open(self.getHistoryFilePath(), 'r') as file:
                self.historyLabel.setText(file.read())
        except FileNotFoundError:
            self.historyLabel.setText('')

    # Logs the entry that was just made to the history file and
    # tells the history label to refresh with new line
    def writeEntry(self, message):
        try:
            with open(self.getHistoryFilePath(), 'a+') as file:
                file.write(message + '\n')
        except FileNotFoundError:
            pass
        self.refreshHistoryLabel()


class HistoryLabel(QScrollArea):

    def __init__(self, parent):
        QScrollArea.__init__(self, parent)
        self.setWidgetResizable(True)
        content = QWidget(self)
        self.setWidget(content)

        self.label = CenteredLabel(content)
        self.label.setAlignment(Qt.AlignLeft | Qt.AlignTop)
        self.label.setWordWrap(True)

        lay = QVBoxLayout(content)
        parent.layout.addWidget(CenteredLabel('Previous Entries'))
        lay.addWidget(self.label)

    def setText(self, text):
        self.label.setText(text)
