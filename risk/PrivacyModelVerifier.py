import pandas as pd
import duckdb
import logging
from output_validation.utils.Constants import *
from output_validation.utils import QiQuery

class PrivacyModelVerifier:


    def __init__(self,
                confMinK: int,
                trueMinK: int,
                confMinL: int,
                outDataDf: pd.DataFrame,
                qiQueryHelper: QiQuery):
        self._confMinK = confMinK
        self._trueMinK = trueMinK
        self._confMinL = confMinL
        self._outDataDf = outDataDf
        self._qiQueryHelper = qiQueryHelper


    @property
    def confMinK(self):
        '''The minimum k-anonymity threshold specified
        in the configuration file.'''
        return self._confMinK


    @property
    def trueMinK(self):
        '''The minimum k-anonymity in the output dataset.
        Let this value be x, then the output dataset is
        guaranteed to be x-anonymous.'''
        return self._trueMinK


    @property
    def confMinL(self):
        '''The minimum l-diversity threshold specified
        in the configuration file.'''
        return self._confMinL


    @property
    def outDataDf(self):
        '''The output dataset as a pandas dataframe.'''
        return self._outDataDf


    @property
    def qiQueryHelper(self):
        '''The current query helper.'''
        return self._qiQueryHelper


    def compute(self) -> dict:
        '''Computes privacy model values and detects
        violations.'''
        pvmDict = dict()
        if not self.qiQueryHelper.quasiIdentifyingColumns:
            raise RuntimeError('Unable to verify privacy models, quasi-identifying columns not specified.')
        
        if self.outDataDf is not None:
            pvmDict[PR_K] = self.kAnonymityFindIllegal()
            pvmDict[PR_XY], pvmDict[PR_L] = self.checkLDiversityAndXYAnonymityAndFindIllegal()
        return pvmDict


    # Record level k-anonymity
    # Behaviour depends on ClassSizes.smallest_eq_class_size
    # as this value is equivalent to the real smallest k value
    # for which record level k-anonymity holds
    def kAnonymityFindIllegal(self) -> list:
        '''Returns smallest k value (smallest equivalence class size) with
        all combinations of QID that violate the k-anonymity privacy model
        imposed by the configuration file.'''

        df = self.outDataDf
        if self.trueMinK >= self.confMinK:
            logging.info('Minimum record level k-anonymity is guaranteed. Skipping violation detection.')
            return [self.trueMinK, dict()]
        
        logging.info('Minimum record level k-anonymity is violated. Gathering violating QID.')
        violations = dict()
        eqClassesSizesDf = duckdb.query(f'''SELECT DISTINCT {self.qiQueryHelper.quasiIdentifyingColumns}, count(*) as {K_ANONYMITY} FROM df 
                            GROUP BY {self.qiQueryHelper.quasiIdentifyingColumns} ORDER BY {K_ANONYMITY} ASC''').to_df()
        i = 0
        rowdict = dict(eqClassesSizesDf.iloc[i])
        while int(rowdict[K_ANONYMITY]) < self.confMinK:
            local_k = rowdict[K_ANONYMITY]
            rowdict.pop(K_ANONYMITY, None)
            clause = self.qiQueryHelper.dictToQueryString(self.qiQueryHelper.AND, ' = ', rowdict)
            violations[clause] = local_k
            i += 1
            try:
                rowdict = dict(eqClassesSizesDf.iloc[i])
            except:
                logging.warning('All equivalence classes violate K!')
                break
        return [self.trueMinK, violations]


    # Equivalence class level l-diversity
    def checkLDiversityAndXYAnonymityAndFindIllegal(self) -> list:
        '''Detects and returns the smallest l value across the anonymized dataset
        and all cominations of QID that violate the l-diversity privacy model
        imposed by the configuration file.'''

        df = self.outDataDf
        eqClassesSizesDf = duckdb.query(f'''SELECT DISTINCT {self.qiQueryHelper.quasiIdentifyingColumns}, count(*) as {K_ANONYMITY} FROM df 
                            GROUP BY {self.qiQueryHelper.quasiIdentifyingColumns} ORDER BY {K_ANONYMITY} ASC''').to_df()
        resdictL = dict()
        lResult = [0, resdictL]

        XYViolations = dict()

        doXYAnalysis = self.checkXYAnonymityComputable()
        xyResult = [self.trueMinK, dict()]

        i = 0
        trueMinL = float('inf')
        trueMinXY = float('inf')
        while i < eqClassesSizesDf.shape[0]:
            rowdict = dict(eqClassesSizesDf.iloc[i])
            rowdict.pop(K_ANONYMITY, None)
            clause = self.qiQueryHelper.dictToQueryString(self.qiQueryHelper.AND, ' = ', rowdict)
            eqclassdf = duckdb.query(f'''SELECT * FROM df WHERE {clause}''').to_df()
            
            # Calculate L and violations
            if self.qiQueryHelper.sensitiveColumns:
                currdictL = dict()
                for col in self.qiQueryHelper.commaSeparatedColumnsAsList(self.qiQueryHelper.sensitiveColumns):
                    currunique = len(list(eqclassdf[col].unique()))
                    trueMinL = min(trueMinL, currunique)
                    if currunique < self.confMinL:
                        currdictL[col] = currunique
                if currdictL:
                    resdictL[clause] = currdictL

            # Calculate XY and violations
            if doXYAnalysis[0]:
                unique = len(list(eqclassdf[doXYAnalysis[1]].unique()))
                trueMinXY = min(trueMinXY, unique)
                if unique < self.confMinK:
                    XYViolations[clause] = unique

            i += 1

        if XYViolations:
            xyResult = [trueMinXY, XYViolations]
        if self.qiQueryHelper.sensitiveColumns and trueMinL < float('inf'):
            lResult[0] = trueMinL

        return [xyResult, lResult]


    # Individual level k-anonymity (requires non-suppressed identifying column)
    def checkXYAnonymityComputable(self) -> tuple:
        '''Runs all necessary checks to verify whether or not
        computing (X, Y)-anonymization violations is feasible.'''
        
        identifyingColumns = self.qiQueryHelper.commaSeparatedColumnsAsList(self.qiQueryHelper.identifyingColumns)
        if not identifyingColumns:
            logging.info('Unable to calculate individual level k-anonymity, missing identifying column.')
            return False, None
        # Only need one, take first
        identifyingColumn = identifyingColumns[0]

        df = self.outDataDf
        distinctIdCount = duckdb.query(f'''SELECT count(DISTINCT {identifyingColumn}) FROM df''').fetchall()
        if distinctIdCount and distinctIdCount[0][0] > 0:
            distinctIdCount = distinctIdCount[0][0]
            if distinctIdCount == df.shape[0]:
                logging.info('Record level k-anonymity is equal to individual level, as all identifying attributes are unique.')
                return False, None
        else:
            logging.info('''Unable to calculate individual level k-anonymity, 
                        could not fetch unique identifying attribute count or
                        identifying attribute contains null values.''')
            return False, None
        
        return True, identifyingColumn