import pytest
import os
import logging
import pandas as pd
import configparser
from output_validation.utils.Constants import *
from output_validation.Validator import Validator
from output_validation.inp.Simulator import populateConfigFromFile
from output_validation.inp.Simulator import getSepNaive

class TestValidator:


    GENERAL_TESTFILES_LOC = os.path.join(os.getcwd(), 'tests', 'testfiles', 'general_tests')
    GENERAL_TEST_CONFS_LOC = os.path.join(os.getcwd(), 'tests', 'generaltests')


    def parseConfig(self, path):
        config = configparser.ConfigParser(
        converters={'list': lambda x: [i.strip() for i in x.split(',')]})

        config.read(path, encoding='UTF-8')
        return config


    def testEmpty(self):
        expectedmsg = '''Module is unable to produce meaningful output without proper input data. 
                                Please provide either input or output data or both.'''
        # Doesn't matter which configuration we use here, should end earlier
        with pytest.raises(ValueError, match=expectedmsg):
            Validator(os.path.join(self.GENERAL_TESTFILES_LOC, 'randompath'),
                        os.path.join(self.GENERAL_TESTFILES_LOC, 'anotherrandompath'),
                        populateConfigFromFile(os.path.join(self.GENERAL_TEST_CONFS_LOC, 'conf_all.txt')))

    
    def testNoQIDBreak(self):
        result = Validator(os.path.join(self.GENERAL_TESTFILES_LOC, 'general_input_test1.csv'),
                    os.path.join(self.GENERAL_TESTFILES_LOC, 'general_output_test1.csv'),
                    self.parseConfig(os.path.join(self.GENERAL_TEST_CONFS_LOC, 'conf_noqids.txt'))).analyzeAndValidate()

        assert result == '{}'


    def testKLNone(self):
        result = Validator(os.path.join(self.GENERAL_TESTFILES_LOC, 'general_input_test1.csv'),
                    os.path.join(self.GENERAL_TESTFILES_LOC, 'general_output_test1.csv'),
                    self.parseConfig(os.path.join(self.GENERAL_TEST_CONFS_LOC, 'conf_klnone.txt'))).analyzeAndValidate()

        assert result == '{}'


    def testLLessThan1(self):
        validator = Validator(os.path.join(self.GENERAL_TESTFILES_LOC, 'general_input_test1.csv'),
                        os.path.join(self.GENERAL_TESTFILES_LOC, 'general_output_test1.csv'),
                        self.parseConfig(os.path.join(self.GENERAL_TEST_CONFS_LOC, 'conf_llessthan1.txt')))
        assert validator.confMinL is None


    def testBadSeparatorCsv(self):
        badCsvPath = os.path.join(self.GENERAL_TESTFILES_LOC, 'badseparator.csv')
        expectedmsg = '''Module is unable to produce meaningful output without proper input data. 
                                Please provide either input or output data or both.'''
        with pytest.raises(ValueError, match=expectedmsg):
            Validator(badCsvPath,
                        badCsvPath,
                        self.parseConfig(os.path.join(self.GENERAL_TEST_CONFS_LOC, 'conf_all.txt'))).analyzeAndValidate()

    
    def testBadConfig(self):
        expectedmsg = 'Konfiguratsioonifailis ei leitud sektsiooni Main.'
        with pytest.raises(Exception, match=expectedmsg):
            Validator(os.path.join(self.GENERAL_TESTFILES_LOC, 'general_input_test1.csv'),
                        os.path.join(self.GENERAL_TESTFILES_LOC, 'general_output_test1.csv'),
                        populateConfigFromFile(os.path.join(self.GENERAL_TEST_CONFS_LOC, 'conf_broken.txt')))


    def testAll(self):
        result = Validator(os.path.join(self.GENERAL_TESTFILES_LOC, 'general_input_test1.csv'),
                    os.path.join(self.GENERAL_TESTFILES_LOC, 'general_output_test1.csv'),
                    self.parseConfig(os.path.join(self.GENERAL_TEST_CONFS_LOC, 'conf_all.txt'))).analyzeAndValidate()

        expectedAttackerModelRiskDict = {
            AR_INPUT : {
                AR_PROSECUTOR_AVERAGE : '100.0 %',
                AR_ESTIMATED_JOURNALIST_RISK : '100.0 %',
                AR_ESTIMATED_MARKETER_RISK : '100.0 %',
                AR_PROSECUTOR_HIGHEST : '100.0 %',
                AR_PROSECUTOR_LOWEST : '100.0 %',
                AR_RECORDS_AFFECTED_HIGHEST : '100.0 %',
                AR_RECORDS_AFFECTED_LOWEST : '100.0 %'
            },
            AR_OUTPUT : {
                AR_PROSECUTOR_AVERAGE : '12.0 %',
                AR_ESTIMATED_JOURNALIST_RISK : '20.0 %',
                AR_ESTIMATED_MARKETER_RISK : '12.0 %',
                AR_PROSECUTOR_HIGHEST : '20.0 %',
                AR_PROSECUTOR_LOWEST : '5.882 %',
                AR_RECORDS_AFFECTED_HIGHEST : '30.0 %',
                AR_RECORDS_AFFECTED_LOWEST : '34.0 %'
            }
        }

        expectedEquivalenceClassStatDict = {
            EQ_INPUT : {
                EQ_AVG_NOSUP : 1,
                EQ_AVG_SUP : 1,
                EQ_BIGGEST : 1,
                EQ_SUPPRESSED : 0,
                EQ_NOCLASSES : 50,
                EQ_NORECORDS : 50,
                EQ_SMALLEST : 1,
            },
            EQ_OUTPUT : {
                EQ_AVG_NOSUP : 8.333,
                EQ_AVG_SUP : 8.333,
                EQ_BIGGEST : 17,
                EQ_SUPPRESSED : 0,
                EQ_NOCLASSES : 6,
                EQ_NORECORDS : 50,
                EQ_SMALLEST : 5,
            }
        }

        expectedPrivacyModelVerificationDict = {
            PR_K : [5, dict()],
            PR_L : [0, dict()],
            PR_XY : [5, dict()]
        }
        
        expectedSummaryStatisticsDict = {
            SS_INPUT : {
                SS_DISTINCT : {
                    'id' : 50,
                    'patient_gender' : 2,
                    'patient_birthdate' : 50,
                    'patient_ehak_code' : 36
                },
                SS_INFORMATIVE : {
                    'id' : 50,
                    'patient_gender' : 50,
                    'patient_birthdate' : 50,
                    'patient_ehak_code' : 50
                },
                SS_MODES : {
                    'id': [1, 1],
                    'patient_gender' : ['M', 27],
                    'patient_birthdate' : ['14.06.1983', 1],
                    'patient_ehak_code' : [793, 3]
                }
            },
            SS_OUTPUT : {
                SS_DISTINCT : {
                    'id' : 50,
                    'patient_gender' : 2,
                    'patient_birthdate' : 1,
                    'patient_ehak_code' : 4
                },
                SS_GENSUP : {
                    'id' : 0,
                    'patient_gender' : 0,
                    'patient_birthdate' : 50,
                    'patient_ehak_code' : 50
                },
                SS_INFORMATIVE : {
                    'id' : 50,
                    'patient_gender' : 50,
                    'patient_birthdate' : 0,
                    'patient_ehak_code' : 21
                },
                SS_MODES : {
                    'id': [1, 1],
                    'patient_gender' : ['M', 27],
                    'patient_birthdate' : ['*', 50],
                    'patient_ehak_code' : ['37', 11]
                },
                SS_SUP : {
                    'id': [0, '0.0 %'],
                    'patient_gender' : [0, '0.0 %'],
                    'patient_birthdate' : [50, '100.0 %'],
                    'patient_ehak_code' : [29, '58.0 %']
                },
                SS_SUP_OF_CHANGED : '79.0 %',
                SS_TOTAL_GENSUP : [100, '50.0 %'],
                SS_TOTAL_SUP : [79, '39.5 %']
            }
        }

        assert result[0][ATTACK_RISKS] == expectedAttackerModelRiskDict
        assert result[0][EQUIVALENCE_CLASSES] == expectedEquivalenceClassStatDict
        assert result[0][PRIVACY_VERIFICATION] == expectedPrivacyModelVerificationDict
        assert result[0][SUMMARY_STATISTICS][SS_INPUT] == expectedSummaryStatisticsDict[SS_INPUT]
        assert result[0][SUMMARY_STATISTICS][SS_OUTPUT] == expectedSummaryStatisticsDict[SS_OUTPUT]
