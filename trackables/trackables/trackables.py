from trackables.trackables.user import UserSource
from trackables.trackables.ouraRing import OuraTrackable
from trackables.trackables.habitBull import HabitTrackable
from trackables.trackables.myFitnessNutrient import NutrientTrackable
from trackables.variableCategories.binaryVariable import BinaryVariable
from trackables.variableCategories.timeVariable import TimeVariable
from trackables.variableCategories.continuousVariable import ContinuousVariable
from widgets.settings.logTime import LogTime

import pandas as pd


# ======================== User Trackables =================================
class UserContinuousTrackable(UserSource, ContinuousVariable):

    def __init__(self, name, df=pd.DataFrame({'Score': []}), logTime=LogTime.DATE):
        UserSource.__init__(self, name, df, logTime)


class UserBinaryTrackable(UserSource, BinaryVariable):
    def __init__(self, name, df=pd.DataFrame({'Score': []}), logTime=LogTime.DATE):
        UserSource.__init__(self, name, df, logTime)


class UserTimeTrackable(UserSource, TimeVariable):
    def __init__(self, name, df=pd.DataFrame({'Score': []})):
        UserSource.__init__(self, name, df)


# ========================= Habit Ring Trackables =============================
class OuraContinuousTrackable(OuraTrackable, ContinuousVariable):

    def __init__(self, name, category, df):
        OuraTrackable.__init__(self, name, category, df)


class OuraBinaryTrackable(OuraTrackable, BinaryVariable):
    def __init__(self, name, category, df):
        OuraTrackable.__init__(self, name, category, df)


class OuraTimeTrackable(OuraTrackable, TimeVariable):
    def __init__(self, name, category, df):
        df['Score'] = df['Score'].apply(lambda x: pd.to_datetime(x[11:19], format='%H:%M:%S'))
        # Consider ending above statement with .time()
        OuraTrackable.__init__(self, name, category, df)


# =============== Habitbull Trackables (Doesn't Support Time) ============================
class HabitContinuousTrackable(HabitTrackable, ContinuousVariable):
    def __init__(self, name, df):
        HabitTrackable.__init__(self, name, df)


class HabitBinaryTrackable(HabitTrackable, BinaryVariable):
    def __init__(self, name, df):
        HabitTrackable.__init__(self, name, df)


# =============== My Fitness Pal Nutrients ========================================
class NutrientContinuousTrackable(NutrientTrackable, ContinuousVariable):
    def __init__(self, name, df):
        NutrientTrackable.__init__(self, name, df)