from trackables.variableCategories.trackType import TrackType

from matplotlib.backends.backend_qt5agg import FigureCanvas
from matplotlib.backends.backend_qt5agg import NavigationToolbar2QT as NavigationToolbar

from matplotlib.figure import Figure
import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
import seaborn as sns

from PyQt5.QtWidgets import *
from PyQt5.QtGui import *
from PyQt5.QtCore import *

'''
HeatmapWidget class is responsible for populating the heatmap's matrix using statistical tests
in TrackableGroup and displaying the resulting heatmap on a FigureCanvas
'''


class HeatmapWidget(FigureCanvas):

    def __init__(self):
        self.fig = Figure()
        super().__init__(self.fig)

        # Set up layout
        layout = QVBoxLayout()
        self.widget = QWidget()
        self.widget.setLayout(layout)
        layout.addWidget(self)

        # Create axes for main heatmap and color bar simultaneously
        plot_grid = plt.GridSpec(
            1, 15, hspace=0.2, wspace=0.1)  # Setup a 1x15 grid
        # Use the leftmost 14 columns of the grid for the main plot
        self.ax = self.fig.add_subplot(plot_grid[:, :-1])
        # Use the rightmost column of the plot
        self.colorbar = self.fig.add_subplot(plot_grid[:, -1])

        self.toolbar = NavigationToolbar(self, self.widget)
        self.hidePlotBorders()

        layout.addWidget(self)
        layout.addWidget(self.toolbar)

    def trackableGroupToHeatmap(self, trackGroup, test='Pearson', lagDays=0):
        self.trackablesToHeatmap(
            trackGroup.getTrackables(), test=test, lagDays=lagDays)

    def trackablesToHeatmap(self, trackables, test='Pearson', lagDays=0):
        if len(trackables) < 2:
            print('Cannot make heatmap with less than 2 trackables')
            return

        self.ax.clear()
        corrMatrix = self.makeRelationshipMatrix(
            trackables, test, lagDays=lagDays)
        names = [t.name for t in trackables]
        corrDf = self.relationshipMatrixToDF(corrMatrix, names)
        self.displayHeatmap(
            x=corrDf['x'], y=corrDf['y'], size=corrDf['value'].abs(), color=corrDf['value'])

    # Taken from https://towardsdatascience.com/better-heatmaps-and-correlation-matrix-plots-in-python-41445d0f2bec
    # Displays and beautifies heatmap using precalculated pandas series x and y
    def displayHeatmap(self, x, y, size, color):
        n_colors = 256  # Use 256 colors for the diverging color palette
        palette = sns.diverging_palette(
            20, 220, n=n_colors)  # Create the palette
        # Range of values that will be mapped to the palette, i.e. min and max possible correlation
        color_min, color_max = [-1, 1]

        def value_to_color(val):
            # position of value in the input range, relative to the length of the input range
            val_position = float((val - color_min)) / (color_max - color_min)
            # target index in the color palette
            ind = int(val_position * (n_colors - 1))
            return palette[ind]

        # Mapping from column names to integer coordinates
        x_labels = [v for v in sorted(x.unique())]
        y_labels = [v for v in sorted(y.unique())]
        x_to_num = {p[1]: p[0] for p in enumerate(x_labels)}
        y_to_num = {p[1]: p[0] for p in enumerate(y_labels)}

        self.ax.set_xlim([-0.5, max([v for v in x_to_num.values()]) + 0.5])
        self.ax.set_ylim([-0.5, max([v for v in y_to_num.values()]) + 0.5])

        size_scale = 500
        self.ax.scatter(
            x=x.map(x_to_num),  # Use mapping for x
            y=y.map(y_to_num),  # Use mapping for y
            s=size * size_scale,  # Vector of square sizes, proportional to size parameter
            marker='s',  # Use square as scatterplot marker
            color=color.apply(value_to_color)
        )

        # Show column labels on the axes
        self.ax.set_xticks([x_to_num[v] for v in x_labels])
        self.ax.set_xticklabels(x_labels, rotation=45,
                                horizontalalignment='right')
        self.ax.set_yticks([y_to_num[v] for v in y_labels])
        self.ax.set_yticklabels(y_labels)

        # Add color legend on the right side of the plot
        col_x = [0]*len(palette)  # Fixed x coordinate for the bars
        # y coordinates for each of the n_colors bars
        bar_y = np.linspace(color_min, color_max, n_colors)

        bar_height = bar_y[1] - bar_y[0]
        self.colorbar.barh(
            y=bar_y,
            width=[6]*len(palette),  # Make bars 5 units wide
            left=col_x,  # Make bars start at 0
            height=bar_height,
            color=palette,
            linewidth=0
        )

        # Show vertical ticks for min, middle and max
        self.colorbar.set_yticks(np.linspace(min(bar_y), max(bar_y), 3))

        self.draw()

    def makeRelationshipMatrix(self, trackables, test, lagDays=0):
        # We need some way to index each trackable and compute the 'correlation' value between all elements
        corrs = np.zeros((len(trackables), len(trackables)))
        for i in range(len(trackables)):
            for j in range(len(trackables)):

                # No need to recalculate elements for symmetric tests (correlation with 0 lag)
                if lagDays == 0 and test.isSymmetric():
                    if corrs[i][j] != 0:
                        corrs[j][i] = corrs[i][j]
                        continue
                    if corrs[j][i] != 0:
                        corrs[i][j] = corrs[j][i]
                        continue

                # I don't currently have a way to deal with times, so skip
                # (leaves correlation as 0 which is fine)
                if trackables[i].getTrackType() == TrackType.TIME or \
                        trackables[j].getTrackType() == TrackType.TIME:
                    continue

                # compute the correlation for the current elements
                corrs[i][j] = test.runTestForLag(trackables[i], trackables[j], lag=lagDays)

        return corrs

    def relationshipMatrixToDF(self, corrMatrix, trackableNames):
        corrDf = pd.DataFrame(
            data=corrMatrix, index=trackableNames, columns=trackableNames)
        # Unpivot the dataframe, so we can get pair of arrays for x and y
        corrDf = pd.melt(corrDf.reset_index(), id_vars='index')
        corrDf.columns = ['x', 'y', 'value']
        return corrDf

    def hidePlotBorders(self):

        self.ax.grid(False, 'major')
        self.ax.grid(True, 'minor')
        self.ax.spines['top'].set_visible(False)
        self.ax.spines['right'].set_visible(False)
        self.ax.spines['left'].set_visible(False)
        self.ax.spines['bottom'].set_visible(False)
        self.ax.set_xticks([])
        self.ax.set_yticks([])

        self.colorbar.grid(False)  # Hide grid
        self.colorbar.spines['top'].set_visible(False)
        self.colorbar.spines['right'].set_visible(False)
        self.colorbar.spines['left'].set_visible(False)
        self.colorbar.spines['bottom'].set_visible(False)
        self.colorbar.set_facecolor('white')  # Make background white
        self.colorbar.set_xticks([])  # Remove horizontal ticks
        self.colorbar.set_yticks([])
        self.colorbar.yaxis.tick_right()  # Show vertical ticks on the right
