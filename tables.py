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
    # 通名的英文-中文字典
    def __init__(self, tableData):
        # TODO: implement
        super(genericTable, self).__init__(tableData)

class unitTable(Table):
    # 专名单元的英文-中文字典（暂时不用）
    def __init__(self, tableData):
        # TODO: implement
        super(unitTable, self).__init__(tableData)
        
class syllableTable(Table):
    # 特殊音节（附录C）的英文-中文字典
    def __init__(self, tableData):
        # TODO: implement
        super(syllableTable, self).__init__(tableData)

class phoneticTable(Table):
    # 音标的英文-中文字典（就是那个大表格）
    def __init__(self, tableData):
        # TODO: implement
        super(phoneticTable, self).__init__(tableData)


































