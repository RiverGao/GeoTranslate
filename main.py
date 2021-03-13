# -*- coding: utf-8 -*-
"""
Created on Sun Mar  7 22:57:43 2021

@author: 高长江
"""
from model import GeoTranslator
from data import readData, saveData
from tables import initTables

if __name__ == 'main':
    # 初始化4个表格：通名表，专名单元表，音节表，音标表
    tables = initTables()
    # 初始化翻译器
    translator = GeoTranslator(tables)
    # 输入要翻译的内容
    inputNames = readData()
    # 输出结果
    results = translator.run(inputNames)
    # 保存结果
    saveData(results)
    