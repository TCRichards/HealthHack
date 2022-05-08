from PyQt5.QtWidgets import *
from PyQt5.QtGui import *
from PyQt5.QtCore import *


class Window(QWidget):

    def __init__(self, UI=None):
        super().__init__()
        self.fullLayout = QHBoxLayout()
        self.UI = UI
        self.fullLayout.setAlignment(Qt.AlignTop)
        palette = self.palette()
        palette.setColor(self.backgroundRole(), Qt.white)
        self.setPalette(palette)
        self.setAutoFillBackground(True)
        self.setLayout(self.fullLayout)

    def formatDate(self, dateObj):
        return dateObj.toString('MM/dd/yyyy')

    def formatTime(self, timeObj):
        return timeObj.toString('HH:mm')

    # Abstract method describing how to create this object
    # Essentially the constructor, but allows delaying creation
    def create(self):
        ...
