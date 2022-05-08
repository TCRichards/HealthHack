from trackables.trackables.trackables import *
from trackables.variableCategories.trackType import TrackType
import trackables.trackables.ouraData as OD

from util.paths import habitDataPath
from util.dbInterface import DBInterface

import pandas as pd


class UserFactory:

    @staticmethod
    def create(name, df, trackType, logTime):
        if trackType == TrackType.CONTINUOUS:
            return UserContinuousTrackable(name, df, logTime)
        elif trackType == TrackType.BINARY:
            return UserBinaryTrackable(name, df, logTime)
        elif trackType == TrackType.TIME:
            return UserTimeTrackable(name, df)


class OuraFactory:

    @staticmethod
    def create(name, category, df):
        trackType = OD.Oura.instance().getOuraTypeFromName(category, name)
        # I don't currently know how to even begin supporting these
        if trackType in (
            TrackType.LIST,
            TrackType.HYPNOGRAM,
            TrackType.CONTINUOUS_5_MIN_WINDOW,
        ):
            return None

        if trackType == TrackType.CONTINUOUS:
            return OuraContinuousTrackable(name, category, df)
        elif trackType == TrackType.BINARY:
            return OuraBinaryTrackable(name, category, df)
        elif trackType == TrackType.TIME:
            return OuraTimeTrackable(name, category, df)

    @staticmethod
    def getAllTrackables():
        return OD.Oura.instance().getAllTrackables()


class HabitFactory:

    @staticmethod
    def create(name, df):
        trackType = TrackType.CONTINUOUS
        if len(df['Score']) == 0:
            trackType = TrackType.EMPTY
        if len(set(df['Score'])) <= 2:
            trackType = TrackType.BINARY

        if trackType == TrackType.CONTINUOUS:
            return HabitContinuousTrackable(name, df)
        elif trackType == TrackType.BINARY:
            return HabitBinaryTrackable(name, df)

    # Static Methods for loading habit data from existing spreadsheets
    @staticmethod
    def loadAllHabits():
        # Loads data from HabitBull's Excel output
        try:
            habitDf = pd.read_csv(habitDataPath)
        except FileNotFoundError:
            return []

        habitNames = habitDf['HabitName'].tolist()
        dates = habitDf['CalendarDate'].tolist()
        scores = habitDf['Value'].tolist()

        DBInterface.makeListDateTimes(dates, '%m/%d/%Y')

        # Create objects for all the unique habit names
        allDf = pd.DataFrame(data={
            'Date': dates,
            'Name': habitNames,
            'Score': scores
        })
        groupedHabits = dict(tuple(allDf.groupby('Name')))
        allHabits = []
        for rawDf in list(groupedHabits.values()):
            rawDf = rawDf.set_index('Date')
            habitDf = rawDf['Score'].to_frame()
            name = rawDf['Name'].to_list()[0]
            allHabits.append(HabitFactory.create(name, habitDf))
        return allHabits


class NutrientFactory:

    # Creates a nutrient trackable -- all nutrients are continuous
    @staticmethod
    def create(name, df):
        return NutrientContinuousTrackable(name, df)
