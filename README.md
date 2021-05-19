# GeoTranslate：基于规则的英-中地理名词翻译系统
## 简介
本项目主要解决英文地理名词的规范化翻译问题，根据国家标准《外语地名汉字译写导则 英语》（GB/T 17693.1-2008）规定的音译、意译规则实现。

## 依赖库
本工具的主要依赖库包括：pytorch, eng-to-ipa, docopt

## 使用方法
本工具有两种使用方式：一种是通过网页 demo 进行交互式翻译，另一种是作为 Python API 供其他程序调用。

### 1. 交互式
运行 rule/app.py，并访问 localhost:5000，即可进行交互式翻译。或者在 rules/data.py 中指定源端输入，运行 rule/main.py 进行批量翻译。

### 2. 作为 API
在其他 Python 程序中，导入 translator 类并初始化，即可使用相应的功能。

## 项目结构
1. rule：规则部分。主要由 4 份规则表以及对应的 splitors 组成，代码见 rule/tables.py 和 rule/splitors.py。得到地理名词后，按照通名-专名、可翻译单元、音节、音标的次序依次拆分，并由 result.py 中的 result 类存储，最后输出多个翻译候选，以及对应的规则。
2. neural-ipa: 神经网络部分。主要由一个英文单词到国际音标的 Bi-LSTM 网络组成，用来处理 eng-to-ipa 包中未登录的单词。
