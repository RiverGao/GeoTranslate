# GeoTranslate：基于规则的英-中地理名词翻译系统
## 简介
本项目主要解决英文地理名词的规范化翻译问题，根据国家标准《外语地名汉字译写导则 英语》（GB/T 17693.1-2008）规定的音译、意译规则实现。

## 依赖库
本工具的主要依赖库包括：pytorch, [eng-to-ipa](https://github.com/mphilli/English-to-IPA), docopt

## 下载方法
在命令行输入：
```$ git clone https://github.com/RiverGao/GeoTranslate```
或直接下载 zip 文件并解压。

## 使用方法
本工具有多种使用方式：可以通过网页 demo 进行交互式翻译，或者指定输入文件批量翻译，还可以作为 Python API 供其他程序调用。

### 1. 交互式
交互式网页 demo 基于 flask 实现。运行 rule/app.py，并访问 localhost:5000，即可进行交互式翻译。

网页截图：

![image](https://user-images.githubusercontent.com/56507857/119098351-4f8d3d00-ba48-11eb-85c3-93249b26499e.png)

在文本框中输入需要翻译的英文地名，点击翻译按钮，可得到多个翻译候选，以及对应的原因：

![image](https://user-images.githubusercontent.com/56507857/119098696-ab57c600-ba48-11eb-89b2-425daceca426.png)

例如此例中，“斯诺希尔” 是按照国标直接音译；“female: snow -> 丝诺” 表示国标规则中， Snow 若作为女性人名，需要翻译成 “丝诺”；“generic: hill -> 山” 表示国标规则中， Hill 若作为通名，需要翻译成“山”。（国标参考翻译：斯诺希尔）

### 2. 批量翻译
批量翻译时，先将需要翻译的地名写在文本文件中（一行一个地名），然后在本项目的根目录中输入以下命令：
```$ python3 rules/main.py [input file]```
其中 `[input file]` 是输入文件名。程序就会输出所有翻译。

### 2. 作为 API
若要在其他 Python 程序中导入此工具，首先需要安装 pytorch 和 docopt 库，并下载此项目。下载安装完成后，在目标 python 文件中导入：
```
from GeoTranslate.rule.model import GeoTranslator
from GeoTranslate.rule.tables import initTables
```
然后使用以下语句新建一个 translator 类并初始化：
```
tableData = initTables()
translator = GeoTranslator(tableData)
```
这样就可以使用 `translator.run(inputNames)` 进行翻译，其中 `inputNames` 是需要翻译的英文的列表。

## 项目结构
1. rule：规则部分。主要由 4 份规则表以及对应的 splitors 组成，代码见 rule/tables.py 和 rule/splitors.py。得到地理名词后，按照通名-专名、可翻译单元、音节、音标的次序依次拆分，并由 result.py 中的 result 类存储，最后输出多个翻译候选，以及对应的规则。
2. neural-ipa: 神经网络部分。主要由一个英文单词到国际音标的 Bi-LSTM 网络组成，用来处理 eng-to-ipa 包中未登录的单词。neural-ipa/model.bin 是训练好的模型，基于 13 万条美音数据训练，在测试集上的 BLEU 达到 80 以上。数据集来自 [ipa-dict](https://github.com/open-dict-data/ipa-dict) 项目。
