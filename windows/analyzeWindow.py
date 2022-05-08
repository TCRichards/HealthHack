from PyQt5.QtWidgets import *
from PyQt5.QtGui import *
from PyQt5.QtCore import *

from util.settings import settings
from widgets.plotWidget import PlotWidget
from widgets.metricWidget import MetricWidget
from widgets.analysisControlWidget import AnalysisControlWidget
from windows.window import Window


class AnalyzeWindow(Window):

    def __init__(self, UI):
        super().__init__(UI)

    def create(self):

        if not settings.updated["Analyze"]:
            try:
                self.controlWidget.updateLayoutCombos()   # Prevents combos from last session from persisting
                return
            except AttributeError:
                return

        settings.updated["Analyze"] = False

        # In case this window has been created before, we destroy all components to avoid duplication
        self.reset()

        self.controlWidget = AnalysisControlWidget(self)
        self.plotWidget = PlotWidget(self)
        self.metricWidget = MetricWidget(self)

        self.fullLayout.addWidget(self.controlWidget)

        # Add the widgets for data visualization and analysis
        self.analysisLayout = QVBoxLayout()

        # Need to assign the stacked layout to a widget so we can add to fullLayout
        widg = QWidget()
        widg.setLayout(self.analysisLayout)
        self.fullLayout.addWidget(widg)
        self.analysisLayout.addWidget(self.plotWidget.widget)
        self.analysisLayout.addWidget(self.metricWidget)

        self.updateAnalysisWidgets()

    # Tells the plotWidget and metricWidget that there has been a change to the analyzed
    # trackable when the Update Analysis button is hit
    def updateAnalysisWidgets(self):
        # User should be prevented from accessing this method when invalid selection is made
        assert(self.getCurrentTrackables().isValid())
        self.plotWidget.updatePlot()
        self.metricWidget.updatePanels()

    def getCurrentTrackables(self):
        return self.controlWidget.getCurrentTrackables()

    # Destroys all active widgets if there are any
    def reset(self):
        try:
            self.fullLayout.removeWidget(self.metricWidget)
            self.metricWidget.setParent(None)
        except AttributeError:
            pass

        try:
            self.fullLayout.removeWidget(self.controlWidget)
            self.controlWidget.setParent(None)
        except AttributeError:
            pass

        try:
            self.fullLayout.removeWidget(self.plotWidget.widget)
            self.plotWidget.widget.setParent(None)
        except AttributeError:
            pass
