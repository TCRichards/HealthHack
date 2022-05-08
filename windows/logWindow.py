from windows.window import Window
from util.settings import settings


class LogWindow(Window):

    def __init__(self, UI):
        super().__init__(UI)

    def create(self):
        if settings.updated["Log"]:
            self.clearAllWidgets()
            # Loads the panel name, type, and inputs from the provided settings.txt file
            # Initialize a panel object based on these specifications
            for panel in settings.getPanels():
                self.fullLayout.addWidget(panel)

            settings.updated["Log"] = False

    # @brief because we replace each logging widget each time the
    # settings are updated, we need to clear each time
    def clearAllWidgets(self):
        for i in reversed(range(self.fullLayout.count())):
            toRemove = self.fullLayout.itemAt(i).widget()
            self.fullLayout.removeWidget(toRemove)
            toRemove.setParent(None)
