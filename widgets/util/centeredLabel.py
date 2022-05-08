from PyQt5.QtWidgets import QLabel
from PyQt5.QtCore import Qt


# I got annoyed that I had to align QLabel text center every time to make it look good
class CenteredLabel(QLabel):

    def __init__(self, text, widget=None):
        if widget is not None:
            super().__init__(text, widget)
        else:
            super().__init__(text)

        self.setAlignment(Qt.AlignCenter)
