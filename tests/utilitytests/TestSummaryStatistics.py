import pytest
import os
import pandas as pd
from output_validation.utils.Constants import *
from output_validation.utility.SummaryStatistics import SummaryStatistics
from output_validation.utils.QiQuery import QiQuery

class TestSummaryStatistics:

    TESTFILES_LOC = os.path.join('output_validation', 'tests', 'testfiles')
    CONFIGS = os.path.join(TESTFILES_LOC, 'config')
    DATA_IN = os.path.join(TESTFILES_LOC, 'data_in')
    DATA_OUT = os.path.join(TESTFILES_LOC, 'data_out')

    def initDf(self, path: str) -> pd.DataFrame:
        df = pd.read_csv(path)
        return df


    def test_empty(self):
        emptyStat = SummaryStatistics(None, None, QiQuery('','','',''))
        expected = {SS_INPUT : dict(), SS_OUTPUT : dict()}
        assert emptyStat.compute() == expected