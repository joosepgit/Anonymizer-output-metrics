import pytest
import os
import pandas as pd
from output_validation.utils.Constants import *
from output_validation.utility.SummaryStatistics import SummaryStatistics
from output_validation.utils.QiQuery import QiQuery

class TestSummaryStatistics:


    GENERAL_TESTFILES_LOC = os.path.join(os.getcwd(), 'tests', 'testfiles', 'general_tests')
    SUMMARYSTAT_TESTFILES_LOC = os.path.join(os.getcwd(), 'tests', 'testfiles', 'summary_statistics_tests')


    def initDf(self, path: str) -> pd.DataFrame:
        df = pd.read_csv(path)
        return df


    def testEmpty(self):
        emptyStat = SummaryStatistics(None, None, QiQuery('','','',''))
        expected = {SS_INPUT : dict(), SS_OUTPUT : dict()}
        assert emptyStat.compute() == expected


    def testNoBlindPerColumn(self):
        oneLineStat = SummaryStatistics(None, self.initDf(os.path.join(self.GENERAL_TESTFILES_LOC, 'oneline.csv')), QiQuery('','','','')).compute()
        assert oneLineStat[SS_OUTPUT][SS_MODES]['id'] == [1, 1]
        assert oneLineStat[SS_OUTPUT][SS_MODES]['gender'] == ['N', 1]
        assert oneLineStat[SS_OUTPUT][SS_MODES]['ehak'] == [111, 1]
        expectedmsg = 'Column id mode was not detected, does it contain any values?'
        with pytest.raises(RuntimeError, match=expectedmsg) as re_info:
            SummaryStatistics(None, 
                        self.initDf(os.path.join(self.GENERAL_TESTFILES_LOC, 'nolines.csv')),
                        QiQuery('','','','')).compute()


    def test30AsIn(self):
        stat30 = SummaryStatistics(self.initDf(os.path.join(self.SUMMARYSTAT_TESTFILES_LOC, 'summary_statistics_test1.csv')),
                            None,
                            QiQuery('id', 'gender, ehak', '', ''))
        res = stat30.compute()
        expectedSSInput = {
            SS_DISTINCT : {'id': 29,
                            'gender': 3,
                            'ehak': 4},
            SS_INFORMATIVE : {'id': 30,
                            'gender': 30,
                            'ehak': 30},
            SS_MODES : {'id': [30,2],
                        'gender': ['N', 13],
                        'ehak': ['111', 9]
                        }
        }
        expected = {SS_INPUT : expectedSSInput, SS_OUTPUT : dict()}
        assert res[SS_INPUT][SS_DISTINCT]['id'] == expected[SS_INPUT][SS_DISTINCT]['id']
        assert res[SS_INPUT][SS_DISTINCT]['gender'] == expected[SS_INPUT][SS_DISTINCT]['gender']
        assert res[SS_INPUT][SS_DISTINCT]['ehak'] == expected[SS_INPUT][SS_DISTINCT]['ehak']
        assert res[SS_INPUT][SS_INFORMATIVE]['id'] == expected[SS_INPUT][SS_INFORMATIVE]['id']
        assert res[SS_INPUT][SS_INFORMATIVE]['gender'] == expected[SS_INPUT][SS_INFORMATIVE]['gender']
        assert res[SS_INPUT][SS_INFORMATIVE]['ehak'] == expected[SS_INPUT][SS_INFORMATIVE]['ehak']
        assert res[SS_INPUT][SS_MODES]['id'] == expected[SS_INPUT][SS_MODES]['id']
        assert res[SS_INPUT][SS_MODES]['gender'] == expected[SS_INPUT][SS_MODES]['gender']
        assert res[SS_INPUT][SS_MODES]['ehak'] == expected[SS_INPUT][SS_MODES]['ehak']

        assert res == expected


    def test30AsOut(self):
        stat30 = SummaryStatistics(None, 
                            self.initDf(os.path.join(self.SUMMARYSTAT_TESTFILES_LOC, 'summary_statistics_test1.csv')),
                            QiQuery('id', 'gender, ehak', '', ''))
        res = stat30.compute()
        expectedSSOutput = {
            SS_DISTINCT : {'id': 29,
                            'gender': 3,
                            'ehak': 4},
            SS_GENSUP : dict(),
            SS_INFORMATIVE : {'id': 30,
                            'gender': 20,
                            'ehak': 24},
            SS_MODES : {'id': [30,2],
                        'gender': ['N', 13],
                        'ehak': ['111', 9]
                        },
            SS_SUP: {'id': [0, '0.0 %'],
                    'gender': [10, '33.3 %'],
                    'ehak': [6, '20.0 %']
                    }, 
            SS_SUP_OF_CHANGED: "0 %", 
            SS_TOTAL_GENSUP: [
                0, 
                "0 %"
            ], 
            SS_TOTAL_SUP: [
                0, 
                "0 %"
            ]
        }
        expected = {SS_INPUT : dict(), SS_OUTPUT : expectedSSOutput}
        assert res[SS_OUTPUT][SS_DISTINCT]['id'] == expected[SS_OUTPUT][SS_DISTINCT]['id']
        assert res[SS_OUTPUT][SS_DISTINCT]['gender'] == expected[SS_OUTPUT][SS_DISTINCT]['gender']
        assert res[SS_OUTPUT][SS_DISTINCT]['ehak'] == expected[SS_OUTPUT][SS_DISTINCT]['ehak']
        assert res[SS_OUTPUT][SS_GENSUP] == expected[SS_OUTPUT][SS_GENSUP]
        assert res[SS_OUTPUT][SS_INFORMATIVE]['id'] == expected[SS_OUTPUT][SS_INFORMATIVE]['id']
        assert res[SS_OUTPUT][SS_INFORMATIVE]['gender'] == expected[SS_OUTPUT][SS_INFORMATIVE]['gender']
        assert res[SS_OUTPUT][SS_INFORMATIVE]['ehak'] == expected[SS_OUTPUT][SS_INFORMATIVE]['ehak']
        assert res[SS_OUTPUT][SS_MODES]['id'] == expected[SS_OUTPUT][SS_MODES]['id']
        assert res[SS_OUTPUT][SS_MODES]['gender'] == expected[SS_OUTPUT][SS_MODES]['gender']
        assert res[SS_OUTPUT][SS_MODES]['ehak'] == expected[SS_OUTPUT][SS_MODES]['ehak']
        assert res[SS_OUTPUT][SS_SUP] == expected[SS_OUTPUT][SS_SUP]
        assert res[SS_OUTPUT][SS_SUP_OF_CHANGED] == expected[SS_OUTPUT][SS_SUP_OF_CHANGED]
        assert res[SS_OUTPUT][SS_TOTAL_GENSUP] == expected[SS_OUTPUT][SS_TOTAL_GENSUP]
        assert res[SS_OUTPUT][SS_TOTAL_SUP] == expected[SS_OUTPUT][SS_TOTAL_SUP]

        assert res == expected
