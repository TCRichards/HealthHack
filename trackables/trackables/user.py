from trackables.trackables.trackable import Trackable
from widgets.settings.logTime import LogTime


class UserSource(Trackable):

    def __init__(self, name, df, logTime=LogTime.DATE):
        super().__init__(name, df)
        self.logTime = logTime
