from PyQt5.QtWidgets import *
from PyQt5.QtGui import *
from PyQt5.QtCore import *

from util.paths import *

from windows.window import Window
from widgets.settings.selectors import IntegrationSelector, CategorySelector


# @brief this is the window where we can modify the settings.JSON file to control program flow
class SettingsWindow(Window):

    JSONPanel = None
    debug = False

    def __init__(self, UI):
        super().__init__(UI)

        if SettingsWindow.debug:
            with open(settingsPath, 'r') as settingsFile:
                SettingsWindow.JSONPanel = QLabel(settingsFile.read())
                self.fullLayout.addWidget(SettingsWindow.JSONPanel)

        self.fullLayout.addWidget(IntegrationSelector())
        self.fullLayout.addWidget(CategorySelector())

    # Only display the JSON file in the settings window in debug setting
    @staticmethod
    def updateDisplay():
        if SettingsWindow.debug:
            with open(settingsPath, 'r') as settingsFile:
                SettingsWindow.JSONPanel.setText(settingsFile.read())
