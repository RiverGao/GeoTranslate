# -*- coding: utf-8 -*-
"""
Created on Sun Mar  7 23:45:26 2021

@author: 高长江
"""
import csv

def initTables() -> list:
    '''
    初始化四个字典

    Returns
    -------
    list
        长度为 4 的列表，每个元素是一个字典
        [0]: 通名
        [1]: 单元
        [2]: 音节
        [3]: 音标

    '''
    phonetics = {}
    with open('phonetics.csv', 'r', encoding='utf-8') as f:
        reader = csv.reader(f)
        for row in reader:
            phonetics[(row[0], row[1])] = row[2]
    female = {}
    with open('female.csv', 'r', encoding='utf-8') as f:
        reader = csv.reader(f)
        for row in reader:
            female[(row[0], row[1])] = row[2]
    generics = {}
    with open('generics.csv', 'r', encoding='utf-8') as f:
        reader = csv.reader(f)
        for row in reader:
            generics[row[0]] = row[1]
    units = {}
    with open('units.csv', 'r', encoding='utf-8') as f:
        reader = csv.reader(f)
        for row in reader:
            units[row[0]] = row[1]
    with open('big_dict.csv', 'r', encoding='utf-8') as f:
        reader = csv.reader(f)
        for row in reader:
            units[row[1]] = row[3]
    adj_generics = {}
    with open('adj.csv', 'r', encoding='utf-8') as f:
        reader = csv.reader(f)
        for row in reader:
            adj_generics[row[0]] = row[1]
    prefix = {}
    with open('prefix.csv', 'r', encoding='utf-8') as f:
        reader = csv.reader(f)
        for row in reader:
            prefix[row[0]] = (row[1], row[2])
    suffix = {}
    with open('suffix.csv', 'r', encoding='utf-8') as f:
        reader = csv.reader(f)
        for row in reader:
            suffix[row[0]] = (row[1], row[2])
    tables = []
    tables.append(generics)
    tables.append(units)
    tables.append(prefix)
    tables.append(suffix)
    tables.append(phonetics)
    tables.append(female)
    tables.append(adj_generics)

    return tables

class Table():
    # Father class of tables
    def __init__(self, tableData):
        # tableData 是一个字典
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
        return (key in self.data)

    def lookup(self, key: str) -> str:
        '''
        Lookup the value (translation) of given key (source)

        Parameters
        ----------
        key : str
            The source name/unit/syllable/phonetic
            其中 phonetic 需要重写
        Returns
        -------
        str
            translation

        '''
        return self.data[key]

class genericTable(Table):
    # 通名的英文-中文字典
    def __init__(self, tableData):
        # TODO: implement
        super(genericTable, self).__init__(tableData)

class adjTable(Table):
    # 形容词性通名的英文-中文字典
    def __init__(self, tableData):
        # TODO: implement
        super(adjTable, self).__init__(tableData)

class unitTable(Table):
    # 专名单元的英文-中文字典
    def __init__(self, tableData):
        # TODO: implement
        super(unitTable, self).__init__(tableData)

class prefixTable(Table):
    # 特殊音节（附录C）的英文-中文字典
    def __init__(self, tableData):
        # TODO: implement
        super(prefixTable, self).__init__(tableData)

class suffixTable(Table):
    # 特殊音节（附录C）的英文-中文字典
    def __init__(self, tableData):
        # TODO: implement
        super(suffixTable, self).__init__(tableData)

class phoneticTable(Table):
    # 音标的英文-中文字典（就是那个大表格）
    def __init__(self, tableData):
        # TODO: implement
        super(phoneticTable, self).__init__(tableData)

class femaleTable(Table):
    # 女性人名的英文-中文字典
    def __init__(self, tableData):
        # TODO: implement
        super(femaleTable, self).__init__(tableData)
