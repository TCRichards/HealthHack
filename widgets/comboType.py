from enum import Enum


# Enum wrapping info about how data will be interpreted for plotting
class ComboType(Enum):

    @staticmethod
    def list():
        return [ComboType.SINGLE, ComboType.X, ComboType.Y]

    SINGLE = 0
    X = 1
    Y = 2

    # Descriptor for the purpose of data from the combo
    def getLabelText(self):
        if self == ComboType.SINGLE:
            return ''
        elif self == ComboType.X:
            return 'Independent '
        elif self == ComboType.Y:
            return 'Dependent '