from PyQt5.QtWidgets import *
from PyQt5.QtGui import *
from PyQt5.QtCore import *

from util.paths import *

from util.settings import settings
import windows.settingsWindow as sw

from widgets.util.centeredLabel import CenteredLabel
from widgets.settings.categorySpecifications import CategorySpecifications
from widgets.settings.panelType import PanelType
from widgets.settings.logTime import LogTime
import widgets.settings.activeWidgets as aw


# @brief The popup that appears when user selects 'Add Category' that accepts input and adds
# a new category to the settings file
class AddCategoryPopup(QDialog):

    def __init__(self, categorySelector):
        super().__init__()
        self.setWindowTitle('Add New Category')
        self.setWindowIcon(QIcon(os.path.join(imgPath, 'questionIcon.png')))

        self.categorySelector = categorySelector

        self.layout = QVBoxLayout()
        self.setLayout(self.layout)

        self.createTypeSelection()
        self.createLogTimeSelection()

        inputLabel = CenteredLabel('Input New Category Name and Press Return')
        self.textBox = QLineEdit(self)
        self.textBox.returnPressed.connect(self.submit)

        self.layout.addWidget(inputLabel)
        self.layout.addWidget(self.textBox)
        self.layout.addStretch(1)

        self.exec()

    def createTypeSelection(self):
        typeBanner = CenteredLabel('Select Widget to Track Category')
        self.layout.addWidget(typeBanner)

        self.typeButtonLayout = QVBoxLayout()
        self.typeButtonLayout.setAlignment(Qt.AlignCenter)
        typeButtonBackground = QWidget()
        typeButtonBackground.setLayout(self.typeButtonLayout)
        self.layout.addWidget(typeButtonBackground)

        self.typeButtonGroup = QButtonGroup()  # which type of panel will it be?
        self.typeButtonGroup.setExclusive(True)

        for idx, integration in enumerate([p.toString() for p in PanelType]):
            newButton = QCheckBox(integration, self)
            self.typeButtonGroup.addButton(newButton, idx)
            self.typeButtonLayout.addWidget(newButton)

    def createLogTimeSelection(self):
        typeBanner = CenteredLabel('Select Data About Time To Track')
        self.layout.addWidget(typeBanner)

        self.timeButtonLayout = QVBoxLayout()
        self.timeButtonLayout.setAlignment(Qt.AlignCenter)
        timeButtonBackground = QWidget()
        timeButtonBackground.setLayout(self.timeButtonLayout)
        self.layout.addWidget(timeButtonBackground)

        self.timeButtonGroup = QButtonGroup()  # which type of panel will it be?
        self.timeButtonGroup.setExclusive(True)

        for idx, integration in enumerate([t.toString() for t in LogTime]):
            newButton = QCheckBox(integration, self)
            self.timeButtonGroup.addButton(newButton, idx)
            self.timeButtonLayout.addWidget(newButton)

    # @brief adds the new category to the settings file
    def submit(self):
        newName = self.textBox.text()
        self.textBox.clear()

        checkedTypeBut = self.typeButtonGroup.checkedButton()
        checkedTimeBut = self.timeButtonGroup.checkedButton()
        if newName == '' or checkedTimeBut is None or checkedTypeBut is None:
            return

        pTypeStr = checkedTypeBut.text()
        panelType = PanelType.mapPanelTypeToEnum(pTypeStr)

        timeSelectStr = checkedTimeBut.text()
        logTime = LogTime.mapLogTimeToEnum(timeSelectStr)

        newPanel = CategorySpecifications(panelType, newName, logTime, [])
        settings.addCategory(newPanel)
        settings.writeSettings()
        sw.SettingsWindow.updateDisplay()

        # Insert the new category widget at the bottom, but still
        # before the "Add Category" button
        self.categorySelector.layout.insertWidget(
            self.categorySelector.layout.count() - 2,
            aw.ActiveCategoryWidget(newPanel, self.categorySelector))

        self.close()


# @brief popup window that allows us to adjust the inputs to this category
class AddInputPopup(QDialog):

    def __init__(self, activeCategoryWidget):
        super().__init__()
        self.setWindowTitle(f'Adjust Variables for {activeCategoryWidget.name}')
        self.setWindowIcon(QIcon(os.path.join(imgPath, 'questionIcon.png')))

        self.layout = QVBoxLayout()
        self.setLayout(self.layout)
        self.panelSpec = activeCategoryWidget.panelSpec

        inputLabel = CenteredLabel('Type New Variable Name and Press Return')
        self.textBox = QLineEdit(self)
        self.textBox.returnPressed.connect(self.addUserTrackable)

        self.layout.addWidget(inputLabel)
        self.layout.addWidget(self.textBox)

        for track in self.panelSpec.trackableNames:
            self.addTrackableWidget(track)

        self.exec()

    def addUserTrackable(self):
        text = self.textBox.text()
        self.textBox.clear()
        self.addTrackableWidget(text)
        settings.addTrackableToPanelSpecByName(text, self.panelSpec.name)
        settings.writeSettings()
        sw.SettingsWindow.updateDisplay()

    def addTrackableWidget(self, name):
        newInput = aw.ActiveTrackableWidget(name, self.panelSpec, self.layout)
        self.layout.addWidget(newInput)
