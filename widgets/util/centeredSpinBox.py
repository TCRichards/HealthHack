from PyQt5.QtWidgets import *
from PyQt5.QtGui import *
from PyQt5.QtCore import *

from widgets.util.centeredLabel import CenteredLabel


class CenteredSpinBox(QSpinBox):

    def __init__(self, parent):
        super().__init__(parent)
        self.setAlignment(Qt.AlignCenter)


class LabeledCenteredSpinBox(QWidget):

    def __init__(self, parent, labelText):
        super().__init__(parent)

        self.layout = QVBoxLayout()
        self.setLayout(self.layout)
        
        self.label = CenteredLabel(labelText)
        self.layout.addWidget(self.label)

        self.spin = CenteredSpinBox(parent)
        self.layout.addWidget(self.spin)

    def setVisible(self, vis):
        self.label.setVisible(vis)
        self.spin.setVisible(vis)
        super().setVisible(vis)

