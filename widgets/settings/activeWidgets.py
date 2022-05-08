
from PyQt5.QtWidgets import *
from PyQt5.QtGui import *
from PyQt5.QtCore import *

import os
from util.paths import *
import numpy as np

from util.settings import settings
import windows.settingsWindow as sw

from widgets.util.centeredLabel import CenteredLabel
from widgets.util.transparentButton import TransparentButton

from widgets.settings.popups import AddInputPopup


class AbstractActiveWidget(QWidget):

    def __init__(self, name, panelSpec, superLayout):
        super().__init__()

        self.name = name
        self.panelSpec = panelSpec
        self.superLayout = superLayout

        self.layout = QGridLayout()
        self.setLayout(self.layout)

        self.label = CenteredLabel(name)
        self.layout.addWidget(self.label)

        upBut = TransparentButton()
        upBut.setIcon(QIcon(os.path.join(imgPath, 'upIcon.png')))
        upBut.clicked.connect(lambda: self.move(-1))

        downBut = TransparentButton()
        downBut.setIcon(QIcon(os.path.join(imgPath, 'downIcon.png')))
        downBut.clicked.connect(lambda: self.move(1))

        removeBut = TransparentButton()
        removeBut.setIcon(QIcon(os.path.join(imgPath, 'redXIcon.jpg')))
        removeBut.clicked.connect(self.remove)

        self.layout.addWidget(upBut, 0, 1)
        self.layout.addWidget(downBut, 0, 2)
        self.layout.addWidget(removeBut, 0, 3)

    # @brief handles reordering the widget in the superLayout, with its new position
    # @param minIdx the number of UI elements before the range we're interested in
    # @param maxIdx the number of UI elements after the range we're interested in
    # constrained between minIdx and maxIdx.  Does not handle updating settings or JSON
    def move(self, offset, minIdx, maxIdx):
        curIdx = self.superLayout.indexOf(self)
        # don't allow movement outside of this range
        newIdx = np.clip(curIdx + offset, minIdx, maxIdx)

        # change order by removing and re-adding
        self.superLayout.removeWidget(self)
        self.superLayout.insertWidget(newIdx, self)
        return curIdx, newIdx

    # @brief handles removing the widget from the superLayout
    # Does not handle updating settings or JSON
    def remove(self):
        # remove from layout
        self.superLayout.removeWidget(self)
        self.setParent(None)


# @brief this class describes the horizontal label + buttons used to mark categories that are currently active
class ActiveCategoryWidget(AbstractActiveWidget):

    def __init__(self, panelSpec, categorySelector):
        super().__init__(panelSpec.name, panelSpec, categorySelector.layout)
        self.categorySelector = categorySelector

        # Also add a button to display more info and control inputs
        self.inputBut = TransparentButton()
        self.inputBut.setIcon(QIcon(os.path.join(imgPath, 'questionIcon.png')))
        self.inputBut.clicked.connect(self.openInputPopup)
        self.layout.addWidget(self.inputBut, 0, 4)

    def openInputPopup(self):
        AddInputPopup(self)

    # @brief change the order of this widget in the layout by offset units
    # constrained within the limits of the layout
    def move(self, offset):
        minIdx = 2
        maxIdx = self.superLayout.count() - 3
        curIdx, newIdx = super().move(offset, minIdx, maxIdx)

        # update the settings.json file to reflect new order
        if curIdx != newIdx:
            settings.categoryData[curIdx - minIdx], settings.categoryData[newIdx - minIdx] = \
                settings.categoryData[newIdx -
                                      minIdx], settings.categoryData[curIdx - minIdx]

            settings.writeSettings()
            sw.SettingsWindow.updateDisplay()

    def remove(self):
        super().remove()
        # remove from util.settings
        settings.removeCategory(self.panelSpec)
        settings.writeSettings()
        sw.SettingsWindow.updateDisplay()


# @brief UI element for a trackable belonging to a specific category
class ActiveTrackableWidget(AbstractActiveWidget):

    def __init__(self, name, panelSpec, superLayout):
        super().__init__(name, panelSpec, superLayout)

    # Change the order of a category's trackables
    def move(self, order):
        minIdx = 2
        maxIdx = self.superLayout.count()
        curIdx, newIdx = super().move(order, minIdx, maxIdx)

        if curIdx != newIdx:
            # Locate the category that we need to adjust
            for i in range(len(settings.categoryData)):
                spec = settings.categoryData[i][0]
                if settings.categoryData[i][0] == self.panelSpec:
                    # swap order of trackables in settings
                    spec.trackableNames[curIdx - minIdx], spec.trackableNames[newIdx - minIdx] = \
                        spec.trackableNames[newIdx - minIdx], spec.trackableNames[curIdx - minIdx]

                    settings.categoryData[i] = (spec, spec.createPanel())

            settings.writeSettings()
            sw.SettingsWindow.updateDisplay()

    def remove(self):
        super().remove()
        # Seems like self.panelSpec is a reference to settings.panelData, so modifying it through
        # settings also modifies here
        settings.removeTrackableFromPanelSpecByName(self.name, self.panelSpec.name)
        settings.writeSettings()
        sw.SettingsWindow.updateDisplay()
