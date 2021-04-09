# -*- coding: utf-8 -*-
"""
Created on Mon Mar  8 21:04:05 2021

@author: 高长江
"""
from tables import *
from config import GEN_TOKEN

import eng_to_ipa as ipa

word_ipa_dict = {}
class Splitor():
    # xxxSplitor 的父类
    def __init__(self, table):
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
        list
            [0]: list, 专名单词列表，包含 GEN_TOKEN
            [1]: str, 通名，可能为空字符串

        '''
        words = name.split() # 单词的列表
        possible_gen_idx = [] # indices of possible generic names
        ret = [None, None, None] # 返回的列表
        for i in range(len(words)):
            if self.table.inTable(words[i]):
                possible_gen_idx.append(i)
                
        def naiveChoose(src_words: list, possibles: list)-> int:
            # 朴素的确认通名的方法
            if len(possibles) == 0: # 没有在词典中的通名
                return -1
            elif len(possibles) == 1: # 只有一个候选
                return possibles[0]
            else: # 不止一个候选
                if 'of' in src_words and src_words.index('of') - 1 in possibles:
                    # 如果第一个 of 前的那个单词是可能的通名
                    # 例如： Royal Park of London City
                    return possibles[0]
                else:
                    # 否则返回最后一个候选
                    return  possibles[-1]
                
        idx_gen = naiveChoose(words, possible_gen_idx)
        if idx_gen == -1:
            # raise ValueError('Cannot find generic name in "{}"'.format(name))
            # 认为没有通名
            ret[1] = ''
            words.append(GEN_TOKEN)
        else:
            ret[2] = words[idx_gen]
            ret[1] = self.table.lookup(words[idx_gen]) # 顺便翻译
            words[idx_gen] = GEN_TOKEN # 标记原来通名所在的位置
            # 原因：当 unit 不止两个时，需要知道通名的位置，以确定专名的排列顺序
        
        ret[0] = words
        return ret

class unitSplitor(Splitor):
    def split(self, name: list) -> list:
        '''
        拆分专名的可翻译单元（现在只作简单实现）

        Parameters
        ----------
        name : list
            含有 GEN_TOKEN 的专名单词列表

        Returns
        -------
        list(str)
            可翻译单元的列表，一定为 [part1, GEN_TOKEN, part2] 的格式，
            part1, part2 可以为空字符串

        '''
        ret = []
        idx_gen = name.index(GEN_TOKEN)
        # 将专名分成 3 部分： GEN_TOKEN 左、本身、右，左右两个部分可以为空字符串
        left = name[: idx_gen]
        right = name[idx_gen + 1:]
        if len(right) > 0 and right[0] == 'of':
            right.pop(0) # 去掉开头的 of
        
        ret.append(' '.join(left))
        ret.append(GEN_TOKEN)
        ret.append(' '.join(right))
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
            [0]: 拆分后的音节列表（字母），或 GEN_TOKEN，或空字符串
            [1]: 拆分后的音节列表（音标），或 GEN_TOKEN，或空字符串

        '''
        # 找不到办法对应音标和字母音节，暂时不实现音节拆分 
        if unit == '': # 空字符串，应该很常见
            return ('', '') # 返回两个空字符串
        elif unit == GEN_TOKEN: # 保留 token
            return (GEN_TOKEN, GEN_TOKEN)
        else: # 正常情况
            # 跳过附录 C，只进行单词到音标的转换
            ret = ([], [])
            can_convert = ipa.isin_cmu(unit)
            if can_convert:
                ret[0].append(unit)
                ret[1].append(ipa.convert(unit, stress_marks='none'))
                word_ipa_dict[unit] = ipa.convert(unit, stress_marks='none')
                #print(word_ipa_dict)
                return ret
            else:
                raise ValueError('Cannot convert unit "{}" to IPA'.format(unit))

class phoneticSplitor(Splitor):
    leadings = ['b', 'p', 'd', 't', 'g', 'k', 'v', 'w', 'f',
                'z', 'dz', 'ts', 's', 'ð', 'θ', 'ʒ', 'ʃ', 'ʤ',
                'ʧ', 'h', 'm', 'n', 'l', 'r', 'j', 'gw',
                'kw', 'hw']
    followings = ['æ', 'ɑ', 'ʌ', 
                  'ɛ', 'eɪ', 
                  'ə', 
                  'i', 'ɪ',
                  'ɔ', 'o', 'əʊ', 'oʊ',
                  'u', 
                  'ju', 
                  'aɪ', 
                  'aʊ',
                  'æn', 'an', 'ʌn', 'æŋ',
                  'ɑn', 'ʌŋ', 'aʊn', 'ɔn', 'ɔŋ',
                  'ən', 'əŋ', 'ɛn', 'ɛŋ',
                  'ɪn', 'in', 'ɪən', 'jən',
                  'ɪŋ','iŋ',
                  'un', 'oʊn',
                  'uŋ']
    def split(self, phonetic: str) -> list:
        '''
        将转换后的国际音标字符串拆分成可查询的元音-辅音组合

        Parameters
        ----------
        phonetic : str
            音标字符串，单词之间有空格，可能为 GEN_TOKEN 或 None

        Returns
        -------
        list
            元辅音组合的列表

        '''
        def clean(phonetic: str) -> list:
            # 转换之前还要清洗一下，主要做的事情有：
            # 1. 把 of 连在前一个词上（假设不会出现两个of）
            # 2. 词尾和下一个词开头辅音相同，则去除词尾的辅音
            phonetic = phonetic.replace(' əv', 'əv')
            phon_list = phonetic.split()
            for i in range(len(phon_list)):
                if i >= 1 and phon_list[i][0] in self.leadings \
                    and  phon_list[i][0] == phon_list[i-1][-1]:
                    phon_list[i-1] = phon_list[i-1][:-1]
            return phon_list
        
        # phonetic 不可能是 GEN_TOKEN
        if phonetic == '': # 如果是空字符串
            return []
        # 正常情况
        phon_list = clean(phonetic)
        ret_list = []
        for word in phon_list:
            _word = word # 对 _word 进行多次切除
            element_list = [] # 用来存储 (leading, following)
            while len(_word) > 0:
                l = None # leading phonetic
                f = None # following phonetic
                head = _word[0] # 第一个音标
                if head in self.leadings: # 如果以辅音开头
                    l = head
                    _word = _word[1:] # 切掉 head
                else: # 检查是因为非法字符还是因为单独元音
                    if head in self.followings:
                        l = 'none'
                    else:
                        raise ValueError('Invalid leading phonetic: {}'.format(head))
                # 然后确定 following
                # 先认为 leading 之后的都是，再一个个排除
                tail = _word
                while len(tail) > 0:
                    if tail in self.followings:
                        f = tail
                        break
                    else:
                        tail = tail[:-1] # 去掉最后一个音标
                else: # 如果没找到 following，认为是单辅音
                    f = 'none'
                
                element_list.append((l, f)) # 存储找到的 l-f 对
                _word = _word[len(tail):] # 切掉找到的 following
            # 一个单词找完之后
            #ret_list.extend(element_list)
            #print("element_list:", element_list)
            ret_list.append(element_list)
        # 全部找完以后
        #print(ret_list)
        return ret_list
                    
                
            




























