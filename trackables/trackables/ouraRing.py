from trackables.trackables.trackable import Trackable
import trackables.trackables.ouraData as OD

from abc import ABC
from copy import deepcopy as copy


# Data source that deals with Oura Ring's categories
class OuraTrackable(Trackable, ABC):

    # TODO: Values are only properly downcast in single plotting mode and not for multiple variables
    def __init__(self, name, category, df):
        super().__init__(name, df)
        self.category = category

        # Certain measurements default to 0 if not recorded
        # For consistency with other data types, drop these measurements
        df.dropna(inplace=True)
        if (name == 'Rest Mode State'):  # Rest Mode uses 0's in a non-missing sense and uses NaNs for missing
            self.rawData = df
        else:
            try:
                self.rawData = df.drop(df.index[df['Score'] <= 1])
            except TypeError:
                # This strategy for recognizing missing data by 0's only works for numeric data
                self.rawData = df

        self.processedData = copy(self.rawData)

