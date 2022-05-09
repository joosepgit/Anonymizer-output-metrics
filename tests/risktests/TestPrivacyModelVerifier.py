import pytest
import os
import logging
import pandas as pd
from output_validation.utils.Constants import *
from output_validation.risk.PrivacyModelVerifier import PrivacyModelVerifier
from output_validation.utils.QiQuery import QiQuery

class TestPrivacyModelVerifier:


    GENERAL_TESTFILES_LOC = os.path.join(os.getcwd(), 'tests', 'testfiles', 'general_tests')
    PRIVACY_TESTFILES_LOC = os.path.join(os.getcwd(), 'tests', 'testfiles', 'privacy_model_verification_tests')


    def initDf(self, path: str, sep=',') -> pd.DataFrame:
        df = pd.read_csv(path, sep)
        return df


    def testEmptyWithAndWithoutQID(self):
        emptyVerifier = PrivacyModelVerifier(1,1,1, None, QiQuery('','','',''))
        expectedmsg = 'Unable to verify privacy models, quasi-identifying columns not specified.'
        with pytest.raises(RuntimeError, match=expectedmsg):
            emptyVerifier.compute()

        emptyVerifierWithQID = PrivacyModelVerifier(0,0,0, None, QiQuery('','gender','',''))
        expected = dict()
        assert emptyVerifierWithQID.compute() == expected


    def testNoLines(self):
        expected = {PR_K: [0, dict()], PR_XY: [0, dict()], PR_L: [0, dict()]}
        resdict = PrivacyModelVerifier(0,0,0,self.initDf(os.path.join(self.GENERAL_TESTFILES_LOC, 'nolines.csv')),  
                            QiQuery('','gender','','')).compute()
        assert resdict[PR_K] == expected[PR_K]
        assert resdict[PR_L] == expected[PR_L]
        assert resdict[PR_XY] == expected[PR_XY]    
    

    def testOneLine(self):
        expected = {PR_K: [1, dict()], PR_XY: [1, dict()], PR_L: [0, dict()]}
        resdict = PrivacyModelVerifier(1,1,1,self.initDf(os.path.join(self.GENERAL_TESTFILES_LOC, 'oneline.csv')),  
                            QiQuery('','gender','','')).compute()
        assert resdict[PR_K] == expected[PR_K]
        assert resdict[PR_L] == expected[PR_L]
        assert resdict[PR_XY] == expected[PR_XY]    

        expected = {PR_K: [1, dict()], PR_XY: [1, dict()], PR_L: [1, dict()]}
        resdict = PrivacyModelVerifier(1,1,1,self.initDf(os.path.join(self.GENERAL_TESTFILES_LOC, 'oneline.csv')),  
                            QiQuery('','gender','ehak','')).compute()
        assert resdict[PR_K] == expected[PR_K]
        assert resdict[PR_L] == expected[PR_L]
        assert resdict[PR_XY] == expected[PR_XY]    

        expected = {PR_K: [0, dict()], PR_XY: [0, dict()], PR_L: [1, dict()]}
        resdict = PrivacyModelVerifier(0,0,0,self.initDf(os.path.join(self.GENERAL_TESTFILES_LOC, 'oneline.csv')),  
                            QiQuery('','gender','ehak','')).compute()
        assert resdict[PR_K] == expected[PR_K]
        assert resdict[PR_L] == expected[PR_L]
        assert resdict[PR_XY] == expected[PR_XY]

        # XYViolations is empy because if the datasets distinct id count is equal to
        # the number of rows in the dataset, then it is skipped, 1 == 1 in case of 1 row.
        expected = {PR_K: [3, {"gender = 'N'": 1}], PR_XY: [3, dict()], PR_L: [1, {"gender = 'N'": {'ehak': 1}}]}
        resdict = PrivacyModelVerifier(5,3,9,self.initDf(os.path.join(self.GENERAL_TESTFILES_LOC, 'oneline.csv')),  
                            QiQuery('','gender','ehak','')).compute()
        assert resdict[PR_K] == expected[PR_K]
        assert resdict[PR_L] == expected[PR_L]
        assert resdict[PR_XY] == expected[PR_XY]    


    def testFetchEmptyColumn(self):
        expected = {PR_K: [0, dict()], PR_XY: [0, dict()], PR_L: [1, dict()]}
        resdict = PrivacyModelVerifier(0,0,0,self.initDf(os.path.join(self.PRIVACY_TESTFILES_LOC, 'onecolumnempty.csv')),  
                            QiQuery('id','gender','ehak','')).compute()
        assert resdict[PR_K] == expected[PR_K]
        assert resdict[PR_L] == expected[PR_L]
        assert resdict[PR_XY] == expected[PR_XY]
        

    def test1_20Rows(self):
        expected = {PR_K: [5, dict()], PR_XY: [5, dict()], PR_L: [5, dict()]}
        resdict = PrivacyModelVerifier(5,5,5,
            self.initDf(os.path.join(self.PRIVACY_TESTFILES_LOC, 'privacy_model_verification_test1.csv')),
            QiQuery('id', 'gender, ehak', 'dgn','')).compute()
        
        assert resdict[PR_K] == expected[PR_K]
        assert resdict[PR_L] == expected[PR_L]
        assert resdict[PR_XY] == expected[PR_XY]    
        
    
    def test2_20Rows(self):
        expected = {PR_K: [5, dict()], PR_XY: [5, dict()],
                     PR_L: [3, {"gender = 'M' AND ehak = 56": {'dgn': 4},"gender = 'N' AND ehak = 245": {'dgn': 3}}]}
        resdict = PrivacyModelVerifier(5,5,5,
            self.initDf(os.path.join(self.PRIVACY_TESTFILES_LOC, 'privacy_model_verification_test2.csv'), sep='\t'),
            QiQuery('id', 'gender, ehak', 'dgn','')).compute()
        
        assert resdict[PR_K] == expected[PR_K]
        assert resdict[PR_L] == expected[PR_L]
        assert resdict[PR_XY] == expected[PR_XY]   


    def test3_20Rows(self):
        expected = {PR_K: [5, dict()], 
                    PR_XY: [3, {"gender = 'M' AND ehak = 56": 4,"gender = 'N' AND ehak = 131": 3}],
                    PR_L: [5, dict()]}
        resdict = PrivacyModelVerifier(5,5,5,
            self.initDf(os.path.join(self.PRIVACY_TESTFILES_LOC, 'privacy_model_verification3_test3.csv'), sep='\t'),
            QiQuery('id', 'gender, ehak', 'dgn','')).compute()
        
        assert resdict[PR_K] == expected[PR_K]
        assert resdict[PR_L] == expected[PR_L]
        assert resdict[PR_XY] == expected[PR_XY]   