from trackables.trackables.trackables import UserBinaryTrackable, UserContinuousTrackable
from trackables.variableCategories.trackType import TrackType
from trackables.trackables.ouraData import Oura
from trackables.trackables.trackableFactories import OuraFactory, HabitFactory
from trackables.trackables.myFitnessMeals import MFPManager
import util.settings as set


class TrackableManager:

    _instance = None

    @staticmethod
    def instance():
        if not TrackableManager._instance:
            TrackableManager._instance = TrackableManager.__TrackableManager()

        return TrackableManager._instance

    class __TrackableManager:

        def __init__(self):

            # Deal with the optional integrations first
            self.trackables = []
            if 'Oura Ring' in set.settings.integrations:
                self.ouraTrackables = OuraFactory.getAllTrackables()
                self.trackables += self.ouraTrackables
            if 'MyFitnessPal' in set.settings.integrations:
                self.MFPManager = MFPManager()
                self.MFPTrackables = self.MFPManager.getTrackables()
                self.trackables += self.MFPTrackables
            if 'HabitBull' in set.settings.integrations:
                self.habitTrackables = HabitFactory.loadAllHabits()
                self.trackables += self.habitTrackables

            # Adds trackables from the user-logged panels
            for panel in [x[1] for x in set.settings.categoryData]:
                panelTrackables = panel.getTrackables()
                self.trackables += panelTrackables

            # Dictionary associating each panel's name with its corresponding trackables
            self.loggedTrackableDict = {p.panelName: p.getTrackables()
                                        for p in [x[1] for x in set.settings.categoryData]}

            # Look through each of the panel contained in the settings file for the trackable methods
            self.trackNameDict = {t.name: t for t in self.trackables}

        def addTrackableToPanel(self, category, trackableName, trackType):
            if trackType == TrackType.BINARY:
                newTrackable = UserBinaryTrackable(trackableName)
            else:
                newTrackable = UserContinuousTrackable(trackableName)
            self.trackables.append(newTrackable)
            self.trackNameDict[newTrackable.name] = newTrackable
            # keep self.loggedTrackableDict in sync with settings.categoryData
            self.loggedTrackableDict[category].append(newTrackable)

        def removeTrackableFromPanel(self, category, trackableName):
            if trackableName in self.trackNameDict.keys():
                trackToRemove = self.trackNameDict[trackableName]
                self.trackables.remove(trackToRemove)
                self.trackNameDict.pop(trackableName)
                if category in self.loggedTrackableDict.keys() and trackToRemove in self.loggedTrackableDict[category]:
                    # keep self.loggedTrackableDict in sync with settings.categoryData
                    self.loggedTrackableDict[category].remove(trackToRemove)

        # Searching the name dict field for the trackable with the given name
        def getTrackableFromName(self, name):
            try:
                return self.trackNameDict[name]
            except KeyError:
                raise KeyError(name + ' is not a valid trackable')

        def getOuraTrackableFromName(self, ouraCategory, name):
            trackList = self.getOuraTrackablesOfCategory(ouraCategory)
            for t in trackList:
                if t.name == name:
                    return t
            raise ValueError('Oura trackable of category {} and name {} not found'.format(
                ouraCategory, name))

        def getTrackablesOfCategory(self, category):
            if category == 'HabitBull':
                return self.habitTrackables
            elif category == 'MyFitnessPal':
                return self.MFPTrackables
            elif category == 'Oura':
                return self.ouraTrackables
            else:
                return self.loggedTrackableDict[category]

        def getOuraTrackablesOfCategory(self, ouraCategory):
            return Oura.instance().getTrackablesOfCategory(ouraCategory)

        def getAllTrackables(self):
            return self.trackables

        # Wrappers over previous getters that filter unanalyzable trackables for use in analysis
        def getAnalyzableTrackablesOfCategory(self, category):
            return list(filter(lambda t: t.isAnalyzable(), self.getTrackablesOfCategory(category)))

        def getAnalyzableOuraTrackablesOfCategory(self, ouraCategory):
            return list(filter(lambda t: t.isAnalyzable(), self.getOuraTrackablesOfCategory(ouraCategory)))

        def getAllAnalyzableTrackables(self):
            return list(filter(lambda t: t.isAnalyzable(), self.trackables))

        def getOuraCategories(self):
            return ['readiness', 'sleep', 'activity']

        def getCategories(self):
            allCats = set.settings.categoryNames
            if 'Oura Ring' in allCats and not self.foundOuraData():
                allCats.remove('Oura Ring')
            if 'HabitBull' in allCats and not self.foundHabitData():
                allCats.remove('HabitBull')
            return allCats

        def foundOuraData(self):
            return len(self.ouraTrackables) > 0

        def foundHabitData(self):
            return len(self.habitTrackables) > 0
