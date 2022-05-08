from PyQt5.QtWidgets import *
from PyQt5.QtGui import *
from PyQt5.QtCore import *

from widgets.util.centeredLabel import CenteredLabel
from widgets.settings.logTime import LogTime


# Panel that contains a label and a dateTimeEditor for use in other widgets
class DateTimeWidget(QWidget):

    def __init__(self, logTime, panelLabel='Time of Event'):
        super().__init__()
        self.logTime = logTime
        layout = QVBoxLayout()
        panel = QWidget()
        panel.setLayout(layout)

        if logTime == LogTime.DATE:
            dateTimeEditor = QDateEdit()
            timeLabel = CenteredLabel('Date of Event')
        else:
            dateTimeEditor = QDateTimeEdit()
            dateTimeEditor.setTime(QTime.currentTime())
            timeLabel = CenteredLabel('Date and Time of Event')

        layout.addWidget(timeLabel)
        dateTimeEditor.setDate(QDate.currentDate())
        dateTimeEditor.resize(150, 35)
        # Center text
        lineEdit = dateTimeEditor.lineEdit()
        lineEdit.setAlignment(Qt.AlignCenter)
        layout.addWidget(dateTimeEditor)

        self.dateTimeEditor = dateTimeEditor
        self.panel = panel

    # @brief formats a date objection to 'MM/dd/yyyy"
    def formatDate(self, dateObj):
        return dateObj.toString('MM/dd/yyyy')

    # @brief formats a time object to 'HH:mm"
    def formatTime(self, timeObj):
        return timeObj.toString('HH:mm')

    # @return the selected time if supported, or None if not
    def getSelectedTime(self):
        if self.logTime == LogTime.DATE:
            return None
        return self.formatTime(self.dateTimeEditor.time())

    def getSelectedDate(self):
        return self.formatDate(self.dateTimeEditor.date())

    def getSelectedDateAndTime(self):
        return self.getSelectedDate(), self.getSelectedTime()
