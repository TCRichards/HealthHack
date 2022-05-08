from PyQt5.QtWidgets import *
from PyQt5.QtGui import *
from PyQt5.QtCore import *


# Base class for creating widgets with set background colors
class ColoredWidget(QWidget):

    def __init__(self, qtColor):
        super().__init__()
        pal = QPalette()
        pal.setColor(QPalette.Background, qtColor)
        self.setPalette(pal)
        self.setAutoFillBackground(True)


class LightGrayWidget(ColoredWidget):

    def __init__(self):
        super().__init__(Qt.lightGray)


class BlackWidget(ColoredWidget):

    def __init__(self):
        super().__init__(Qt.black)


class DarkYellowWidget(ColoredWidget):

    def __init__(self):
        super().__init__(Qt.darkYellow)


class DarkGrayWidget(ColoredWidget):

    def __init__(self):
        super().__init__(Qt.darkGray)


class CyanWidget(ColoredWidget):

    def __init__(self):
        super().__init__(Qt.cyan)
