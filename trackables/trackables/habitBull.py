from trackables.trackables.trackable import Trackable
from trackables.variableCategories.trackType import TrackType

from abc import ABC


# Subclass of Trackable that deals with habits imported from HabitBull
class HabitTrackable(Trackable, ABC):
    def __init__(self, name, habitDf):
        # Only way to tell whether Habitbull data is binary is based on presence of non 0-1 values
        super().__init__(name, habitDf)

    @staticmethod
    def getHabitFromName(habitList, name):
        for h in habitList:
            if h.name == name:
                return h
        raise ValueError("No habit with the name {} is found".format(name))
