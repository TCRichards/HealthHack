from PyQt5.QtWidgets import *
from PyQt5.QtGui import *
from PyQt5.QtCore import *

from widgets.util.centeredLabel import CenteredLabel
from widgets.util.centeredComboBox import CenteredComboBox


class ComboBoxWidget(QWidget):

    def __init__(self, labelName, items):
        super().__init__()
        layout = QVBoxLayout()
        widget = QWidget()
        widget.setLayout(layout)

        label = CenteredLabel(labelName, self)
        layout.addWidget(label)

        combo = CenteredComboBox(self)
        combo.addItems(items)
        layout.addWidget(combo)

        self.combo = combo
        self.widget = widget
        self.label = label

    def getSelectedText(self):
        return self.combo.currentText()

    def addFunctionOnChange(self, func):
        self.combo.currentIndexChanged.connect(func)

    def disconnectSignals(self):
        self.combo.currentIndexChanged.disconnect()

    def setItems(self, items):
        self.combo.clear()
        self.combo.addItems(items)

    def setVisible(self, vis):
        self.combo.setVisible(vis)
        self.widget.setVisible(vis)

    def setText(self, text):
        self.label.setText(text)
