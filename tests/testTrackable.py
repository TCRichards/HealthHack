from trackables.trackable import Trackable

import unittest
import pandas as pd
import numpy as np


class TestDates(unittest.TestCase):

    def test_CheckNoOverlap(self):
        dateRange1 = pd.date_range(start='1/1/2020', end='2/1/2020')
        data1 = pd.DataFrame(data={
            'Score': np.random.rand(len(dateRange1))
        }, index=dateRange1)
        t1 = Trackable('t1', data1)

        dateRange2 = pd.date_range(start='1/1/2019', end='2/1/2019')
        data2 = pd.DataFrame(data={
            'Score': np.random.rand(len(dateRange2))
        }, index=dateRange1)
        t2 = Trackable('t1', data2)

        self.assertFalse(t1.overlaps(t2))


def run():
    unittest.main()


if __name__ == '__main__':
    run()
