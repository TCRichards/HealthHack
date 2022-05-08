from enum import Enum


class PanelType(Enum):
    BINARY_LOG = 1,
    CONTINUOUS_LOG = 2,
    # TIME_LOG = 3

    def mapPanelTypeToEnum(typeStr):
        typeMap = {'Binary Log Widget': PanelType.BINARY_LOG,
                   'Continuous Log Widget': PanelType.CONTINUOUS_LOG}
        return typeMap[typeStr]

    def toString(self):
        if self == PanelType.BINARY_LOG:
            return 'Binary Log Widget'
        elif self == PanelType.CONTINUOUS_LOG:
            return 'Continuous Log Widget'
