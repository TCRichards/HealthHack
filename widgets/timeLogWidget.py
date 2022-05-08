from PyQt5.QtWidgets import *
from PyQt5.QtGui import *
from PyQt5.QtCore import *

import pandas as pd

from .baseLogWidget import BaseLogWidget
from trackables.trackable import Trackable


class TimeLogWidget(BaseLogWidget):

    def __init__(self, panelName, buttonName):
        super().__init__(panelName, buttonName)

        self.button = QPushButton(buttonName, self)
        self.layout.addWidget(self.button)
        self.panelName = panelName

    def mapLogFunctionToButton(self, func):
        self.button.on_clicked.connnect(func)

    # All timing data is stored in an Excel sheet
    def getTrackables(self):
        df = pd.read_csv(self.getSpreadsheetPath(self.panelName))
        dates = df['Date'].tolist()
        times = df['Time'].tolist()

        makeListDateTimes(dates, '%m/%d/%Y')
        makeListDateTimes(times, '%H:%M')

        track = Trackable(dates, times, fillStrategy=(False, 0))
        return [track]
