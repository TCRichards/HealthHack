from PyQt5.QtWidgets import *
from PyQt5.QtGui import *
from PyQt5.QtCore import *


class TransparentButton(QPushButton):

    def __init__(self, text=None, parent=None):
        super().__init__(text, parent)
        self.setAttribute(Qt.WA_StyledBackground)
        #self.setStyleSheet('QPushButton{background: transparent;}')
        self.setStyleSheet("background-color: rgba(255, 255, 255, 0);")