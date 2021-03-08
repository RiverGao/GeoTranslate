# -*- coding: utf-8 -*-
"""
Created on Sun Mar  7 23:45:26 2021

@author: 高长江
"""

def initTables():
    # init all four tables
    # TODO: implement
    return


class Table():
    # Father class of tables
    def __init__(self, tableData):
        # TODO: implement
        self.data = tableData
    
    def inTable(self, key: str) -> bool:
        '''
        Checkout whether a key (source) is in the table

        Parameters
        ----------
        key : str
            The source name/unit/syllable/phonetic

        Returns
        -------
        bool
            the key is or is not in the table

        '''
        # TODO: implement
        return (key in self.tableData.keys())
    
    def lookup(self, key: str) -> str:
        '''
        Lookup the value (translation) of given key (source)

        Parameters
        ----------
        key : str
            The source name/unit/syllable/phonetic

        Returns
        -------
        str
            translation

        '''
        # TODO: implement
        return self.tableData[key]

class genericTable(Table):
    def __init__(self, tableData):
        # TODO: implement
        super(genericTable).__init__(tableData)

class unitTable(Table):
    def __init__(self, tableData):
        # TODO: implement
        super(unitTable).__init__(tableData)
        
class syllableTable(Table):
    def __init__(self, tableData):
        # TODO: implement
        super(syllableTable).__init__(tableData)

class phoneticTable(Table):
    def __init__(self, tableData):
        # TODO: implement
        super(phoneticTable).__init__(tableData)


































