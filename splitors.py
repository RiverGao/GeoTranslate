# -*- coding: utf-8 -*-
"""
Created on Mon Mar  8 21:04:05 2021

@author: 高长江
"""
from tables import *
from config import GEN_TOKEN

import eng_to_ipa as ipa

class Splitor():
    # xxxSplitor 的父类
    def __init__(self, table: tables.Table):
        self.table = table

class nameSplitor(Splitor):
    def split(self, name: str)-> list:
        '''
        拆分专名和通名

        Parameters
        ----------
        name : str
            经过预处理的完整地名

        Returns
        -------
        list(str)
            [0]: list, 专名
            [1]: str, 通名

        '''
        words = name.split() # 单词的列表
        possible_gen_idx = [] # indices of possible generic names
        ret = [] # 返回的列表
        for i in range(len(words)):
            if self.table.inTable(words[i]):
                possible_gen_idx.append(i)
                
        def naiveChoose(src_words: list(str), possibles: list(str))-> int:
            # 朴素的确认通名的方法
            if len(possibles) == 0: # 没有在词典中的通名
                return -1
            elif len(possibles) == 1: # 只有一个候选
                return possibles[0]
            else: # 不止一个候选
                if 'of' in src_words and src_words.index('of') - 1 in possibles:
                    # 如果第一个 of 前的那个单词是可能的通名
                    # 例如： Royal Park of Blahblah City
                    return possibles[0]
                else:
                    # 否则返回最后一个候选
                    return  possibles[-1]
                
        idx_gen = naiveChoose(words, possible_gen_idx)
        if idx_gen == -1:
            raise ValueError('Cannot find generic name in "{}"'.format(name))
        else:
            ret[1] = self.table.lookup(words[idx_gen]) # 顺便翻译
            words[idx_gen] = GEN_TOKEN # 标记原来通名所在的位置
            ret[0] = words
            return ret

class unitSplitor(Splitor):
    def split(self, name: list) -> list(str):
        '''
        拆分专名的可翻译单元（现在只作简单实现）

        Parameters
        ----------
        name : list
            含有 GEN_TOKEN 的专名单词列表

        Returns
        -------
        list(str)
            可翻译单元的列表

        '''
        ret = []
        idx_gen = name.index(GEN_TOKEN)
        # 将专名分成 3 部分： GEN_TOKEN 前、本身、后，前后两个部分可以为空字符串
        ret.append(' '.join(name[: idx_gen]))
        ret.append(GEN_TOKEN)
        ret.append(' '.join(name[idx_gen + 1:]))
        return ret

class syllableSplitor(Splitor):
    def split(self, unit: str) -> tuple:
        '''
        将专名单元按音节拆分

        Parameters
        ----------
        unit : str
            专名单元，可能为 GEN_TOKEN

        Returns
        -------
        tuple
            [0]: 拆分后的音节列表（字母），或 GEN_TOKEN，或空
            [1]: 拆分后的音节列表（音标），或 GEN_TOKEN，或空

        '''
        if unit == '': # 空字符串，应该很常见
            return (None, None) # 返回 None, None
        elif unit == GEN_TOKEN: # 保留 token
            return (GEN_TOKEN, GEN_TOKEN)
        else: # 正常情况
            whole_phonics = ipa.convert(unit)
            # TODO: implement
            # 此处规则较为复杂，可能 unit split 和 syllable split 之间还需要一个环节
        return None
        
































