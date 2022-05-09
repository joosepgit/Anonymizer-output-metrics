import pandas as pd
import logging
import duckdb
from output_validation.utils.Constants import *
from output_validation.utils import QiQuery

class SummaryStatistics:


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
        '''Computes summary statistics for both datasets.'''
        statSict = dict()

        inputResult = dict()
        if self.inDataDf is not None:
            inputResult = self.computeInput()
        statSict[SS_INPUT]= inputResult

        outputResult = dict()
        if self.outDataDf is not None:
            outputResult = self.computeOutput()
        statSict[SS_OUTPUT] = outputResult

        return statSict


    def computeInput(self) -> dict:
        '''Computes summary statistics for the input dataset.'''
        inDict = dict()
        inDict[SS_DISTINCT] = dict([(col, len(list(self.inDataDf[col].value_counts()))) for col in list(self.inDataDf.columns)])
        # Modes with their respective quantities
        inDict[SS_MODES] = self.nonblindModesPerColumn(self.inDataDf, list(self.inDataDf.columns))
        # The number of not suppressed values for both input and output
        inDict[SS_INFORMATIVE] = dict([(col, self.inDataDf.shape[0]) for col in self.inDataDf.columns])
        return inDict


    def computeOutput(self) -> dict:
        '''Computes summary statistics for the output dataset.'''
        outDict = dict()
        outDict[SS_DISTINCT] = dict([(col, len(list(self.outDataDf[col].value_counts()))) for col in list(self.outDataDf.columns)])
        # Modes with their respective quantities
        outDict[SS_MODES] = self.nonblindModesPerColumn(self.outDataDf, list(self.outDataDf.columns))
        # suppressed values per column
        outDict[SS_SUP] = self.suppressedValuesPerColumn()
        outDict[SS_INFORMATIVE] = dict([(col, (self.outDataDf.shape[0] - blinds[0])) for col, blinds in outDict[SS_SUP].items()])

        if self.inDataDf is not None:
            # Generalized or suppressed values per column and total (0, 1)
            changestats = self.extractChangedValueStats()
            outDict[SS_GENSUP] = changestats[0]
            # Total modified values (generalized or suppressed)
            totalValuesInDf = self.outDataDf.shape[0] * len(self.outDataDf.columns)
            outDict[SS_TOTAL_GENSUP] = [changestats[1], str(round(changestats[1]/totalValuesInDf*100, 3)) + ' %']
            # Total suppressed values
            outDict[SS_TOTAL_SUP] = (lambda x : [x, str(round(x/totalValuesInDf*100, 3)) + ' %'])(sum(list(map(lambda x: x[1][0], outDict[SS_SUP].items()))))
            outDict[SS_SUP_OF_CHANGED] = str(round(outDict[SS_TOTAL_SUP][0]/outDict[SS_TOTAL_GENSUP][0]*100, 3)) + ' %'
        else:
            outDict[SS_GENSUP] = dict()
            outDict[SS_TOTAL_GENSUP] = [0,'0 %']
            outDict[SS_TOTAL_SUP] = [0,'0 %']
            outDict[SS_SUP_OF_CHANGED] = '0 %'

        return outDict
    

    def nonblindModesPerColumn(self, df, cols) -> dict:
        '''Returns a dictionary where keys are column names and values are
        modes (excluding suppressed values unless the attribude contains
        only suppressed values) paired with their counts in the corresponding column.'''
        
        res = dict()
        for col in cols:
            mode = list(duckdb.query(f'''SELECT {col} AS Mode, COUNT(*) AS Count FROM df
                GROUP BY Mode ORDER BY COUNT(*) DESC LIMIT 2''').fetchall())
            if not mode:
                raise RuntimeError(f'Column {col} mode was not detected, does it contain any values?')
            elif len(mode) == 1:
                res[col] = list(mode[0])
            else:
                res[col] = list(mode[0]) if mode[0][0] != self.qiQueryHelper.blindSymbol else list(mode[1])
        return res


    def suppressedValuesPerColumn(self) -> dict:
        '''Calculates the number of suppressed values and 
        the percentage of all values that have been
        suppressed per column.'''

        init = dict(self.outDataDf.isin([self.qiQueryHelper.blindSymbol]).sum(axis=0))
        values = dict([(key, [value, str((round(100*(value/self.outDataDf.shape[0]), 1))) + ' %']) for key, value in init.items()])
        return values


    def extractChangedValueStats(self) -> tuple:
        '''Calculates the number of changed cells per column and
        the the total number of changed columns.'''

        changedValuesPerColumn = dict()
        totalChangedValues = 0
        for col in self.inDataDf:
            s = set(self.inDataDf[col])
            changed = len([x for x in self.outDataDf[col] if x not in s])
            changedValuesPerColumn[col] = changed
            totalChangedValues += changed
        
        return changedValuesPerColumn, totalChangedValues