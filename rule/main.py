# -*- coding: utf-8 -*-
"""
Created on Sun Mar  7 22:57:43 2021

@author: 高长江
"""
from rule.model import GeoTranslator
from rule.data import readData, printResult, saveData
from rule.tables import initTables

import sys

# 命令行需要指定输入文件，否则默认为 examples.txt
inputFile = None
if len(sys.argv) == 1:
    print('运行方式： python3 main.py [input file]')
    print('未指定文件，默认读取 examples.txt')
    inputFile = 'examples.txt'
elif len(sys.argv) == 2:
    inputFile = sys.argv[1]
else:
    raise RuntimeError('Too many commandline arguments')

# 初始化4个表格：通名表，专名单元表，音节表，音标表
tableData = initTables()
# 初始化翻译器
translator = GeoTranslator(tableData)
# 输入要翻译的内容
inputNames = readData(inputFile)
# 输出结果
results = translator.run(inputNames)
# 打印结果
printResult(inputNames, results)

# 保存结果
# saveData(results)
    
