from PyQt5.QtWidgets import *
from PyQt5.QtGui import *
from PyQt5.QtCore import *

from widgets.util.centeredLabel import CenteredLabel


class LabeledHorizontalButtons(QWidget):

    def __init__(self, label, names, exclusive=False, setFirstChecked=False, funcOnClick=None):
        super().__init__()
        fullLayout = QVBoxLayout()
        self.setLayout(fullLayout)
        fullLayout.addWidget(CenteredLabel(label))

        buttonLayout = QHBoxLayout()
        buttonBackground = QWidget()
        buttonBackground.setLayout(buttonLayout)
        fullLayout.addWidget(buttonBackground)

        self.buttons = QButtonGroup()
        self.buttons.setExclusive(True)
        for idx, name in enumerate(names):
            newButton = QCheckBox(name, self)
            self.buttons.addButton(newButton, idx)
            buttonLayout.addWidget(newButton)
            if funcOnClick is not None:
                newButton.clicked.connect(funcOnClick)

            if idx == 0 and setFirstChecked:
                newButton.setChecked(True)

    def setIdxEnabled(self, idx, enable):
        self.buttons.buttons()[idx].setEnabled(enable)

    def setIdxChecked(self, idx, check):
        self.buttons.buttons()[idx].setChecked(check)
