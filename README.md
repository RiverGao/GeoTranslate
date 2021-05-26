# GeoTranslate：基于规则的英-中地理名词翻译系统
## 简介
本项目主要解决英文地理名词的规范化翻译问题，根据国家标准《外语地名汉字译写导则 英语》（GB/T 17693.1-2008）规定的音译、意译规则实现。

## 依赖库
本工具的主要依赖库包括：[pytorch](https://pytorch.org/), [eng-to-ipa](https://github.com/mphilli/English-to-IPA), docopt。
依赖库的安装过程如下:

``` python
### 安装pytorch
pip download torch==1.7.1+cu101 -f https://download.pytorch.org/whl/torch_stable.html
### 安装eng-to-ipa
git clone https://github.com/mphilli/English-to-IPA
cd English-to-IPA
python -m pip install .
### 安装docopt
pip install docopt
```

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
```
$ python3 rules/main.py [input file]
```
其中 `[input file]` 是输入文件名。程序就会输出所有翻译。 若未指定输入文件，程序会默认读取自带的 `examples.txt`，输出如下（部分）：

![image](https://user-images.githubusercontent.com/56507857/119115779-207fc700-ba5a-11eb-8623-1ae8b6021db0.png)

### 3. 作为 API
若要在其他 Python 程序中导入此工具，首先需要安装 pytorch 和 docopt 库，并下载此项目。下载安装完成后，在 GeoTranslate 目录下执行：
```
from rule.model import GeoTranslator
from rule.tables import initTables
```
然后使用以下语句新建一个 translator 类并初始化：
```
tableData = initTables()
translator = GeoTranslator(tableData)
```
这样就可以使用 `translator.run(inputNames)` 进行翻译，其中 `inputNames` 是需要翻译的英文的列表。运行结果示例如下：

![image](https://user-images.githubusercontent.com/56507857/119263390-75b20900-bc11-11eb-9638-1416a03ecaf6.png)

## 项目结构
### 规则部分
规则部分的代码和资源文件存放在 rule 目录下，主要由 4 份规则表以及对应的 splitors 组成。得到地理名词后，按照通名-专名、可翻译单元、音节、音标的次序依次拆分，并由 result.py 中的 result 类存储，最后输出多个翻译候选，以及对应的规则。主要代码包括：

1. `main.py`: 项目入口文件，用于批量翻译和程序调试等；

1. `app.py`: 交互式网页 demo 的执行文件；

1. `model.py`: 定义 `GeoTranslator` 类，初始化过程包括加载各规则表格，以及初始化拆分器；之后还定义了 4 个阶段的 `split` 方法，以及主要接口 `run` 方法。

1. `splitors.py`: 定义拆分器类 `Splitor`，以及它的子类，包括：专名-通名拆分器 `nameSplitor`，翻译单元拆分器 `unitSplitor`，音节拆分器 `syllableSplitor`，音标拆分器 `phoneticSplitor`。每个拆分器通过自身的 `split` 方法进行对应阶段的处理，同时定义了一些辅助的方法等。用于处理未登录词的神经网络在 `syllableSplitor` 的初始化方法中加载，并由其调用。

1. `results.py`: 定义 `Result` 类。处理流程中，输入地名会存储在一个 `Result` 对象中，并在每个拆分阶段记录拆分动作和原因。流程结束后，通过 `merge` 方法拼接各部分翻译结果，并产生格式化输出。

1. `tables.py`: 定义了规则表格 `Table` 类以及一个初始化接口 `initTables`。`Table` 对象实际上是对 `python` 字典对象的封装，包括数据以及查询方法。

1. `data.py`: 定义了数据加载和打印的工具函数。

1. `config.py`: 存放全局设置变量。

### 神经网络部分
神经网络部分的代码、模型和数据存放在 neural_ipa 目录下，主要由一个英文单词到国际音标的 Bi-LSTM 网络组成，用来处理 eng-to-ipa 包中未登录的单词。代码基于 pytorch 框架，由斯坦福大学 CS224N 课程作业改编，数据集来自 [ipa-dict](https://github.com/open-dict-data/ipa-dict) 项目。这部分的主要内容包括：

1. `word_ipa_data`: 此目录存放了训练数据。原始数据是 `en_US.csv`，包含 130k+ 条美音数据。经过 `datasets.py` 预处理后得到一系列文件，命名格式为 `[train/test/dev].[word/ipa]`，分别表示训练、测试、验证集的单词和音标。带有 `toy_` 前缀的是只包含 8 个样例的小数据集，用于检查相关程序是否正常。

2. `model.bin`: 训练好的模型，在测试集上的 BLEU 达到 80 以上。翻译系统需要依赖它运行。

3. `nmt_model.py`: 定义了 Bi-LSTM 网络模型，以及前向、后向过程。

4. `model_embeddings.py`: 定义了模型的词嵌入模块。

5. `vocab.py`: 定义了 seq2seq 的源端（英文字母）和目标端（国际音标符号）词表类，并可以生成相应的 json 文件。

6. `utils.py`: 定义了训练过程中的一些辅助函数。

7. `run.py`: 训练和测试的入口程序，由 `run.sh` 调用。

8. `run.sh`: 控制模型训练、测试、生成词表的脚本。

测试中 `model.bin` 已经可以满足翻译需求。如果需要自行训练模型，可以通过命令行执行 `run.sh`，用法如下：

```
$ bash run.py [option]

options:
--train
--test
--vocab
--toy-train
--toy-test
--toy-vocab
```

**在训练之前，需要先选择 `--vocab` 选项生成词表。** 此后，选择 `--train` 或 `--test` 可以执行 `run.py` 并进行训练或测试。带有 `toy-` 前缀的选项会使用之前提到的小数据集执行操作。由于训练时间较长，建议先使用此选项观察结果是否正常，无误后再开始训练。

如需更改超参数，可参阅 `run.py` 的注释：

```
"""
Usage:
    run.py train --train-src=<file> --train-tgt=<file> --dev-src=<file> --dev-tgt=<file> --vocab=<file> [options]
    run.py decode [options] MODEL_PATH TEST_SOURCE_FILE OUTPUT_FILE
    run.py decode [options] MODEL_PATH TEST_SOURCE_FILE TEST_TARGET_FILE OUTPUT_FILE

Options:
    -h --help                               show this screen.
    --cuda                                  use GPU
    --train-src=<file>                      train source file
    --train-tgt=<file>                      train target file
    --dev-src=<file>                        dev source file
    --dev-tgt=<file>                        dev target file
    --vocab=<file>                          vocab file
    --seed=<int>                            seed [default: 0]
    --batch-size=<int>                      batch size [default: 64]
    --embed-size=<int>                      embedding size [default: 256]
    --hidden-size=<int>                     hidden size [default: 256]
    --clip-grad=<float>                     gradient clipping [default: 5.0]
    --log-every=<int>                       log every [default: 10]
    --max-epoch=<int>                       max epoch [default: 30]
    --input-feed                            use input feeding
    --patience=<int>                        wait for how many iterations to decay learning rate [default: 5]
    --max-num-trial=<int>                   terminate training after how many trials [default: 5]
    --lr-decay=<float>                      learning rate decay [default: 0.5]
    --beam-size=<int>                       beam size [default: 5]
    --sample-size=<int>                     sample size [default: 5]
    --lr=<float>                            learning rate [default: 0.001]
    --uniform-init=<float>                  uniformly initialize all parameters [default: 0.1]
    --save-to=<file>                        model save path [default: model.bin]
    --valid-niter=<int>                     perform validation after how many iterations [default: 1000]
    --dropout=<float>                       dropout [default: 0.3]
    --max-decoding-time-step=<int>          maximum number of decoding time steps [default: 70]
"""
```

该文档采用 `docopt` 库规范编写，规定了各项超参数以及默认取值。根据您的需要，可以直接在注释中指定默认取值，或在 `run.sh` 的命令中添加相关选项。

此外，若要交互式调用此神经网络，可以在初始化 `GeoTranslator` 类后，调用其 `syllableSplitor.nmt_model` 的 `beam_search` 函数，例如：

![image](https://user-images.githubusercontent.com/56507857/119627606-ec801980-be3e-11eb-9ec8-06375859b9eb.png)

其中第 6 行是将输入单词转化成字符列表。模型会输出 5 个候选，并给出相应的得分。
