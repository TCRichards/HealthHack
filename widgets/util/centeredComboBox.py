from PyQt5.QtWidgets import *
from PyQt5.QtGui import *
from PyQt5.QtCore import *

from widgets.util.centeredLabel import CenteredLabel


class CenteredComboBox(QComboBox):

    def __init__(self, parent=None):
        super().__init__(parent)

    # @overide
    def addItems(self, items):
        self.setEditable(True)
        super().addItems(items)

        # Center new text
        lineEdit = self.lineEdit()
        if lineEdit is not None:
            lineEdit.setReadOnly(True)
            lineEdit.setAlignment(Qt.AlignCenter)


class LabeledCenteredComboBox(QWidget):

    def __init__(self, parent, labelText):
        super().__init__(parent)

        self.layout = QVBoxLayout()
        self.setLayout(self.layout)

        self.label = CenteredLabel(labelText)
        self.layout.addWidget(self.label)

        self.combo = CenteredComboBox(parent)
        self.layout.addWidget(self.combo)

    def addItems(self, items):
        self.combo.addItems(items)

    def currentText(self):
        return self.combo.currentText()

    def setVisible(self, vis):
        self.label.setVisible(vis)
        self.combo.setVisible(vis)
        super().setVisible(vis)
