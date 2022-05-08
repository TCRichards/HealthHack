from PyQt5.QtWidgets import *
from PyQt5.QtGui import *
from PyQt5.QtCore import *

from datetime import datetime

from widgets.util.centeredLabel import CenteredLabel


# Defines a panel that is added to the analyzeWindow containing two date editors that enable the
# user to adjust the date range of the trackable(s) being analyzed
class TrackDateWidget(QWidget):

    def __init__(self, analyzeWindow):
        super().__init__()
        self.analyzeWindow = analyzeWindow
        startDatePanel, self.startDateEditor = self.createDateEditor(
            'Select Start Date')
        endDatePanel, self.endDateEditor = self.createDateEditor(
            'Select End Date')

        self.layout = QVBoxLayout()
        self.setLayout(self.layout)

        self.layout.addWidget(startDatePanel)
        self.layout.addWidget(endDatePanel)

    def createDateEditor(self, label):
        layout = QVBoxLayout()
        panel = QWidget()
        panel.setLayout(layout)

        dateEditor = QDateEdit()
        dateEditor.resize(150, 35)
        lineEdit = dateEditor.lineEdit()
        lineEdit.setAlignment(Qt.AlignCenter)

        layout.addWidget(CenteredLabel(label))
        layout.addWidget(dateEditor)
        return panel, dateEditor

    def setTrackableDateRange(self):
        trackableGroup = self.analyzeWindow.getCurrentTrackables()

        # The dates don't overlap at all
        if not trackableGroup.isValid():
            return datetime.now(), datetime.now()

        # When dealing with multiple trackables, we only want to be able to
        # select over the range where they both contain data
        self.bounds = trackableGroup.getBoundsForDateRange()
        if len(self.bounds) == 0:
            return

        startDate, endDate = self.bounds[0], self.bounds[-1]

        # Also update the editors to the maximum range
        # We don't want to trigger their update signals now
        self.startDateEditor.blockSignals(True)
        self.endDateEditor.blockSignals(True)
        # for w in [self.startDateEditor, self.endDateEditor]:
        #     w.setMinimumDate(startDate)
        #     w.setMaximumDate(endDate)
        self.startDateEditor.setDate(startDate)
        self.endDateEditor.setDate(endDate)
        self.startDateEditor.blockSignals(False)
        self.endDateEditor.blockSignals(False)

    def getSelectedStartEndDates(self):
        startDate = self.startDateEditor.date().toPyDate()
        endDate = self.endDateEditor.date().toPyDate()
        valid = startDate >= self.bounds[0] and endDate <= self.bounds[-1] and startDate <= endDate
        return valid, startDate, endDate

    def addFunctionOnChange(self, func):
        self.startDateEditor.dateChanged.connect(func)
        self.endDateEditor.dateChanged.connect(func)
