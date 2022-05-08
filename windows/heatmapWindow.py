from windows.window import Window
from PyQt5.QtWidgets import *
from PyQt5.QtGui import *
from PyQt5.QtCore import *

import os

from widgets.heatmapWidget import HeatmapWidget
from widgets.util.centeredLabel import CenteredLabel
from widgets.util.centeredComboBox import CenteredComboBox
from widgets.util.centeredSpinBox import CenteredSpinBox
from widgets.util.transparentButton import TransparentButton

from trackables.trackableGroup import TrackableGroup
from trackables.trackableManager import TrackableManager as TM
from stats.test import Test

from util.settings import settings

collapsedIcon = QIcon(os.path.join(os.path.dirname(__file__), 'images/dropdownIcon_closed.png'))
expandedIcon = QIcon(os.path.join(os.path.dirname(__file__), 'images/dropdownIcon_open.png'))

class HeatmapWindow(Window):

    def __init__(self, UI):
        super().__init__(UI)
    

    def create(self):
        if not settings.updated["Heatmap"]:
            return
        settings.updated["Heatmap"] = False
        self.heatmapWidget = HeatmapWidget()

        # Layout defining the control panels on the left side with buttons
        self.controlLayout = QVBoxLayout()
        self.controlLayout.setAlignment(Qt.AlignTop)
        backgroundPanel = QWidget()
        backgroundPanel.setLayout(self.controlLayout)
        self.fullLayout.addWidget(backgroundPanel)

        self.mapLayout = QVBoxLayout()

        # Need to assign the stacked layout to a widget so we can add to fullLayout
        widg = QWidget()
        widg.setLayout(self.mapLayout)
        self.fullLayout.addWidget(widg)

        self.buttonGroups = []
        self.populateControlPanel()

        self.mapLayout.addWidget(self.heatmapWidget.widget)

    def populateControlPanel(self):
        updateButton = QPushButton(
            'Update Heatmap', self)
        updateButton.clicked.connect(self.updateHeatmap)
        self.controlLayout.addWidget(updateButton)
        self.addTestControlWidgets()
        for category in TM.instance().getCategories():

            # For oura ring, use sub-categories
            if category == 'Oura Ring':
                ouraHolder = OuraHolder()

                self.controlLayout.addWidget(ouraHolder)
                for subcat in TM.instance().getOuraCategories():
                    buttons = OuraRadioButtons(subcat)
                    self.controlLayout.addWidget(buttons)
                    self.buttonGroups.append((subcat, buttons))
                    ouraHolder.addOuraRadioButtonWidget(buttons)

            else:
                buttons = RadioButtons(category)
                self.controlLayout.addWidget(buttons)
                self.buttonGroups.append((category, buttons))
    
    def addTestControlWidgets(self):
        testLabel = CenteredLabel('Select Test')
        self.controlLayout.addWidget(testLabel)
        self.testCombo = CenteredComboBox(self)
        self.testCombo.addItems(Test.getTestNames())
        self.controlLayout.addWidget(self.testCombo)

        lagLabel = CenteredLabel('Select Days Offset')
        self.controlLayout.addWidget(lagLabel)
        self.lagSpinner = CenteredSpinBox(self)
        self.lagSpinner.setRange(0, 7)
        self.controlLayout.addWidget(self.lagSpinner)

        # Granger test can't be run for lag == 0, so constrain range when that is selected
        def adjustMinLag():
            mini = 0
            if self.testCombo.currentText() == 'Granger':
                mini = 1 
            self.lagSpinner.setMinimum(mini)
        
        self.testCombo.currentIndexChanged.connect(adjustMinLag)
    
    def updateHeatmap(self):

        selectedTrackables = []
        for entry in self.buttonGroups:
            category, buttonWidget = entry[0], entry[1]
            lookupFunc = TM.instance().getTrackableFromName if category != 'Oura Ring' \
                    else TM.instance().getOuraTracakbleFromName

            for i, button in enumerate(buttonWidget.buttons.buttons()):
                if i == 0 or not button.isChecked():    # Avoid unchecked or 'Select All' buttons
                    continue
                    
                selection = button.text()
                selectedTrackables.append(lookupFunc(selection))
        
        if len(selectedTrackables) == 0:
            return

        testName = self.testCombo.currentText()
        lagDays = self.lagSpinner.value()
        # Display the gathered trackables in the heatmap widget
        self.heatmapWidget.trackablesToHeatmap(selectedTrackables, testName, lagDays)


