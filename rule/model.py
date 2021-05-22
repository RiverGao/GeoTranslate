# -*- coding: utf-8 -*-
"""
Created on Sun Mar  7 23:44:50 2021

@author: 高长江
"""

from rule.tables import *
from rule.splitors import nameSplitor, unitSplitor, syllableSplitor, phoneticSplitor
from rule.config import GEN_TOKEN
from rule.result import Result
import copy


class GeoTranslator:
    def __init__(self, tableData):
        # 四个表格分别是四个类，tableData 包含 4 个字典的数据
        self.genericTable = genericTable(tableData[0])
        self.unitTable = unitTable(tableData[1])
        self.prefixTable = prefixTable(tableData[2])
        self.suffixTable = suffixTable(tableData[3])
        self.phoneticTable = phoneticTable(tableData[4])
        self.femaleTable = femaleTable(tableData[5])
        self.adjTable = adjTable(tableData[6])

        # 四个拆分器
        self.nameSplitor = nameSplitor(self.genericTable, self.adjTable)
        self.unitSplitor = unitSplitor(self.unitTable)
        self.syllableSplitor = syllableSplitor(self.prefixTable)
        self.phoneticSplitor = phoneticSplitor(self.phoneticTable)

        # 用于处理未登录词的神经网络（暂时不用）
        self.network = None

    def preprocess(self, inputNames: list) -> list:
        """
        Preprocess the input names, including stripping and capitalization etc.

        Parameters
        ----------
        inputNames : list(str)
            Raw input geographic names.

        Returns
        -------
        list(str)
            Preprocessed input geographic names.

        """
        processed = []
        for name in inputNames:
            # 全部化成小写并去除空格
            # TODO: 可能需要进一步处理
            _name = name.strip().lower()
            _name = _name.replace("'s", "")
            processed.append(_name)
        return processed

    def nameSplit(self, name: str, res: Result) -> list:
        """
        Split the specific name and the generic name.

        Parameters
        ----------
        Name : str
            The preprocessed name.

        Returns
        -------
        tuple(list, str) :
            [0]: index of the main generic name
            [1]: pairs of generic names and their translations
        """
        idx, spec_pairs, words = self.nameSplitor.split(name)
        res.saveMainIdx(idx)
        for pair in spec_pairs:
            res.saveGen(pair[0], pair[1])
        res.saveStruct(words)
        return words

    def unitSplit(self, specName: list) -> list:
        """
        Split the whole specific name into one or several translatable units.

        Parameters
        ----------
        specName : list(str)
            Whole specific names with GEN_TOKEN in list form.

        Returns
        -------
        list(str)
            A list of specific name units.
        """
        units = self.unitSplitor.split(specName)
        return units

    def syllabSplit(self, unit: str) -> tuple:
        """
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
        """
        syllables, phonetics = self.syllableSplitor.split(unit)
        return (syllables, phonetics)

    def phoneticSplit(self, phonetic: str) -> list:
        """
        Split the phonetics of an unknown syllable into several single phonetics

        Parameters
        ----------
        phonetic : str
            phonetics of an unknown syllable in syllableTable

        Returns
        -------
        list(str)
            list of single phonetics, each is tuple(leading, following)

        """
        return self.phoneticSplitor.split(phonetic)

    def specTranslate(self, spec: list, res: Result):
        """
        Translate the specific name after split from the generic name.

        Parameters
        ----------
        specName : list
            original word list
            e.g.: ['royal', 'park', 'of', 'london', 'city']

        Returns
        -------
        list :
            Translated specific name parts.
            e.g.: ['皇家', GEN_TOKEN, '伦敦']
        """
        # units = self.unitSplit(spec)

        # print("units", units)
        specT = []
        for i in range(0, len(spec)):
            word = spec[i]
            if word == "of":
                continue
            else:
                if i + 1 < len(spec) and spec[i + 1] == "of":
                    word += " of"
            wordT, femaleT = self.unitTranslate(word)
            # print(unitT)
            specT.append(wordT)
            res.saveSpec(word, wordT)
            if wordT != femaleT:
                res.saveSpecFemale(word, femaleT)
        # print("specT:", specT)

    def unitTranslate(self, unit: str) -> tuple:
        """
        Translate a specific name unit.

        Parameters
        ----------
        unit : str
            specific name unit

        Returns
        -------
        str
            translation of the unit
        """
        # if self.unitTable.inTable(unit): # 如果专名单元在表内
        #    return self.unitTable.lookup(unit)
        syllables, phonetics = self.syllabSplit(unit)  # 按音节拆分，并得到对应音标片段
        syllablesT = ""  # 存储各个音节的翻译
        female_syllablesT = ""
        for syllable, phonetic in zip(syllables, phonetics):
            # 此处的 phonetic 是音节对应的音标片段
            # print("syllable", syllable, "phonetic", phonetic)
            syllable_cap = syllable.capitalize()
            if syllable == "with" or syllable == "and":
                syllablesT += "-"
                female_syllablesT += "-"
            elif self.unitTable.inTable(syllable_cap):  # 音节在表内
                new_word = self.unitTable.lookup(syllable_cap)
                syllablesT += new_word
                female_syllablesT += new_word

            else:  # 音节不在表内
                singlePhonetics = self.phoneticSplit(phonetic)  # 拆分成单音标的列表
                # print(singlePhonetics)
                # 4.16.2021
                front_part = ""
                prefix = ""
                prefix_len = 0
                for letter in syllable:
                    front_part += letter
                    if self.prefixTable.inTable(front_part):
                        prefix, prefix_len = self.prefixTable.lookup(front_part)
                syllable_length = len(syllable)
                back_part = ""
                suffix = ""
                suffix_len = 0
                for i in range(1, syllable_length + 1):
                    back_part = syllable[-i] + back_part
                    if self.suffixTable.inTable(back_part):
                        suffix, suffix_len = self.suffixTable.lookup(back_part)
                singlePhonetics[0] = singlePhonetics[0][
                    prefix_len : len(singlePhonetics[0]) - int(suffix_len)
                ]
                # 最好改一下
                # 4.16.2021
                # print("singlePhonetics:", singlePhonetics)
                for word in singlePhonetics:
                    phonesT = []  # 存储各个音标的翻译
                    female_phonesT = []  # 存储各个音标的女性化翻译
                    for singlePhonetic in word:
                        if not self.phoneticTable.inTable(singlePhonetic):
                            # 假设所有音标都能找到翻译
                            raise ValueError(
                                "Invalid phonetic pair: {}".format(singlePhonetic)
                            )
                        phonesT.append(self.phoneticTable.lookup(singlePhonetic))
                        if self.femaleTable.inTable(singlePhonetic):
                            female_phonesT.append(
                                self.femaleTable.lookup(singlePhonetic)
                            )
                        else:
                            female_phonesT.append(
                                self.phoneticTable.lookup(singlePhonetic)
                            )
                    wordT = ""
                    femaleT = ""
                    for common, female in zip(phonesT, female_phonesT):
                        wordT += common
                        femaleT += female
                    syllablesT += wordT
                    female_syllablesT += femaleT
                # 4.16.2021
                syllablesT = prefix + syllablesT + suffix
                female_syllablesT = prefix + female_syllablesT + suffix
        # print("syllablesT:", syllablesT)
        # print("female_syllablesT", female_syllablesT)
        return (syllablesT, female_syllablesT)

    def run(self, inputNames: list) -> list:
        """
        Run the translator and generate translation results.

        Parameters
        ----------
        inputNames : list(str)
            Raw input geographic names.

        Returns
        -------
        list(str)
            Translated geographic names.

        """
        names = self.preprocess(inputNames)
        results = []
        for name in names:
            res = Result()
            words = self.nameSplit(name, res)
            self.specTranslate(words, res)
            res.merge()
            results.append(res.getRes())
        return results
