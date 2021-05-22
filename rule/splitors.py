# -*- coding: utf-8 -*-
"""
Created on Mon Mar  8 21:04:05 2021

@author: 高长江
"""
from rule.tables import *
from rule.config import GEN_TOKEN

import eng_to_ipa as ipa

import torch
from neural_ipa.nmt_model import NMT
import sys
import nltk
from rule.vocab import Vocab

CUDA = torch.cuda.is_available()
word_ipa_dict = {}


class Splitor:
    # xxxSplitor 的父类
    def __init__(self, table):
        self.table = table


class nameSplitor(Splitor):
    def __init__(self, table, adj_table):
        self.adj_table = adj_table
        super(nameSplitor, self).__init__(table)

    def split(self, name: str) -> list:
        """
        拆分专名和通名

        Parameters
        ----------
        name : str
            经过预处理的完整地名

        Returns
        -------
        list
            [0]: int，主要通名在单词序列中的位置
            [1]: list，所有通名以及他们的翻译
            [3]: list，单词序列（英文）

        """
        words = name.split()  # 单词的列表
        possible_gen_idx = []  # indices of possible generic names
        possible_gen = []
        adj_gen = []  # 形容词通名
        ret = [None, None, None]  # 返回的列表
        for i in range(len(words)):
            if self.adj_table.inTable(words[i]):
                adj_gen.append(words[i])

        for i in range(len(words)):
            if self.table.inTable(words[i]):
                possible_gen_idx.append(i)
                possible_gen.append(words[i])

        def naiveChoose(src_words: list, possibles: list) -> int:
            # 朴素的确认通名的方法
            if len(possibles) == 0:  # 没有在词典中的通名
                return -2
            elif len(possibles) == 1:  # 只有一个候选
                return possibles[0]
            else:  # 不止一个候选
                if "of" in src_words and src_words.index("of") - 1 in possibles:
                    # 如果第一个 of 前的那个单词是可能的通名
                    # 例如： Royal Park of London City
                    return possibles[0]
                else:
                    # 否则返回最后一个候选
                    return possibles[-1]

        idx_gen = naiveChoose(words, possible_gen_idx)
        if idx_gen == -2 and len(adj_gen) > 0:
            idx_gen = -1
        # print("words:", words, "idx_gen:", idx_gen, "possible_gen:", possible_gen)
        if idx_gen == -2:
            # raise ValueError('Cannot find generic name in "{}"'.format(name))
            # 认为没有通名
            ret[1] = []
        else:
            ret[1] = []
            for i in possible_gen:
                ret[1].append((i, self.table.lookup(i)))
            for i in adj_gen:
                ret[1].append((i, self.adj_table.lookup(i)))
        # print(idx_gen)
        ret[0] = idx_gen
        ret[2] = words
        # print("ret", ret)
        return ret


class unitSplitor(Splitor):
    def split(self, name: list) -> list:
        """
        拆分专名的可翻译单元（现在只作简单实现）

        Parameters
        ----------
        name : list
            英文单词列表

        Returns
        -------
        list(str)
            可翻译单元的列表，一定为 [part1, GEN_TOKEN, part2] 的格式，
            part1, part2 可以为空字符串

        """
        ret = []
        idx_gen = name.index(GEN_TOKEN)
        # 将专名分成 3 部分： GEN_TOKEN 左、本身、右，左右两个部分可以为空字符串
        left = name[:idx_gen]
        right = name[idx_gen + 1 :]
        if len(right) > 0 and right[0] == "of":
            right.pop(0)  # 去掉开头的 of

        ret.append(" ".join(left))
        ret.append(GEN_TOKEN)
        ret.append(" ".join(right))
        return ret


class syllableSplitor(Splitor):
    def __init__(self, table):
        super(syllableSplitor, self).__init__(table)
        # print("load model from {}".format(model_path), file=sys.stderr)
        # self.vocab = Vocab.load('vocab.json')
        self.nmt_model = NMT.load("./neural_ipa/model.bin")
        if CUDA:
            self.nmt_model = self.nmt_model.to(torch.device("cuda:0"))
        self.nmt_model.eval()

    def predict(self, unit: list) -> str:
        """
        预测未登录词的 ipa 音标，需要逐单词翻译成音标

        Parameters
        ----------
        unit: List[str]
            专名单元，由一个或多个单词组成。
            每个单词都是小写全拼，可以含有 a-z，单引号和连字符

        Returns
        -------
        str
            ipa 音标

        """
        words = unit.split()  # 按空格分成单个单词
        ipas = []  # 每个单词对应一个音标
        for word in words:
            sent = " ".join(word).split()
            hyps = self.nmt_model.beam_search(sent)  # beam search 的 5 个结果
            pred = hyps[0].value  # 取可能性最高的
            # 去掉重音记号
            for mark in ["ˈ", "ˌ"]:
                if mark in pred:
                    pred.remove(mark)
            ipas.append("".join(pred))  # 保存音标
        result = " ".join(ipas)  # 与 ipa_convert 返回格式保持一致
        return result

    def split(self, unit: str) -> tuple:
        """
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

        """
        # 找不到办法对应音标和字母音节，暂时不实现音节拆分
        if unit == "":  # 空字符串，应该很常见
            return ("", "")  # 返回两个空字符串
        elif unit == GEN_TOKEN:  # 保留 token
            return (GEN_TOKEN, GEN_TOKEN)
        else:  # 正常情况
            # 跳过附录 C，只进行单词到音标的转换
            ret = ([], [])
            can_convert = ipa.isin_cmu(unit)
            if can_convert:
                ret[0].append(unit)
                ret[1].append(ipa.convert(unit, stress_marks="none"))
                word_ipa_dict[unit] = ipa.convert(unit, stress_marks="none")
                # print(word_ipa_dict)
                return ret
            else:  # 正常情况
                # 跳过附录 C，只进行单词到音标的转换
                ret = ([], [])
                can_convert = ipa.isin_cmu(unit)
                if can_convert:
                    ret[0].append(unit)
                    ret[1].append(ipa.convert(unit, stress_marks="none"))
                    word_ipa_dict[unit] = ipa.convert(unit, stress_marks="none")
                    # print(word_ipa_dict)
                    return ret
                else:  # 用模型预测音标
                    # raise ValueError('Cannot convert unit "{}" to IPA'.format(unit))
                    ret[0].append(unit)
                    ret[1].append(self.predict(unit))
                    return ret


