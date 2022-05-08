from trackables.trackables.trackable import Trackable
from abc import ABC


class NutrientTrackable(Trackable, ABC):

    def __init__(self, name, df):
        # Let's assume for now that we only care about daily reports from MFP
        super().__init__(name, df)
        # Combines all of the meal entries into a single entry for the day
        self.combineDuplicateDates()
