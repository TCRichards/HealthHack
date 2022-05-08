from stats.test import Test
from scipy.stats import linregress


class PearsonTest(Test):

    def __init__(self):
        super().__init__('Pearson', 'Linear Regression', True)

    # For now this is just univariate
    def runValidTestForLag(self, dependentT, independentT, lag=1):
        backIdx = -lag if lag > 0 else len(
            dependentT.getSelectedDateScores())
        x_data = independentT.getSelectedDateScores()[lag:]
        y_data = dependentT.getSelectedDateScores()[:backIdx]

        try:
            res = linregress(x_data, y_data)
            r2, p = res[2] ** 2, res[3]
            return r2, p

        # This happens sometimes -- I don't really know why
        except ValueError:
            return -1, -1
