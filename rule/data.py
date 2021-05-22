# -*- coding: utf-8 -*-
"""
Created on Sun Mar  7 23:45:14 2021

@author: 高长江
"""


def readData(filename):
    # 读取要翻译的英文
    lines = []
    with open(filename, "r") as f:
        lines = f.read().splitlines()
    return lines


def printResult(inputs, results):
    for src, trans in zip(inputs, results):
        print("原单词：{}".format(src))
        for i in range(len(trans)):
            print("翻译 {}: {}，原因：{}".format(i + 1, trans[i][0], trans[i][1]))


def saveData(saveDIR):
    # save the translated geographical names into saveDIR
    # TODO: implement
    return None
