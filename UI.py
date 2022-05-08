from PyQt5.QtWidgets import *
from PyQt5.QtGui import *
from PyQt5.QtCore import *

import sys
import os
from util.paths import *

# To avoid circular dependencies, the app must be initialized before any windows are launched
app = QApplication(sys.argv)
from windows.logWindow import LogWindow
from windows.analyzeWindow import AnalyzeWindow
from windows.heatmapWindow import HeatmapWindow
from windows.settingsWindow import SettingsWindow


# The driver program for the application
# Defines a UI class with a toolbar that contains the program's primary windows
class UI(QMainWindow):

    def __init__(self):
        super().__init__()

        # Give the app a name and nice icon
        self.setWindowTitle('Health Data')
        iconPath = os.path.join(os.path.dirname(__file__), 'images', 'mainIcon.png')
        self.setWindowIcon(QIcon(iconPath))

        # Creates the stackedlayout and adds a button to switch between windows
        self.stackedLayout = QStackedLayout()
        # Use a stacked layout, which allows multiple tabs
        self.stackedLayout.setAlignment(Qt.AlignTop)
        self.stackedLayout.setStackingMode(QStackedLayout.StackOne)

        self.createToolBar()
        self.analyzeWindow = AnalyzeWindow(self)
        self.logWindow = LogWindow(self)
        # Don't support heatmap for now
        # self.heatmapWindow = HeatmapWindow(self)
        self.settingsWindow = SettingsWindow(self)

        self.stackedLayout.addWidget(self.settingsWindow)
        self.stackedLayout.addWidget(self.logWindow)
        self.stackedLayout.addWidget(self.analyzeWindow)
        # self.stackedLayout.addWidget(self.heatmapWindow)

        self.stackedLayout.setCurrentWidget(self.settingsWindow)

        backgroundWidget = QWidget()
        backgroundWidget.setLayout(self.stackedLayout)
        self.setCentralWidget(backgroundWidget)
        self.show()

        # Set size and size constraints
        resolution = QDesktopWidget().availableGeometry(self)
        self.resize(resolution.size() * 0.95)
        self.move((resolution.width() // 2) - (self.frameSize().width() // 2),
                  (resolution.height() // 2) - (self.frameSize().height() // 2))
        self.setMinimumSize(int(resolution.width() * 0.9), int(resolution.height() * 0.9))

    # Create buttons to jump to each of the windows in the app
    def createToolBar(self):
        def addJumpButton(iconPath, switchFunc, buttonName, shortcutKey):
            action = QAction(QIcon(os.path.join(imgPath, iconPath)), buttonName, self)
            action.setShortcut(shortcutKey)
            action.triggered.connect(switchFunc)

            self.toolBar = self.addToolBar(buttonName)
            self.toolBar.addAction(action)

        addJumpButton('settingsIcon.jpg', lambda: self.stackedLayout.setCurrentIndex(0), 'Settings', 'S')
        addJumpButton('logIcon2.png', self.activateLogWindow, 'Log', 'L')
        addJumpButton('analysisIcon.png', self.activateAnlyzeWindow, 'Analysis', 'A')
        # addJumpButton('heatmapIcon.png', self.activateHeatmapWindow, 'Heatmap', 'H')

    # Called whenever the toolbar action is taken.  Alternates between active windows
    def switchWindow(self, idx):
        self.stackedLayout.setCurrentIndex(idx)

    def activateLogWindow(self):
        self.stackedLayout.setCurrentIndex(1)
        self.logWindow.create()

    def activateAnlyzeWindow(self):
        self.stackedLayout.setCurrentIndex(2)
        self.analyzeWindow.create()

    # def activateHeatmapWindow(self):
    #     self.stackedLayout.setCurrentIndex(3)
    #     self.heatmapWindow.create()


if __name__ == '__main__':
    ui = UI()
    sys.exit(app.exec_())
