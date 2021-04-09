# -*- coding: utf-8 -*-
"""
Created on Sun Mar  7 23:44:50 2021

@author: 高长江
"""

from tables import genericTable, unitTable, syllableTable, phoneticTable
from splitors import nameSplitor, unitSplitor, syllableSplitor, phoneticSplitor
from config import GEN_TOKEN
import copy

class GeoTranslator():
    
    def __init__(self, tableData):
        # 四个表格分别是四个类，tableData 包含 4 个字典的数据
        self.genericTable = genericTable(tableData[0])
        self.unitTable = unitTable(tableData[1])
        self.syllableTable = syllableTable(tableData[2])
        self.phoneticTable = phoneticTable(tableData[3])
        
        # 四个拆分器
        self.nameSplitor = nameSplitor(self.genericTable)
        self.unitSplitor = unitSplitor(self.unitTable)
        self.syllableSplitor = syllableSplitor(self.syllableTable)
        self.phoneticSplitor = phoneticSplitor(self.phoneticTable)
        
        # 用于处理未登录词的神经网络（暂时不用）
        self.network = None
    
    def preprocess(self, inputNames: list) -> list:
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
        processed = []
        for name in inputNames:
            # 全部化成小写并去除空格
            # TODO: 可能需要进一步处理
            _name = name.strip().lower()
            processed.append(_name)
        return processed
    
    def nameSplit(self, name: str) -> tuple:
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
        spec, genT, gen = self.nameSplitor.split(name)
        return (spec, genT, gen)
    
    def unitSplit(self, specName: list) -> list:
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
    
    def syllabSplit(self, unit: str) -> tuple:
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
    
    def phoneticSplit(self, phonetic: str) -> list:
        '''
        Split the phonetics of an unknown syllable into several single phonetics

        Parameters
        ----------
        phonetic : str
            phonetics of an unknown syllable in syllableTable

        Returns
        -------
        list(str)
            list of single phonetics, each is tuple(leading, following)

        '''
        return self.phoneticSplitor.split(phonetic)
    
    def specTranslate(self, spec: str) -> list:
        '''
        Translate the specific name after split from the generic name.

        Parameters
        ----------
        specName : list
            Parts of specific name derived from nameSplit
            e.g.: ['royal', GEN_TOKEN, 'london'], 
                  ['yellow stone', GEN_TOKEN, ''], [', GEN_TOKEN, 'fuji']

        Returns
        -------
        list :
            Translated specific name parts.
            e.g.: ['皇家', GEN_TOKEN, '伦敦']
        '''
        units = self.unitSplit(spec)

        #print("units", units)
        specT = []
        for unit in units:
            unitT = self.unitTranslate(unit)
            #print(unitT)
            specT.append(unitT)
        #print(specT)
        return specT
    
    def unitTranslate(self, unit: str):
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
        elif unit == GEN_TOKEN:
            return GEN_TOKEN
        else: # 专名单元不在表内
            syllables, phonetics = self.syllabSplit(unit) # 按音节拆分，并得到对应音标片段
            #print("syllables", syllables)
            #print("phonetics", phonetics)
            syllablesT = [] # 存储各个音节的翻译
            female_syllablesT = []
            for syllable, phonetic in zip(syllables, phonetics): 
                # 此处的 phonetic 是音节对应的音标片段
                #print("syllable", syllable, "phonetic", phonetic)
                if self.syllableTable.inTable(syllable): # 音节在表内
                    new_word = self.syllableTable.lookup(syllable)
                    syllablesT.append(new_word)
                    female_syllablesT.append(new_word)
                
                else: # 音节不在表内
                    singlePhonetics = self.phoneticSplit(phonetic) # 拆分成单音标的列表
                    #print("singlePhonetics:", singlePhonetics)
                    for word in singlePhonetics:
                        phonesT = []  # 存储各个音标的翻译
                        female_phonesT = []
                        for singlePhonetic in word:
                            if not self.phoneticTable.inTable(singlePhonetic):
                            # 假设所有音标都能找到翻译
                                raise ValueError('Invalid phonetic pair: {}'.format(singlePhonetic))
                            phonesT.append(self.phoneticTable.lookup(singlePhonetic))
                        #print('phoneT:', phonesT)
                        wordT = ""
                        femaleT = ""
                        for item in phonesT:
                            lst = item.split(" ")
                            wordT += lst[0]
                            femaleT += lst[-1]
                        syllablesT.append(wordT)
                        female_syllablesT.append(femaleT)
            translation = ''.join(syllablesT)
            #print("syllablesT:", syllablesT)
            #print("female_syllablesT", female_syllablesT)
            expression_res = [[copy.deepcopy(syllablesT), ""], ]
            for i in range(0, len(syllablesT)):
                if syllablesT[i] != female_syllablesT[i]:
                    temp = copy.deepcopy(expression_res)
                    for item in temp:
                        #print("item", item)
                        item[0][i] = female_syllablesT[i]
                        item[1] += "assuming \"{}\" as female name, \"{}\" ".format( syllable.split(" ")[i], female_syllablesT[i])
                    expression_res += temp
            for item in expression_res:
                item[0] = ''.join(item[0])
            #print("expression_res", expression_res)
            #print("translation:", translation)
            return expression_res
    
    def merge(self, translatedSpec: list, translatedGen: str, originalGen: str) -> list:
        '''
        Merge the translated specific and generic name.

        Parameters
        ----------
        translatedSpec : list
            翻译后的专名列表，包含 GEN_TOKEN
            例如：['皇家', GEN_TOKEN, '伦敦']，['', GEN_TOKEN, '富士']
        translatedGen : str
            翻译后的通名，可能为空字符串
            例如：'俱乐部'，'山'
        Returns
        -------
        str
            专名和通名按一定顺序组合
            顺序为：GEN_TOKEN 两侧分别从左到右，然后将左中右三个部分按照右-左-中排列
            例如：'伦敦皇家俱乐部'，'富士山'
            
        '''
        #print("translatedGen", translatedGen)
        idx_gen = translatedSpec.index(GEN_TOKEN)
        left_part = translatedSpec[:idx_gen]
        right_part = translatedSpec[idx_gen + 1:]
        if len(left_part) == 1:
            left_part = left_part[0]
        if len(right_part) == 1:
            right_part = right_part[0]
        #print("left:", left_part, "right", right_part)
        names = []
        final_res = []
        for left_item in left_part:
            for right_item in right_part:
                names.append([left_item[0] + right_item[0], left_item[1] + right_item[1]])
        #print("names:", names)
        for name in names:
            if name[0][0:3] == "弗/夫" or name[0][0:3] == "东/栋" or \
                    name[0][0:3] == "西/锡" or name[0][0:3] == "南/楠":
                init = name[0][2]
                name[0] = init + name[0][2:]
            if name[0][-3:] == "海/亥":
                if translatedGen == "":
                    name[0] = name[0][0:-3] + "亥"
            res = [""]
            pairs = []
            rests = []
            pos = 0
            for i in range(0, len(name[0])):
                if name[0][i] == '/':
                    pairs.append((name[0][i - 1], name[0][i + 1]))
                    rests.append(name[0][pos: i - 1])
                    pos = i + 2
            rests.append(name[0][pos: len(name[0])])
            for pair_num in range(0, len(pairs)):
                for res_num in range(0, len(res)):
                    res[res_num] += rests[pair_num]
                temp = copy.deepcopy(res)
                for res_num in range(0, len(res)):
                    res[res_num] += pairs[pair_num][0]
                for temp_num in range(0, len(temp)):
                    temp[temp_num] += pairs[pair_num][1]
                res += temp
            for res_num in range(0, len(res)):
                res[res_num] += rests[len(pairs)]
                res[res_num] = [res[res_num], name[1]]
            #print("rests", rests)
            #print("res", res)
            all_genT = translatedGen.split("/")
            temp = copy.deepcopy(res)
            res = []
            for genT in all_genT:
                for item in temp:
                    if genT != "":
                        expression = item[1] + "assuming {} as a general name {}".format(originalGen, genT)
                    else:
                        expression = item[1]
                    res.append([item[0] + genT, expression])
            final_res += res
            #print("res", res)

        #print("final_res", final_res)
        return final_res
    
    def run(self, inputNames: list) -> list:
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
            spec, genT, gen = self.nameSplit(name)
            #print("spec:", spec, "genT:", genT, "gen:", gen)
            #print("genT", genT)
            specT = self.specTranslate(spec)
            #print("specT:", specT)
            results.append(self.merge(specT, genT, gen))
        return results



























