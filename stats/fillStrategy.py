from enum import Enum


# Enum describing how to collect data points for points for display and analysis
class FillStrategy(Enum):
    ZEROS = 1
    MEAN_EXCLUSIVE = 2
    MEAN_INCLUSIVE = 3
    FORWARD = 5
    BACKWARD = 6
    NONE = 7

    @staticmethod
    def mapStratStringToEnum(fillStr):
        fillMap = {
            'Fill with Zeros': FillStrategy.ZEROS,
            'Fill with Mean Excluding Missing Values': FillStrategy.MEAN_EXCLUSIVE,
            'Fill with Mean Including Missing Values': FillStrategy.MEAN_INCLUSIVE,
            'Forward Fill': FillStrategy.FORWARD,
            'Back Fill': FillStrategy.BACKWARD,
            'Don\'t Fill': FillStrategy.NONE
        }
        return fillMap[fillStr]

    @staticmethod
    def getDefaultStrategies():
        return [FillStrategy.ZEROS, FillStrategy.MEAN_INCLUSIVE, FillStrategy.MEAN_EXCLUSIVE, FillStrategy.FORWARD, FillStrategy.BACKWARD, FillStrategy.NONE]

    @staticmethod
    def getTimeStrategies():
        return [FillStrategy.MEAN_EXCLUSIVE, FillStrategy.FORWARD, FillStrategy.BACKWARD, FillStrategy.NONE]

    def toString(self):
        if self == FillStrategy.ZEROS:
            return 'Fill with Zeros'
        if self == FillStrategy.MEAN_EXCLUSIVE:
            return 'Fill with Mean Excluding Missing Values'
        if self == FillStrategy.MEAN_INCLUSIVE:
            return 'Fill with Mean Including Missing Values'
        if self == FillStrategy.FORWARD:
            return 'Forward Fill'
        if self == FillStrategy.BACKWARD:
            return 'Back Fill'
        if self == FillStrategy.NONE:
            return 'Don\'t Fill'
