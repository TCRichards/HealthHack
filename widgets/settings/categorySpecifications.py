from widgets.binaryLogWidget import BinaryLogWidget
from widgets.continuousLogWidget import ContinuousLogWidget
from widgets.settings.panelType import PanelType

from util.paths import *


# This class will be useful when reading data from the settings file
class CategorySpecifications:

    def __init__(self, panelType, name, trackedTime, trackableNames, scoreWord='Servings'):
        self.panelType = panelType  # Button Widget or Checkbox Widget
        self.name = name
        self.trackableNames = trackableNames
        self.trackedTime = trackedTime
        self.scoreWord = scoreWord

        # Since the category's panel type will never change, statically assign whether it handles continuous or binary data now
        self.isBinary = self.panelType == PanelType.BINARY_LOG

    # Uses stored information to create a panel widget
    # Called from the UI's controller, which has access to button & spreadsheet functions
    def createPanel(self):
        if self.panelType == PanelType.BINARY_LOG:
            panel = BinaryLogWidget(self.name, self.trackableNames, self.trackedTime, self.scoreWord, self.isBinary)
        elif self.panelType == PanelType.CONTINUOUS_LOG:
            panel = ContinuousLogWidget(self.name, self.trackableNames, self.trackedTime, self.scoreWord, self.isBinary)
        else:
            raise TypeError('Specified Panel Type is not in the Enum PanelType')

        return panel
