import pytest
import os
import logging
import pandas as pd
from output_validation.utils.Constants import *
from output_validation.utility.ClassSizes import ClassSizes
from output_validation.utils.QiQuery import QiQuery

class TestClassSizes:


    GENERAL_TESTFILES_LOC = os.path.join(os.getcwd(), 'tests', 'testfiles', 'general_tests')
    EQCLASS_TESTFILES_LOC = os.path.join(os.getcwd(), 'tests', 'testfiles', 'equivalence_class_tests')


    def initDf(self, path: str) -> pd.DataFrame:
        df = pd.read_csv(path)
        return df


    def testEmptyWithAndWithoutQID(self):
        emptyEq = ClassSizes(None, None, QiQuery('','','',''))
        expectedmsg = 'Unable to compute equivalence class statistics, quasi-identifying columns not specified.'
        with pytest.raises(RuntimeError, match=expectedmsg) as re_info:
            emptyEq.compute()

        emptyEqWithQid = ClassSizes(None, None, QiQuery('','gender','',''))
        expected = {EQ_INPUT : dict(), EQ_OUTPUT : dict()}
        assert emptyEqWithQid.compute() == expected


    def testNoLines(self):
        expectedmsg = 'Input dataset has no rows!'
        with pytest.raises(RuntimeError, match=expectedmsg):
            ClassSizes(self.initDf(os.path.join(self.GENERAL_TESTFILES_LOC, 'nolines.csv')), 
                            None, 
                            QiQuery('','gender','','')).compute()

    def testOneLine(self):
        oneLineStat = ClassSizes(None, 
                        self.initDf(os.path.join(self.GENERAL_TESTFILES_LOC, 'oneline.csv')),
                        QiQuery('','gender','','')).compute()
        assert oneLineStat[EQ_OUTPUT][EQ_AVG_SUP] == 1
        assert oneLineStat[EQ_OUTPUT][EQ_AVG_NOSUP] == 1
        assert oneLineStat[EQ_OUTPUT][EQ_BIGGEST] == 1
        assert oneLineStat[EQ_OUTPUT][EQ_SUPPRESSED] == 0
        assert oneLineStat[EQ_OUTPUT][EQ_NOCLASSES] == 1
        assert oneLineStat[EQ_OUTPUT][EQ_NORECORDS] == 1
        assert oneLineStat[EQ_OUTPUT][EQ_SMALLEST] == 1

        oneLineStat = ClassSizes(self.initDf(os.path.join(self.GENERAL_TESTFILES_LOC, 'oneline.csv')), 
                        None,
                        QiQuery('','gender','','')).compute()
        assert oneLineStat[EQ_INPUT][EQ_AVG_SUP] == 1
        assert oneLineStat[EQ_INPUT][EQ_AVG_NOSUP] == 1
        assert oneLineStat[EQ_INPUT][EQ_BIGGEST] == 1
        assert oneLineStat[EQ_INPUT][EQ_SUPPRESSED] == 0
        assert oneLineStat[EQ_INPUT][EQ_NOCLASSES] == 1
        assert oneLineStat[EQ_INPUT][EQ_NORECORDS] == 1
        assert oneLineStat[EQ_INPUT][EQ_SMALLEST] == 1

    
    def test1_10Rows(self):
        eqStat = ClassSizes(self.initDf(os.path.join(self.EQCLASS_TESTFILES_LOC, 'Equivalence_class_test1.csv')), 
                        None,
                        QiQuery('id','gender, ehak','','')).compute()
        expecteddict = {
            EQ_INPUT : {
                EQ_AVG_SUP : 3.333,
                EQ_AVG_NOSUP : 3.333,
                EQ_BIGGEST : 5,
                EQ_SMALLEST : 2,
                EQ_SUPPRESSED : 0,
                EQ_NOCLASSES : 3,
                EQ_NORECORDS : 10
            },
            EQ_OUTPUT : dict()
        }
        assert expecteddict[EQ_INPUT][EQ_AVG_SUP] == eqStat[EQ_INPUT][EQ_AVG_SUP]
        assert expecteddict[EQ_INPUT][EQ_AVG_NOSUP] == eqStat[EQ_INPUT][EQ_AVG_NOSUP]
        assert expecteddict[EQ_INPUT][EQ_BIGGEST] == eqStat[EQ_INPUT][EQ_BIGGEST]
        assert expecteddict[EQ_INPUT][EQ_SMALLEST] == eqStat[EQ_INPUT][EQ_SMALLEST]
        assert expecteddict[EQ_INPUT][EQ_SUPPRESSED] == eqStat[EQ_INPUT][EQ_SUPPRESSED]
        assert expecteddict[EQ_INPUT][EQ_NOCLASSES] == eqStat[EQ_INPUT][EQ_NOCLASSES]
        assert expecteddict[EQ_INPUT][EQ_NORECORDS] == eqStat[EQ_INPUT][EQ_NORECORDS]

        assert expecteddict == eqStat


    def testNoAllSuppressedOutput10rows(self):
        eqStat = ClassSizes(None,
                        self.initDf(os.path.join(self.EQCLASS_TESTFILES_LOC, 'Equivalence_class_test1.csv')), 
                        QiQuery('id','gender, ehak','','')).compute()
        expecteddict = {
            EQ_INPUT : dict(), 
            EQ_OUTPUT : {
                EQ_AVG_SUP : 3.333,
                EQ_AVG_NOSUP : 3.333,
                EQ_BIGGEST : 5,
                EQ_SMALLEST : 2,
                EQ_SUPPRESSED : 0,
                EQ_NOCLASSES : 3,
                EQ_NORECORDS : 10
            }
        }
        assert expecteddict[EQ_OUTPUT][EQ_AVG_SUP] == eqStat[EQ_OUTPUT][EQ_AVG_SUP]
        assert expecteddict[EQ_OUTPUT][EQ_AVG_NOSUP] == eqStat[EQ_OUTPUT][EQ_AVG_NOSUP]
        assert expecteddict[EQ_OUTPUT][EQ_BIGGEST] == eqStat[EQ_OUTPUT][EQ_BIGGEST]
        assert expecteddict[EQ_OUTPUT][EQ_SMALLEST] == eqStat[EQ_OUTPUT][EQ_SMALLEST]
        assert expecteddict[EQ_OUTPUT][EQ_SUPPRESSED] == eqStat[EQ_OUTPUT][EQ_SUPPRESSED]
        assert expecteddict[EQ_OUTPUT][EQ_NOCLASSES] == eqStat[EQ_OUTPUT][EQ_NOCLASSES]
        assert expecteddict[EQ_OUTPUT][EQ_NORECORDS] == eqStat[EQ_OUTPUT][EQ_NORECORDS]

        assert expecteddict == eqStat


    def test2_10Rows(self):
        eqStat = ClassSizes(None,
                        self.initDf(os.path.join(self.EQCLASS_TESTFILES_LOC, 'equivalence_class_test2.csv')), 
                        QiQuery('id','gender, ehak','','')).compute()
        expecteddict = {
            EQ_INPUT : dict(),
            EQ_OUTPUT : {
                EQ_AVG_SUP : 2.5,
                EQ_AVG_NOSUP : 2.333,
                EQ_BIGGEST : 4,
                EQ_SMALLEST : 1,
                EQ_SUPPRESSED : 3,
                EQ_NOCLASSES : 4,
                EQ_NORECORDS : 10
            }
        }
        assert expecteddict[EQ_OUTPUT][EQ_AVG_SUP] == eqStat[EQ_OUTPUT][EQ_AVG_SUP]
        assert expecteddict[EQ_OUTPUT][EQ_AVG_NOSUP] == eqStat[EQ_OUTPUT][EQ_AVG_NOSUP]
        assert expecteddict[EQ_OUTPUT][EQ_BIGGEST] == eqStat[EQ_OUTPUT][EQ_BIGGEST]
        assert expecteddict[EQ_OUTPUT][EQ_SMALLEST] == eqStat[EQ_OUTPUT][EQ_SMALLEST]
        assert expecteddict[EQ_OUTPUT][EQ_SUPPRESSED] == eqStat[EQ_OUTPUT][EQ_SUPPRESSED]
        assert expecteddict[EQ_OUTPUT][EQ_NOCLASSES] == eqStat[EQ_OUTPUT][EQ_NOCLASSES]
        assert expecteddict[EQ_OUTPUT][EQ_NORECORDS] == eqStat[EQ_OUTPUT][EQ_NORECORDS]

        assert expecteddict == eqStat