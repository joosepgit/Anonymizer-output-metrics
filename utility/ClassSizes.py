import pandas as pd
import logging
import duckdb
from output_validation.utils import QiQuery
from output_validation.utils.Constants import *

class ClassSizes:


    def __init__(self, 
                inDataDf: pd.DataFrame, 
                outDataDf: pd.DataFrame,
                qiQueryHelper: QiQuery):
        self._inDataDf = inDataDf
        self._outDataDf = outDataDf
        self._qiQueryHelper = qiQueryHelper


    @property
    def inDataDf(self):
        '''Input dataset.'''
        return self._inDataDf


    @property
    def outDataDf(self):
        '''Output dataset.'''
        return self._outDataDf


    @property
    def qiQueryHelper(self):
        '''Queryhelper attribute.'''
        return self._qiQueryHelper


    def compute(self) -> dict:
        '''Computes equivalence class statistics for both datasets.'''
        eqDict = dict()
        eqDict[EQ_INPUT] = self.computeInput()
        eqDict[EQ_OUTPUT] = self.computeOutput()
        return eqDict


    def computeInput(self) -> dict:
        '''Computes equivalence class statistics for the input dataset.'''
        inDict = dict()
        ecStats = self.averageEcValue(self.inDataDf, True)
        inDict[EQ_AVG_SUP] = ecStats[0]
        inDict[EQ_AVG_NOSUP] = ecStats[1]
        inDict[EQ_SUPPRESSED] = ecStats[2]
        # Not including completely suppressed equivalence class, if it exists
        inDict[EQ_SMALLEST] = self.smallestEqClassSize(self.inDataDf)
        inDict[EQ_BIGGEST] = self.biggestEqClassSize(self.inDataDf)
        inDict[EQ_NOCLASSES] = ecStats[3]
        inDict[EQ_NORECORDS] = self.inDataDf.shape[0]
        return inDict

    
    def computeOutput(self) -> dict:
        '''Computes equivalence class statistics for the output dataset.'''
        outDict = dict()
        ecStats = self.averageEcValue(self.outDataDf, False)
        outDict[EQ_AVG_SUP] = ecStats[0]
        outDict[EQ_AVG_NOSUP] = ecStats[1]
        outDict[EQ_SUPPRESSED] = ecStats[2]
        # Not including completely suppressed equivalence class, if it exists
        outDict[EQ_SMALLEST] = self.smallestEqClassSize(self.outDataDf)
        outDict[EQ_BIGGEST] = self.biggestEqClassSize(self.outDataDf)
        outDict[EQ_NOCLASSES] = ecStats[3]
        outDict[EQ_NORECORDS] = self.outDataDf.shape[0]
        return outDict
    

    def averageEcValue(self, df, indata) -> tuple:
        '''Calculates the average equivalence class size
        based on number of rows with matching quasi-identifiers.'''
        
        nrOfRows = df.shape[0]
        # Find all equivalence classes and their respective sizes

        eqClassesSizesDf = duckdb.query(f'''SELECT DISTINCT {self.qiQueryHelper.quasiIdentifyingColumns}, count(*) as {K_ANONYMITY} FROM df 
                            GROUP BY {self.qiQueryHelper.quasiIdentifyingColumns} ORDER BY {K_ANONYMITY} DESC''').to_df()
        nrOfEqClasses = eqClassesSizesDf.shape[0]
        avgEcWithAllsuppressed = round(nrOfRows / nrOfEqClasses, 3)

        suppressedClassSize = None
        if not indata:
            ALLBLIND = self.qiQueryHelper.ALLBLIND
            suppressedClassSize = duckdb.query(f'''SELECT {K_ANONYMITY} FROM eqClassesSizesDf WHERE {ALLBLIND} ''').fetchall()

        
        if not suppressedClassSize:
            suppressedClassSize = 0
        else:
            suppressedClassSize = suppressedClassSize[0][0]
        
        avgEcWithoutAllsuppressed = round((nrOfRows-suppressedClassSize) / (nrOfEqClasses-1), 3)

        return (avgEcWithAllsuppressed, avgEcWithoutAllsuppressed, suppressedClassSize, eqClassesSizesDf.shape[0])


    def smallestEqClassSize(self, df) -> int:
        '''Returns the size of the smallest equivalence class.'''

        NOBLIND = self.qiQueryHelper.NOBLIND

        minEqClassSize = duckdb.query(f'''SELECT {K_ANONYMITY} FROM 
                                            (SELECT DISTINCT {self.qiQueryHelper.quasiIdentifyingColumns}, count(*) as {K_ANONYMITY} FROM df
                                            WHERE {NOBLIND} GROUP BY {self.qiQueryHelper.quasiIdentifyingColumns} ORDER BY {K_ANONYMITY} ASC LIMIT 1)''').fetchall()
        return minEqClassSize[0][0] if minEqClassSize else 0


    def biggestEqClassSize(self, df) -> int:
        '''Returns the size of the biggest NOT COMPLETELY suppressed
        equivalence class.'''

        NOBLIND = self.qiQueryHelper.NOBLIND

        maxEqClassSize = duckdb.query(f'''SELECT {K_ANONYMITY} FROM 
                                            (SELECT DISTINCT {self.qiQueryHelper.quasiIdentifyingColumns}, count(*) as {K_ANONYMITY} FROM df
                                            WHERE {NOBLIND} GROUP BY {self.qiQueryHelper.quasiIdentifyingColumns} ORDER BY {K_ANONYMITY} DESC LIMIT 1)''').fetchall()
        return maxEqClassSize[0][0] if maxEqClassSize else 0