class phoneticSplitor(Splitor):
    leadings = [
        "b",
        "p",
        "d",
        "t",
        "g",
        "k",
        "v",
        "w",
        "f",
        "z",
        "dz",
        "ts",
        "s",
        "ð",
        "θ",
        "ʒ",
        "ʃ",
        "ʤ",
        "ʧ",
        "h",
        "m",
        "n",
        "l",
        "r",
        "j",
        "gw",
        "kw",
        "hw",
    ]
    followings = [
        "æ",
        "ɑ",
        "ʌ",
        "a",
        "ɛ",
        "eɪ",
        "ə",
        "i",
        "ɪ",
        "ɔ",
        "o",
        "əʊ",
        "oʊ",
        "u",
        "ʊ",
        "ju",
        "jʊ",
        "aɪ",
        "aʊ",
        "æn",
        "an",
        "ʌn",
        "æŋ",
        "ɑn",
        "ʌŋ",
        "aʊn",
        "ɔn",
        "ɔŋ",
        "ən",
        "əŋ",
        "ɛn",
        "ɛŋ",
        "ɪn",
        "in",
        "ɪən",
        "jən",
        "ɪŋ",
        "iŋ",
        "un",
        "oʊn",
        "uŋ",
    ]

    def split(self, phonetic: str) -> list:
        """
        将转换后的国际音标字符串拆分成可查询的元音-辅音组合

        Parameters
        ----------
        phonetic : str
            音标字符串，单词之间有空格，可能为 GEN_TOKEN 或 None

        Returns
        -------
        list
            元辅音组合的列表

        """

        def clean(phonetic: str) -> list:
            # 转换之前还要清洗一下，主要做的事情有：
            # 1. 把 of 连在前一个词上（假设不会出现两个of）
            # 2. 词尾和下一个词开头辅音相同，则去除词尾的辅音
            phonetic = phonetic.replace(" əv", "əv")
            phon_list = phonetic.split()
            for i in range(len(phon_list)):
                if (
                    i >= 1
                    and phon_list[i][0] in self.leadings
                    and phon_list[i][0] == phon_list[i - 1][-1]
                ):
                    phon_list[i - 1] = phon_list[i - 1][:-1]
            return phon_list

        # phonetic 不可能是 GEN_TOKEN
        if phonetic == "":  # 如果是空字符串
            return []
        # 正常情况
        phon_list = clean(phonetic)
        ret_list = []
        for word in phon_list:
            _word = word  # 对 _word 进行多次切除
            element_list = []  # 用来存储 (leading, following)
            last_f = ""  # 存储上一个 following，针对其以 n 结尾且之后是元音的情况
            while len(_word) > 0:
                l = None  # leading phonetic
                f = None  # following phonetic
                heads = []
                if len(_word) == 1:
                    heads = [_word[0]]
                elif len(_word) == 2:
                    heads = [_word[:2], _word[0]]
                else:
                    heads = [_word[:3], _word[:2], _word[0]]
                # 前三个，前两个或者第一个音标
                for head in heads:
                    if head in self.leadings:  # 如果以辅音开头
                        l = head
                        _word = _word[len(head) :]  # 切掉 head
                        break
                    else:  # 检查是因为非法字符还是因为单独元音
                        if head in self.followings:  # 单独元音
                            if len(last_f) > 0 and last_f[-1] == "n":
                                l = "n"
                            else:
                                l = "none"
                            break
                else:
                    raise ValueError("Invalid leading phonetic: {}".format(head))
                # 然后确定 following
                # 还是考虑前三个，前两个和第一个
                tails = []  # 注意 _word 此时长度可能为 0
                if len(_word) == 1:
                    tails = [_word[0]]
                elif len(_word) == 2:
                    tails = [_word[:2], _word[0]]
                elif len(_word) > 2:
                    tails = [_word[:3], _word[:2], _word[0]]
                for tail in tails:
                    if tail in self.followings:
                        f = tail
                        _word = _word[len(tail) :]  # 切掉找到的 following
                        break
                else:  # 如果没找到 following，认为是单辅音
                    f = "none"

                element_list.append((l, f))  # 存储找到的 l-f 对
                last_f = f  # 存储 following

            # 一个单词找完之后
            # ret_list.extend(element_list)
            # print("element_list:", element_list)
            ret_list.append(element_list)
        # 全部找完以后
        # print(ret_list)
        return ret_list
