import logging
import re
from output_validation.utils.Constants import EMPTY_WHERE

class QiQuery:

    AND = ' AND '
    OR = ' OR '

    def __init__(self, identifyingColumns, quasiIdentifyingColumns, sensitiveColumns, blindSymbol):
        if "'" in blindSymbol or not blindSymbol:
            logging.warning(f'SQL context illegal blind symbol: {blindSymbol}. Defaulting to *.')
            blindSymbol = '*'

        self._identifyingColumns = identifyingColumns
        self._sensitiveColumns = sensitiveColumns
        self._quasiIdentifyingColumns = quasiIdentifyingColumns
        self._blindSymbol = blindSymbol
        if not quasiIdentifyingColumns:
            self._NOBLIND = EMPTY_WHERE
            self._ALLBLIND = EMPTY_WHERE
        else:
            self._NOBLIND = self.createQueryString(self.OR, f"IS DISTINCT FROM '{blindSymbol}'")
            self._ALLBLIND = self.createQueryString(self.AND, f"= '{blindSymbol}'")

    
    @property
    def identifyingColumns(self):
        '''The identifying columns.'''
        return self._identifyingColumns


    @property
    def sensitiveColumns(self):
        '''The sensitive columns.'''
        return self._sensitiveColumns


    @property
    def quasiIdentifyingColumns(self):
        '''The QID columns.'''
        return self._quasiIdentifyingColumns


    @property
    def blindSymbol(self):
        '''The current suppressed value symbol.'''
        return self._blindSymbol


    @property
    def NOBLIND(self):
        '''Non blind values query clause.'''
        return self._NOBLIND


    @property
    def ALLBLIND(self):
        '''All blind values query clause.'''
        return self._ALLBLIND


    def commaSeparatedColumnsAsList(self, columns) -> list:
        '''Converts a comma separated string to list of strings'''
        if not columns.strip():
            return list()

        return list(filter(lambda x: x != '', map(lambda x: re.sub(r'\s+', '_', x.strip()), columns.split(','))))


    def createQueryString(self, clause: str, operation: str) -> str:
        '''Returns a query of the form: "col operation AND/OR col operation AND/OR ...
        for each col in quasiIdentifyingColumns.'''
        if 'AND' not in clause and 'OR' not in clause:
            logging.warning(f'Illegal clause: {clause}! Returning dummy condition.')
            return EMPTY_WHERE
        
        return clause.join([f"{i} {operation.strip()}" for i in self.commaSeparatedColumnsAsList(self.quasiIdentifyingColumns)]).strip()


    def dictToQueryString(self, clause: str, operation: str, queryDict: dict) -> str:
        '''Generates a where condition from a dictionary.'''
        if 'AND' not in clause and 'OR' not in clause:
            logging.warning(f'Illegal clause: {clause}! Returning dummy condition.')
            return EMPTY_WHERE
        
        res = ''
        for key, value in queryDict.items():
            if isinstance(value, str):
                value = "'" + value + "'"
            res += (str(key) + ' ' + operation.strip() + ' ' + str(value) + clause)
        return res[:-(len(clause))]