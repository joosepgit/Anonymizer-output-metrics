import pandas as pd
import duckdb
import logging
from output_validation.utils import QiQuery
from output_validation.utils.Constants import *
import plotly.graph_objects as go
import os


# Depends on ClassSizes.py in order to avoid 
# duplicated computation
class AttackerModelStatistics:
    '''Computation of risk probabilities imposed by
    three main attack models is implemented here in a
    simplified manner due to the assumption of our sample
    always being equivalent to the population.'''

    def __init__(self, 
                inDataDf: pd.DataFrame, 
                outDataDf: pd.DataFrame,
                confMinK: int, 
                eqClassStats: dict,
                qiQueryHelper: QiQuery,
                ):
        self._inDataDf = inDataDf
        self._outDataDf = outDataDf
        self._threshold = confMinK
        self._eqClassStats = eqClassStats
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
    def threshold(self):
        '''Threshold for smallest allowed equivalence class
        in terms of matching QID values.'''
        return self._threshold


    @property
    def eqClassStats(self):
        '''Result of the module ClassSizes.py for more efficient
        computation.'''
        return self._eqClassStats


    @property
    def qiQueryHelper(self):
        '''Queryhelper attribute.'''
        return self._qiQueryHelper


    def computeAndGenerate(self) -> dict:
        '''Computes the risk overview and generates
        risk analysis gauge charts for both datasets.'''
        resDict = dict()
        resDict[AR_INPUT] = self.computeInput() if self.inDataDf is not None else dict()
        resDict[AR_OUTPUT] = self.computeOutput() if self.outDataDf is not None else dict()
        return resDict


    def computeInput(self) -> dict:
        '''Computes the risk overview and generates
        risk analysis gauge charts for the input dataset.'''
        recordsAtRisk = self.getRecordsAtRisk(self.inDataDf)

        # Generate plots to plots/attackmodels
        self.generateGaugePlots(EQ_INPUT, recordsAtRisk, IN)

        return self.computeOverview(self.inDataDf, EQ_INPUT)

    
    def computeOutput(self) -> dict:
        '''Computes the risk overview and generates
        risk analysis gauge charts for the output dataset.'''
        recordsAtRisk = self.getRecordsAtRisk(self.outDataDf)

        # Generate plots to plots/attackmodels
        self.generateGaugePlots(EQ_OUTPUT, recordsAtRisk, OUT)

        return self.computeOverview(self.outDataDf, EQ_OUTPUT)

    
    def computeOverview(self, df, inOut) -> dict:
        '''Computes the risk overview for the given dataset.'''
        overviewDict = dict()
        overviewDict[AR_PROSECUTOR_LOWEST] = self.percentize(1.0, self.eqClassStats[inOut][EQ_BIGGEST])
        overviewDict[AR_PROSECUTOR_AVERAGE] = self.percentize(1.0, self.eqClassStats[inOut][EQ_AVG_SUP])
        overviewDict[AR_PROSECUTOR_HIGHEST] = self.percentize(1.0, self.eqClassStats[inOut][EQ_SMALLEST])
        overviewDict[AR_RECORDS_AFFECTED_LOWEST] = self.computeRecordsAffectedLowest(df, inOut)
        overviewDict[AR_RECORDS_AFFECTED_HIGHEST] = self.computeRecordsAffectedHighest(df, inOut)
        overviewDict[AR_ESTIMATED_JOURNALIST_RISK] = self.percentize(1.0, self.eqClassStats[inOut][EQ_SMALLEST])
        overviewDict[AR_ESTIMATED_MARKETER_RISK] = self.percentize(1.0, self.eqClassStats[inOut][EQ_AVG_SUP])
        overviewDict = dict([(key, str(value) + ' %') for key, value in overviewDict.items()])
        return overviewDict


    def computeProsecutorJournalistMarketerRiskPlotData(self, inOut) -> tuple:
        '''Returns all risks for gauge plots, computed in a unified manner due
        to the assumption that sample is equivalent to population.'''
        highestRisk = self.percentize(1.0, self.eqClassStats[inOut][EQ_SMALLEST])
        successRate = self.percentize(1.0, self.eqClassStats[inOut][EQ_AVG_SUP])
        
        return highestRisk, successRate


    def generateGaugePlots(self, inOut, recordsAtRisk, ioName):
        '''Generates gauge charts for the given dataset.'''
        highestRisk, successRate = self.computeProsecutorJournalistMarketerRiskPlotData(inOut)
        iterableRisks = [{AR_RECORDS_AT_RISK : recordsAtRisk,
                         AR_HIGHEST_RISK : highestRisk,
                         AR_SUCCESS_RATE : successRate}
                         for i in range(3) if i < 2]
        iterableRisks.append({AR_SUCCESS_RATE : successRate})
        names = ['Prosecutor', 'Journalist', 'Marketer']

        for i, d in enumerate(iterableRisks):
            for k, v in d.items():
                k = k.lower()
                fig = go.Figure(go.Indicator(
                    mode = "gauge+number+delta",
                    value = v,
                    delta = {'reference': self.percentize(1.0, self.threshold),
                    'increasing.color': "red", 'decreasing.color': "green"},
                    number = {'suffix': "%"},
                    domain = {'x': [0, 1], 'y': [0, 1]},
                    title = {'text': names[i] + ' ' + k, 'font': {'size': 24}},
                    gauge = {
                        'axis': {'range': [0, 100], 'tickwidth': 1, 'tickcolor': "black", 'ticksuffix': "%",
                        'tickmode': "array", 'tickvals' : [0, 25, 50, 75, 100]},
                        'bar': {'color': "black"},
                        'bgcolor': "white",
                        'borderwidth': 10,
                        'bordercolor': "gray",
                        'steps': [
                            {'range': [0, 25], 'color': 'green'},
                            {'range': [25, 50], 'color': 'yellow'},
                            {'range': [50, 75], 'color': 'orange'},
                            {'range': [75, 100], 'color': 'red'}],
                        }))
                namekey = names[i] + '_' + k.replace(' ', '_') + '.png'
                output_file_name = os.path.join('plots', 'attackmodels', ioName, namekey)
                fig.write_image(output_file_name) 

    
    def getRecordsAtRisk(self, df) -> float:
        '''Returns the percentage of records at risk
        in terms of the current provided threshold.'''
        recordRiskQuery = duckdb.query(f'''
                            SELECT SUM({K_ANONYMITY}) FROM
                            (SELECT DISTINCT {self.qiQueryHelper.quasiIdentifyingColumns}, 
                            count(*) as {K_ANONYMITY} FROM df
                            GROUP BY {self.qiQueryHelper.quasiIdentifyingColumns}
                            HAVING {K_ANONYMITY} < {self.threshold} 
                            ORDER BY {K_ANONYMITY} DESC)''').fetchall()
        return (self.percentize(recordRiskQuery[0][0], df.shape[0]) if 
                        recordRiskQuery[0][0] is not None
                        else 0.0)


    def computeRecordsAffectedHighest(self, df, inOut) -> float:
        '''Returns the percentage of records affected by the highest
        risk based on the smallest physical equivalence class.'''
        highestRecordRiskQuery = duckdb.query(f'''
                            SELECT SUM({K_ANONYMITY}) FROM
                            (SELECT DISTINCT {self.qiQueryHelper.quasiIdentifyingColumns}, 
                            count(*) as {K_ANONYMITY} FROM df
                            GROUP BY {self.qiQueryHelper.quasiIdentifyingColumns}
                            HAVING {K_ANONYMITY} = {self.eqClassStats[inOut][EQ_SMALLEST]} 
                            )''').fetchall()
        return (self.percentize(highestRecordRiskQuery[0][0], df.shape[0]) if 
                        highestRecordRiskQuery[0][0] is not None
                        else 0.0)


    def computeRecordsAffectedLowest(self, df, inOut) -> float:
        '''Returns the percentage of records affected by the lowest
        risk based on the biggest physical equivalence class.'''
        highestRecordRiskQuery = duckdb.query(f'''
                            SELECT SUM({K_ANONYMITY}) FROM
                            (SELECT DISTINCT {self.qiQueryHelper.quasiIdentifyingColumns}, 
                            count(*) as {K_ANONYMITY} FROM df
                            GROUP BY {self.qiQueryHelper.quasiIdentifyingColumns}
                            HAVING {K_ANONYMITY} = {self.eqClassStats[inOut][EQ_BIGGEST]} 
                            )''').fetchall()
        return (self.percentize(highestRecordRiskQuery[0][0], df.shape[0]) if 
                        highestRecordRiskQuery[0][0] is not None
                        else 0.0)


    def percentize(self, numerator, denominator) -> float:
        '''Returns the result of dividing numerator by the
        denominator in percent form.'''
        return round((numerator / denominator)*100, 3)