# Drop-down list that toggles whether the OuraRadioButtons are displayed
class OuraHolder(QWidget):

    def __init__(self):
        super().__init__()
        self.garbageParent = QWidget()

        self.layout = QVBoxLayout()
        self.layout.setAlignment(Qt.AlignTop)
        self.setLayout(self.layout)
    
        # Begin the UI with all dropdown lists closed to save space
        self.toggleButton = TransparentButton('Oura Ring', self)
        self.toggleButton.clicked.connect(self.toggleVisibility)
        self.toggleButton.setIcon(expandedIcon)
        self.layout.addWidget(self.toggleButton)
        
        self.radioWidgets = []
        self.isHidden = False
        
    def addOuraRadioButtonWidget(self, widg):
        self.radioWidgets.append(widg)

    def hide(self):
        for widg in self.radioWidgets:
            widg.layout.removeWidget(widg.toggleButton)
            widg.toggleButton.setParent(widg.garbageParent)
            widg.hide()

            self.toggleButton.setIcon(collapsedIcon)
        self.isHidden = True
        
    def show(self):
        for widg in self.radioWidgets:
            widg.layout.addWidget(widg.toggleButton)
            widg.toggleButton.setParent(widg)

            self.toggleButton.setIcon(expandedIcon)
        self.isHidden = False

    def toggleVisibility(self):
        if self.isHidden:
            self.show()
        else: 
            self.hide()
        self.adjustSize()

class AbstractRadioButtons(QWidget):

    def __init__(self, toggleName, trackables):
        super().__init__()

        self.SELECT = 'Select All'
        self.UNSELECT = 'Unselect All'

        self.garbageParent = QWidget()

        self.layout = QVBoxLayout()
        self.layout.setAlignment(Qt.AlignTop)
        self.setLayout(self.layout)
    
        # Begin the UI with all dropdown lists closed to save space
        self.toggleButton = TransparentButton(toggleName.capitalize(), self)
        self.toggleButton.clicked.connect(self.toggleVisibility)
        self.toggleButton.setIcon(collapsedIcon)
        self.layout.addWidget(self.toggleButton)

        self.buttons = QButtonGroup()
        self.buttons.setExclusive(False)

        self.selectAllButton = QCheckBox(self.SELECT, self.garbageParent)
        self.buttons.addButton(self.selectAllButton, 0)
        self.selectAllButton.stateChanged.connect(self.toggleSelectAll)

        trackableNames = [t.name for t in trackables]
        for idx, name in enumerate(trackableNames, 1):
            newButton = QCheckBox(name, self.garbageParent)
            self.buttons.addButton(newButton, idx)
            newButton.stateChanged.connect(self.updateAllButtonsSelected)
        
        self.hide()
    
    def getTrackableButtons(self):
        return self.buttons.buttons()[1:]
    
    def updateAllButtonsSelected(self):
        res = True
        for button in self.getTrackableButtons():
            res = res and button.isChecked()
        
        # Need a way to update self.selectAllButton without emitting its signal
        self.selectAllButton.stateChanged.disconnect()
        if res:
            self.selectAllButton.setChecked(True)
            self.selectAllButton.setText(self.UNSELECT)
        else:
            self.selectAllButton.setChecked(False)
            self.selectAllButton.setText(self.SELECT)

        self.selectAllButton.stateChanged.connect(self.toggleSelectAll)
        return res
    
    # 'Select All' button is pressed. Update other buttons based on its state
    def toggleSelectAll(self):
        if self.selectAllButton.isChecked() and self.selectAllButton.text() == self.SELECT:
            for button in self.getTrackableButtons():
                button.setChecked(True)
            self.selectAllButton.setText(self.UNSELECT)
        else:
            for button in self.buttons.buttons():
                button.setChecked(False)
            self.selectAllButton.setText(self.SELECT)

    def toggleVisibility(self):
        if self.isHidden:
            self.show()
        else: 
            self.hide()
        self.adjustSize()

    def show(self):
        for but in self.buttons.buttons():
            self.layout.addWidget(but)
            but.setParent(self)
            self.toggleButton.setIcon(expandedIcon)
        self.isHidden = False
    
    def hide(self):
        for but in self.buttons.buttons():
            self.layout.removeWidget(but)
            but.setParent(self.garbageParent)
            self.toggleButton.setIcon(collapsedIcon)
        self.isHidden = True

class RadioButtons(AbstractRadioButtons):

    def __init__(self, category):
        super().__init__(category, TM.instance().getAnalyzableTrackablesOfCategory(category))     
        
class OuraRadioButtons(AbstractRadioButtons):

    def __init__(self, subcategory):
        super().__init__(subcategory, TM.instance().getAnalyzableOuraTrackablesOfCategory(subcategory))

    








