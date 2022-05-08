from PyQt5.QtWidgets import *
from PyQt5.QtGui import *
from PyQt5.QtCore import *

from util.paths import *
from util.settings import settings
import windows.settingsWindow as sw

from widgets.util.centeredLabel import CenteredLabel
from widgets.util.coloredWidgets import *
from widgets.settings.activeWidgets import ActiveCategoryWidget
from widgets.settings.popups import AddCategoryPopup


class AbstractSelector(QWidget):
    def __init__(self, bannerText):
        super().__init__()

        self.layout = QVBoxLayout()
        self.setLayout(self.layout)

        banner = CenteredLabel(bannerText)
        banner.setFont(QFont("Arial", 15))
        self.layout.addWidget(banner)

    def update(self):
        ...


class IntegrationSelector(AbstractSelector):
    def __init__(self):
        super().__init__("Integrations")

        self.buttonGroup = QButtonGroup()
        self.buttonGroup.setExclusive(False)

        # Layout just holding checkboxes -- need to align these center
        self.buttonLayout = QVBoxLayout()
        self.buttonLayout.setAlignment(Qt.AlignCenter)
        buttonBackground = QWidget()
        buttonBackground.setLayout(self.buttonLayout)
        self.layout.addWidget(buttonBackground)

        for idx, integration in enumerate(settings.getAllIntegrations()):
            newButton = QCheckBox(integration, self)
            self.buttonGroup.addButton(newButton, idx)
            self.buttonLayout.addWidget(newButton)
            newButton.clicked.connect(self.updateIntegrations)

            # Activate button if it's in the current settings
            if integration in settings.integrations:
                newButton.setChecked(True)
        # No reason for this to stretch
        self.layout.addStretch(1)

    def updateIntegrations(self):
        integrations = []
        for button in self.buttonGroup.buttons():
            if button.isChecked():
                integrations.append(button.text())

        # Update the rest of the app to reflect changed integration
        settings.integrations = integrations
        settings.categoryNames = [
            category.name for category in [x[0] for x in settings.categoryData]
        ] + integrations

        settings.writeSettings()
        sw.SettingsWindow.updateDisplay()


class CategorySelector(AbstractSelector):
    def __init__(self):
        super().__init__("Categories")

        self.activeAdjustors = [
            ActiveCategoryWidget(spec, self) for spec in settings.getCategorySpecs()
        ]
        self.layout.addWidget(CenteredLabel("Active Categories"))
        for adj in self.activeAdjustors:
            self.layout.addWidget(adj)

        self.addPanelButton = QPushButton("Add New Category", self)
        self.addPanelButton.clicked.connect(self.launchAddCategoryPopup)
        self.layout.addWidget(self.addPanelButton)

        # No reason for this to stretch
        self.layout.addStretch(1)

    def launchAddCategoryPopup(self):
        AddCategoryPopup(self)
