import pandas as pd
import logging
from output_validation.utils import QiQuery
import matplotlib.pyplot as plt
from output_validation.utils.Constants import *
import os

class Distribution:


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


    def generate(self) -> None:
        '''Generates distribution plots for both datasets.'''
        self.generateDistributionPlots(self.inDataDf, IN)
        self.generateDistributionPlots(self.outDataDf, OUT)


    def generateDistributionPlots(self, df, inOut) -> None:
        '''Generates distribution plots per column for the given dataset.'''

        for col in self.qiQueryHelper.commaSeparatedColumnsAsList(self.qiQueryHelper.quasiIdentifyingColumns):
            col = col.strip()
            fig = plt.figure()
            ax = fig.add_axes([0,0,1,1])
            distDict = dict(df[col].value_counts())
            total = df.shape[0]
            types = list()
            counts = list()
            for key, val in distDict.items():
                types.append(key)
                counts.append(round(100*(val / total), 5))

            # Visibility and understandability largely disappears when we have
            # more than 100 values. Visualisation of the distribution still helps.
            plt.xticks(rotation=90)
            if len(counts) > 40:
                logging.info(f'Could not display xticks for column {col} due to it having > 40 distinct nominal values')
                plt.xticks([])
            ax.bar(types, counts)
            plt.ylabel('Records affected [%]')
            plt.savefig(os.path.join('plots', 'distribution', inOut,  'distribution_' + str(col)), bbox_inches='tight')
