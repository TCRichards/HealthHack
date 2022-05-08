from statsmodels.tsa.stattools import grangercausalitytests
import pandas as pd

from stats.test import Test


# https://www.statsmodels.org/stable/generated/statsmodels.tsa.stattools.grangercausalitytests.html#statsmodels.tsa.stattools.grangercausalitytests
# Tests results are stored in a dictionary whose keys are the number of lags. For each lag the values are a tuple, with the first element a dictionary with
# test statistic, pvalues, degrees of freedom, the second element are the OLS estimation results for the restricted model,
# the unrestricted model and the restriction (contrast) matrix for the parameter f_test.
class GrangerTest(Test):

    def __init__(self):
        super().__init__('Granger', 'Granger Causality', False)

    # First attempt at running a statistical test to check for causation
    # alpha (probability of type I error that I choose)
    def runTestOverRange(self, dependentT, independentT, minLag=0, maxLag=3):

        # Need more than a handful of measurements to even attempt
        # if (len(dependentT.getProcessedScores()) < 5):
        #     return False, 'Not Enough Data To Run Test'

        # Need to convert data into a single dataframe to run test
        data = pd.DataFrame(
            data={'Result': dependentT.getProcessedScores(),
                  'Cause': independentT.getProcessedScores()},
            index=dependentT.getProcessedDates())

        gc_result = None
        while True:
            try:
                # Can throw a ValueError if insufficient measurements
                gc_result = grangercausalitytests(
                    data, maxLag, addconst=True, verbose=False)
                break
            except ValueError:
                # In that case don't try to look so far ahead -- requires fewer measurements to succeed
                maxLag -= 1
                if maxLag == 0:
                    return False, 'Error Running Granger Causality Test'

        # Granger test can't be run for causation with 0 day lag
        # TODO: See if I can mimic this by shifting the data
        eta2s = []
        p_values = []
        minLag = max(1, minLag)
        for lag in range(minLag, maxLag + 1):
            # This will return a dictionary of maxLag entries containing the results for each lag time
            # Tests give similar results, so blindly choose the 'params_ftest'
            f_value, p_value, DOF_denom, DOF_num = gc_result[lag][0]['params_ftest']
            N = len(data)
            # Eta-Squared value to measure effect size
            eta2 = f_value * (DOF_denom - 1) / (f_value *
                                                (DOF_denom - 1) + (N - DOF_denom))
            eta2s.append(eta2)
            p_values.append(p_value)
        return eta2s, p_values

    # Gets the result from the granger test for a specific lag value
    def runValidTestForLag(self, dependentT, independentT, lag=1):
        eta2s, p_values = self.runGrangerTestOverRange(
            dependentT, independentT, maxLag=lag)
        return eta2s[-1], p_values[-1]
