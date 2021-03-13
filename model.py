# -*- coding: utf-8 -*-
"""
Created on Sun Mar  7 23:44:50 2021

@author: 高长江
"""

from tables import genericTable, unitTable, syllableTable, phoneticTable
from splitors import nameSplitor, unitSplitor, syllableSplitor, phoneticSplitor

class GeoTranslator():
    
    def __init__(self, tableData):
        # 四个表格分别是四个类，tableData 包含 4 个字典的数据
        self.genericTable = genericTable(tableData[0])
        self.unitTable = unitTable(tableData[1])
        self.syllableTable = syllableTable(tableData[2])
        self.phoneticTable = phoneticTable(tableData[3])
        
        # 四个拆分器
        self.nameSplitor = nameSplitor()
        self.unitSplitor = unitSplitor()
        self.syllableSplitor = syllableSplitor()
        self.phoneticSplitor = phoneticSplitor()
        
        # 用于处理未登录词的神经网络（暂时不用）
        self.network = None
    
    def preprocess(self, inputNames: list(str)) -> list(str):
        '''
        Preprocess the input names, including stripping and capitalization etc.

        Parameters
        ----------
        inputNames : list(str)
            Raw input geographic names.

        Returns
        -------
        list(str)
            Preprocessed input geographic names.

        '''
        # TODO: implement
        return None
    
    def nameSplit(self, name: str) -> tuple(list, str):
        '''
        Split the specific name and the generic name.

        Parameters
        ----------
        Name : str
            The preprocessed name.

        Returns
        -------
        tuple(list, str) :
            [0]: Specific name in word list form
            [1]: Translated generic name
        '''
        spec, genT = self.nameSplitor.split(name)
        return (spec, genT)
    
    def unitSplit(self, specName: list(str)) -> list(str):
        '''
        Split the whole specific name into one or several translatable units.

        Parameters
        ----------
        specName : list(str)
            Whole specific names with GEN_TOKEN in list form.

        Returns
        -------
        list(str)
            A list of specific name units.
        '''
        units = self.unitSplitor.split(specName)
        return units
    
    def syllabSplit(self, unit: str) -> tuple(list(str), list(str)):
        '''
        Split an unknown specific name unit into several syllables together with
        corresponding phonetics.

        Parameters
        ----------
        unit : str
            a specific name unit

        Returns
        -------
        tuple(list(str), list(str))
            [0]: list of syllables
            [1]: list of phonetics
        '''
        syllables, phonetics = self.syllableSplitor.split(unit)
        return (syllables, phonetics)
    
    def phoneticSplit(self, phonetic: str) -> list(str):
        '''
        Split the phonetics of an unknown syllable into several single phonetics

        Parameters
        ----------
        phonetic : str
            phonetics of an unknown syllable in syllableTable

        Returns
        -------
        list(str)
            list of single phonetics

        '''
        return self.phoneticSplitor.split(phonetic)
    
    def specTranslate(self, specName: list(str)) -> list(str):
        '''
        Translate the specific name after split from the generic name.

        Parameters
        ----------
        specName : str
            Whole specific name derived from spec_genSplit

        Returns
        -------
        str :
            Translated specific name.
        '''
        units = self.unitSplit(self, specName)
        specT = []
        for unit in units:
            unitT = self.unitTranslate(unit)
            specT.append(unitT)
        return specT
    
    def unitTranslate(self, unit: str) -> str:
        '''
        Translate a specific name unit.

        Parameters
        ----------
        unit : str
            specific name unit

        Returns
        -------
        str
            translation of the unit
        '''
        
        if self.unitTable.inTable(unit): # 如果专名单元在表内
            return self.unitTable.lookup(unit)
        
        else: # 专名单元不在表内
            syllables, phonetics = self.syllabSplit(unit) # 按音节拆分，并得到对应音标片段
            syllablesT = [] # 存储各个音节的翻译
            
            for syllable, phonetic in zip(syllables, phonetics): 
                # 此处的 phonetic 是音节对应的音标片段
                if self.syllableTable.inTable(syllable): # 音节在表内
                    syllablesT.append(self.syllableTable.lookup(syllable))
                
                else: # 音节不在表内
                    singlePhonetics = self.phoneticSplit(phonetic) # 拆分成单音标的列表
                    phonesT = [] # 存储各个音标的翻译
                    for singlePhonetic in singlePhonetics:
                        assert self.phoneticTable.inTable(singlePhonetic) # 假设所有音标都能找到翻译
                        phonesT.append(self.phoneticTable.lookup(singlePhonetic))
                    syllablesT.append(''.join(phonesT))
            
            translation = ''.join(syllablesT)
            return translation
    
    def merge(self, translatedSpec: str, translatedGen: str) -> str:
        '''
        Merge the translated specific and generic name.

        Parameters
        ----------
        translatedSpec : str
            Translated specific name.
        translatedGen : str
            Translated generic name.

        Returns
        -------
        str
            Merged result.
        '''
        # TODO: implement
        return None
    
    def run(self, inputNames: list(str)) -> list(str):
        '''
        Run the translator and generate translation results.

        Parameters
        ----------
        inputNames : list(str)
            Raw input geographic names.

        Returns
        -------
        list(str)
            Translated geographic names.

        '''
        names = self.preprocess(inputNames)
        results = []
        for name in names:
            spec, genT = self.nameSplit(name)
            specT = self.specTranslate(spec)
            results.append(self.merge(specT, genT))
        
        return results



























