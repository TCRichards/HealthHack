import json
from util.paths import settingsPath

from widgets.settings.categorySpecifications import CategorySpecifications
from widgets.settings.panelType import PanelType
from widgets.settings.logTime import LogTime

from trackables.trackableManager import TrackableManager as TM
from trackables.variableCategories.trackType import TrackType

'''
Reads the data input into the settings.JSON files
and creates the environment accordingly
'''


class Settings:

    def __init__(self):
        categorySpecs, self.integrations = self.readSettings()
        # list of tuples of format (panelSpec, panel class)

        self.categoryData = list(
            zip(categorySpecs, [c.createPanel() for c in categorySpecs]))

        # The names of all categories, not just the user-defined ones
        self.categoryNames = [category.name for category in
                              [x[0] for x in self.categoryData]] + self.integrations

        # Implement lazy loading of windows by only changing when settings
        # have been updated or on first load
        self.updated = {
            "Log": True,
            "Analyze": True,
            "Heatmap": True,
        }

# ======================== Read and Write to / from JSON ========================
    # @brief Reads the data stored in the settings.JSON file
    # @return tuple containing a list describing each panel and a list with
    # the name of enabled integratiosn
    def readSettings(self):
        with open(settingsPath, 'r') as read_file:
            data = json.load(read_file)
            panelSpecList = []
            for panel in data['Panels']:
                panelTypeString = panel['Panel Type']
                panelType = PanelType.mapPanelTypeToEnum(panelTypeString)
                panelName = panel['Name']
                inputs = panel['Inputs']
                timeStr = panel['Tracked Time']
                scoreWord = panel['Completion Word']
                logTime = LogTime.mapLogTimeToEnum(timeStr)

                specs = CategorySpecifications(
                    panelType, panelName, logTime, inputs, scoreWord)
                panelSpecList.append(specs)

            # Also check if the user has enabled any extras
            integrations = data['Integrations']

        return panelSpecList, integrations

    # Writes data for the current Settings object to the settings.JSON file
    def writeSettings(self):

        # Data need to be stored in a dict
        data = {
            'Panels': [
                {
                    'Panel Type': p.panelType.toString(),
                    'Name': p.name,
                    'Inputs': p.trackableNames,
                    'Tracked Time': p.trackedTime.toString(),
                    'Completion Word': p.scoreWord,
                }
                for p in self.getCategorySpecs()
            ],
            'Integrations': self.integrations
        }

        with open(settingsPath, 'w') as write_file:
            json.dump(data, write_file, indent=4)

        # Each time we write settings, need to reload all windows
        self.setUpdated()

# ================== Dynamically add / remove settings ========================

    # Appends the category to the categoryData list
    def addCategory(self, categorySpec):
        self.categoryData.append((categorySpec, categorySpec.createPanel()))

    # Because we assume settings' panels and panel
    def removeCategory(self, panelSpec):
        for i, cat in enumerate(self.categoryData):
            if cat[0].name == panelSpec.name:
                self.categoryData.pop(i)
                return

    def insertCategory(self, categorySpec, idx):
        self.categoryData.insert(
            idx, (categorySpec, categorySpec.createPanel()))

    # @brief updates the panel data by adding a new trackable to the entry
    # with matching name
    def addTrackableToPanelSpecByName(self, trackableName, panelSpecName):
        self.addOrRemoveTrackableToPanelSpecByName(trackableName, panelSpecName, True)

    def removeTrackableFromPanelSpecByName(self, trackableName, panelSpecName):
        self.addOrRemoveTrackableToPanelSpecByName(trackableName, panelSpecName, False)

    def addOrRemoveTrackableToPanelSpecByName(self, trackableName, panelSpecName, add):
        for i, data in enumerate(self.categoryData):
            if data[0].name == panelSpecName:
                if add:
                    data[0].trackableNames.append(trackableName)
                    trackType = TrackType.BINARY if data[0].isBinary else TrackType.CONTINUOUS
                    TM.instance().addTrackableToPanel(panelSpecName, trackableName, trackType)
                else:
                    assert(trackableName in data[0].trackableNames)
                    data[0].trackableNames.remove(trackableName)
                    TM.instance().removeTrackableFromPanel(panelSpecName, trackableName)
                self.categoryData[i] = (data[0], data[0].createPanel())
                return

    def getCategorySpecs(self):
        return [x[0] for x in self.categoryData]

    def getPanels(self):
        return [x[1] for x in self.categoryData]

    def getAllIntegrations(self):
        return ['MyFitnessPal', 'Oura Ring', 'HabitBull']

    # @brief marks that the settings have changed
    # and each window needs to be reloaded
    def setUpdated(self):
        self.updated = {
            "Log": True,
            "Analyze": True,
            "Heatmap": True,
        }

    # @brief sets analysis and heatmap windows to updated, doesn't modify log window
    def setAnalysisAndHeatmapUpdated(self):
        self.updated['Analyze'] = True
        self.updated['Heatmap'] = True


# Pass this settings object to various programs as a singleton
settings = Settings()
