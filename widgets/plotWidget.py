from matplotlib.backends.backend_qt5agg import FigureCanvas
from matplotlib.backends.backend_qt5agg import NavigationToolbar2QT as NavigationToolbar
import numpy as np
import pandas as pd
from enum import Enum
from copy import deepcopy as copy
from scipy.interpolate import make_interp_spline

from matplotlib.figure import Figure
import matplotlib.dates as mdates

from PyQt5.QtWidgets import *
from PyQt5.QtGui import *
from PyQt5.QtCore import *
from stats.fillStrategy import FillStrategy

from trackables.variableCategories.trackType import TrackType
from stats.frequency import Frequency


class PlotWidget(FigureCanvas):

    def __init__(self, analyzeWindow):
        self.fig = Figure()
        super().__init__(self.fig)

        layout = QVBoxLayout()
        self.widget = QWidget()
        self.widget.setSizePolicy(
            QSizePolicy.MinimumExpanding, QSizePolicy.MinimumExpanding)
        self.widget.setLayout(layout)

        self.axes = self.fig.add_subplot(111)
        self.ax2 = self.axes.twinx()    # Create a second y-axis for multi-plotting
        self.ax2.set_axis_off()
        FigureCanvas(Figure(facecolor='black'))
        layout.addWidget(self)

        self.toolbar = NavigationToolbar(self, self.widget)
        layout.addWidget(self.toolbar)

        # Need a reference to the analyze window to view selected trackables
        self.analyzeWindow = analyzeWindow

    def updatePlot(self):
        currentTrackables = self.analyzeWindow.getCurrentTrackables().getTrackables()
        if len(currentTrackables) > 1:
            self.plotMultiple(currentTrackables)
        else:
            self.plotSingle(currentTrackables[0])

    # Plots the selected trackable's scores vs. dates
    def plotSingle(self, trackable):
        self.clearPlot()
        self.ax2.set_axis_off()
        self.drawTrackable(trackable)

    # Plots the scores for one trackable w.r.t. the other to find correlations
    def plotMultiple(self, trackableList):
        self.ax2.set_axis_on()
        colors = ['blue', 'red', 'black', 'green', 'orange']
        self.clearPlot()
        for i, t in enumerate(trackableList):
            self.drawTrackable(t, color=colors[i], isSecond=(i == 1))

    def drawTrackable(self, trackable, color='blue', isSecond=False):
        # Extract data from the trackable
        x_range = trackable.getSelectedDates()
        # When dealing with times, we have to do some shifting that we don't want to change trackable's state
        y_range = copy(trackable.getSelectedDateScores())

        # matplotlib hangs when we try to plot all nans, so fill single with fake
        try:
            if np.all([np.isnan(y) for y in y_range]):
                y_range[0] = -100000
        except TypeError:      # This doesn't matter when working with times
            pass

        x_label = 'Dates'
        y_label = trackable.name
        y_type = trackable.getTrackType()
        freq = trackable.frequency
        ax = self.axes if not isSecond else self.ax2

        try:
            # map duration in secs to hours (temp fix)
            if y_type == TrackType.DURATION:
                y_range = y_range / 3600

            ax.set_xlabel(x_label)
            ax.set_ylabel(y_label)

            self.formatPlotDates(x_range, y_range,
                                 y_type, freq, useAx2=isSecond)

            plotMarker = '-o'
            if y_type in [TrackType.TIME, TrackType.CONTINUOUS] and len(set(y_range)) > 10:
                self.addSpline(trackable, x_range, y_range, y_type, color, ax)
                plotMarker = 'o'

            ax.plot(x_range, y_range, plotMarker, label=trackable.name, color=color)  # Plot the spline without markers

            if freq == Frequency.DAILY:
                # This will be trickier when figuring out weekly or monthly
                # Add X marks over missing dates
                missingDates = trackable.getMissingDates()
                missingVals = np.array([])
                if y_type == TrackType.TIME:
                    missingVals.dtype = 'datetime64[ns]'
                xList = list(x_range)
                startIdx = 0    # Since missing dates are sorted, constantly update start of searched indices

                for md in missingDates:
                    try:
                        idx = xList.index(md, startIdx, len(xList))
                        startIdx = idx
                        missingVals = np.append(y_range[idx], missingVals)
                    except ValueError:
                        pass
                    except TypeError:
                        pass

                if len(missingDates) == len(missingVals):
                    # Hope that missingVals and missingDates are the same dimensions
                    # This won't be the case if not filling missing data
                    ax.plot(missingDates, missingVals, 'x', markersize=12, color=color)

            if y_type != TrackType.TIME:
                for tick in ax.get_yticklabels():
                    tick.set_color(color)
                # For some reason this can hang when plotting certain times, so have timeout if it doesn't work
                ax.yaxis.label.set_color(color)

            if isSecond:
                # Combine all axis handles into a single legend
                lines1, labels1 = self.axes.get_legend_handles_labels()
                lines2, labels2 = self.ax2.get_legend_handles_labels()
                self.ax2.legend(lines1 + lines2, labels1 + labels2, loc=0)

            self.draw()
        except ValueError:
            print('Tried Plotting Data of different dimensions.  Figure out how to enforce uniform size, or only plot over the smaller range')

    # @brief Add a cubic spline to the data being plotted to smooth curves
    def addSpline(self, trackable, x_range, y_range, y_type, color, ax):
        if trackable.fillStrategy != FillStrategy.NONE:
            xSpline = pd.date_range(x_range.min(), x_range.max(), periods=10 * len(x_range))
            if y_type == TrackType.TIME:
                # Convert datetime to seconds, spline, then convert spline back to datetime
                timeIdxs = pd.DatetimeIndex(y_range)
                # This stores the number of seconds from the beginning of the given
                seconds = [(3600 * t.hour) + (60 * t.minute) + t.second for t in timeIdxs]
                xySpline = make_interp_spline(x_range, seconds)
                splineSeconds = xySpline(xSpline)
                # Add a flat number of seconds to bring the measure to the seconds since the epoch, not just the beginning of the day
                secsFrom1900To1970 = 2208988800
                splinedTimes = np.array([pd.Timestamp(s - secsFrom1900To1970, unit='s').to_datetime64() for s in splineSeconds], dtype='datetime64[ns]')
                ax.plot(xSpline, splinedTimes, color=color)
            else:
                xySpline = make_interp_spline(x_range, y_range)
                ySpline = xySpline(xSpline)
                ax.plot(xSpline, ySpline, color=color)   # Plot the spline without markers

    def clearPlot(self):
        self.axes.clear()
        self.ax2.clear()

    def formatPlotDates(self, x_range, y_range, y_type, freq, useAx2=False):
        ax = self.axes if not useAx2 else self.ax2

        months = mdates.MonthLocator()          # every month
        # Every week starting on Monday
        weeks = mdates.WeekdayLocator(byweekday=mdates.MO)
        days = mdates.DayLocator()              # Mark every day
        years = mdates.YearLocator()

        if y_type == TrackType.TIME:
            ax.yaxis.set_major_locator(mdates.HourLocator())
            ax.yaxis.set_major_formatter(mdates.DateFormatter('%H:%M'))

            '''
            Matplotlib doesn't like wrapping the y_range around multiple days
            The following lines shift the boundaries to work for bedtime
            # Copy of TimeVariable.shiftOvernightTimes, but deals with numpy timedelta
            # I can only figure out how to extract hours when converted to pandas timestamp -- annoying
            # If these events happen on different sides of midnight then manually set ylimits
            # I'm assuming that bedtimes are the only measurements done in the range of hours
            # between 11 PM and 1 AM
            '''
            plottedHours = [pd.Timestamp(y).hour for y in y_range]
            if min(plottedHours) <= 1 and max(plottedHours) >= 23:
                # adjust the dates of the entries on the following day
                for i in range(len(plottedHours)):
                    # I could further tune measurements to be 'Morning', 'Night', or 'Any Time'
                    if plottedHours[i] <= 6:  # 4:00 is when oura defines a new day, but 6:00 seems reasonable
                        y_range[i] += np.timedelta64(1, 'D')

        # Format x data as dates
        formatter = mdates.DateFormatter('%m/%d/%Y')

        # Choose whether to highlight days,weeks or months based on number of data points
        numDays = pd.to_timedelta(x_range[-1] - x_range[0], unit='d').days
        if freq == Frequency.YEARLY or numDays > 365:
            ax.xaxis.set_major_locator(years)
        elif freq == Frequency.MONTHLY or numDays > 50:
            ax.xaxis.set_major_locator(months)
        elif freq == Frequency.WEEKLY or numDays > 20:
            ax.xaxis.set_major_locator(weeks)
        else:
            ax.xaxis.set_major_locator(days)

        ax.xaxis.set_minor_locator(days)
        ax.xaxis.set_major_formatter(formatter)

        # So the cursor highlights the date in the desired format
        ax.format_xdata = formatter
        self.fig.autofmt_xdate(rotation=80)


# To support varied data formats, we have to change plotting logic
# Based on format
class AxisFormat(Enum):
    VALUE = 0
    TIME = 1
    DATE = 2
