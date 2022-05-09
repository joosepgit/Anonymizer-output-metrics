from output_validation.risk.AttackerModelStatistics import AttackerModelStatistics
from output_validation.risk.PrivacyModelVerifier import PrivacyModelVerifier
from output_validation.utility.SummaryStatistics import SummaryStatistics
from output_validation.utility.ClassSizes import ClassSizes
from output_validation.utility.Distribution import Distribution
from output_validation.utils.QiQuery import QiQuery
from output_validation.utils.Constants import *
from output_validation.inp.Simulator import getSepNaive
from numpyencoder import NumpyEncoder
from output_validation.inp.Simulator import populateConfigFromFile
import logging, time, json
import pandas as pd
import os

class Validator:

    def __init__(self, inFilePath: str, outFilePath: str, config, blindSymbol = '*'):
        self.inDataDf, self.outDataDf = self.initializeDfs(inFilePath, outFilePath)
        self.confMinK = self.cast(K_ANONYMITY, config[CONF_ARX][K_ANONYMITY])
        self.confMinL = self.cast(L_DIVERSITY, config[CONF_ARX][L_DIVERSITY])
        self.qiQueryHelper = QiQuery(config[CONF_MAIN][IDENTIFYING], 
                                    config[CONF_MAIN][QUASI_IDENTIFYING],
                                    config[CONF_MAIN][SENSITIVE_ATTRIBUTES],
                                    blindSymbol)

    
    def analyzeAndValidate(self) -> str:
        '''Returns the collective result of risk and utility analysis as
        a json formatted string and generates distribution and risk plots.'''
        start = time.time()
        jsonDict = dict()

        if not self.qiQueryHelper.quasiIdentifyingColumns:
            logging.warning('No QID columns specified. Skipped output validation.')
            return json.dumps(jsonDict)

        if self.confMinK is None and self.confMinL is None:
            logging.warning('Privacy model configuration unspecified. Skipped output validation.')
            return json.dumps(jsonDict)

        summaryStats = SummaryStatistics(self.inDataDf, self.outDataDf, self.qiQueryHelper).compute()
        equivalenceClassStats = ClassSizes(self.inDataDf, self.outDataDf, self.qiQueryHelper).compute()

        trueMinK = equivalenceClassStats[EQ_OUTPUT][EQ_SMALLEST]
        privacyStats = PrivacyModelVerifier(self.confMinK, trueMinK, self.confMinL, self.outDataDf, self.qiQueryHelper).compute()

        jsonDict[PRIVACY_VERIFICATION] = privacyStats
        jsonDict[SUMMARY_STATISTICS] = summaryStats
        jsonDict[EQUIVALENCE_CLASSES] = equivalenceClassStats
    
        attackerModelStatistics = AttackerModelStatistics(self.inDataDf,
                                                     self.outDataDf,
                                                     self.confMinK,
                                                     equivalenceClassStats, 
                                                     self.qiQueryHelper).computeAndGenerate()
        jsonDict[ATTACK_RISKS] = attackerModelStatistics

        # Generate plots to output_validation/plots/distribution/
        Distribution(self.inDataDf, self.outDataDf, self.qiQueryHelper).generate()
        
        spent = time.time()-start
        logging.info('Analyzed and validated output in %s seconds', spent)
        
        return jsonDict, json.dumps(jsonDict,
                    cls=NumpyEncoder, 
                    indent=4, 
                    sort_keys=True,
                    separators=(', ', ': '))


    def initializeDfs(self, inPath: str, outPath:str) -> tuple:
        '''Initializes input and output datasets as pandas
        dataframes for risk and utility analysis, necessary
        for operations that rely on comparison.'''
        try:
            inDataDf = pd.read_csv(inPath, sep=getSepNaive(inPath))
        except:
            logging.warning('''Input data read failed. Skipping analysis for input.
            If input analysis is desired, make sure the file path was specified
            correctly.''')
            inDataDf = None
        
        try:
            outDataDf = pd.read_csv(outPath, sep=getSepNaive(outPath))
        except:
            logging.warning('''Output data read failed. Skipping analysis for output.
            If output analysis is desired, make sure the file path was specified
            correctly.''')
            outDataDf = None

        if inDataDf is None and outDataDf is None:
            raise ValueError('''Module is unable to produce meaningful output without proper input data. 
                                Please provide either input or output data or both.''')

        return inDataDf, outDataDf


    def cast(self, description: str, confIntstring: str) -> int:
        '''Verifies the usability of numeric values specified in configuration.'''
        try:
            asInt = int(confIntstring)
            if asInt >= 1:
                return asInt
            else:
                logging.warning(f'Expected {description} configuration value to be >= 1')
        except ValueError:
            logging.warning(f'Expected "{description}" configuration value to be a number string.')
        return None



# Runner
if __name__ == '__main__':
    logging.basicConfig()
    logging.getLogger().setLevel(logging.INFO)
    validator = Validator('inp/indata.csv', 
                     'inp/outdata.csv', populateConfigFromFile(os.path.join('inp', 'conf.txt')))
    print(validator.analyzeAndValidate())