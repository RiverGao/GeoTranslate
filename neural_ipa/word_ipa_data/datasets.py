import pandas as pd
import numpy as np

raw = pd.read_csv('en_US.csv', sep='\t', names=['word', 'ipa'], dtype=str).dropna()

# 第一步消歧
b = pd.DataFrame(raw.ipa.str.split(',').tolist(), index=raw.word).stack()
b = b.reset_index()[[0, 'word']] # ipa variable is currently labeled 0
b.columns = ['ipa', 'word'] # renaming ipa

# 第二步预处理
# 去掉斜杠
c = b.ipa.str.strip().str.strip('/')
# 替换符号
# 先看一下ipa里面有哪些符号
symbs = set()
for ipa in c.iteritems():
    set_ipa = set(ipa[1])
    symbs = symbs | set_ipa
# 不一样的符号
transform = {'ɜ': 'ə',
             'ɝ': 'ər',
             'ɫ': 'l',
             'ɹ': 'r',
             'ɡ': 'g'}
# 替换
for k, v in transform.items():
    c = c.str.replace(k, v)
b.update(c)

# 加入空格
# b.update(c.apply(lambda x: ' '.join(list(x))))
# b.update(b.word.apply(lambda x: ' '.join(list(x))))
b = b.applymap(lambda x: ' '.join(list(x)))

# 第三步划分数据集: 80% train, 10% dev, 10% test
x = b.index.values
np.random.shuffle(x)
b.index = x
b = b.sort_index() # 这几步打乱顺序
N = len(b)
split = N // 10 # 10% 划分
test = b.iloc[: split, :]
dev = b.iloc[split: 2*split, :]
train = b.iloc[2*split:, :]

# 第三步输出
sets = [train, dev, test]
names = ['train', 'dev', 'test']
for s, name in zip(sets, names): 
    s.head(8).ipa.to_csv('toy_'+name+'.ipa', encoding='utf-8', index=False, header=None)
    s.head(8).word.to_csv('toy_'+name+'.word', encoding='utf-8', index=False, header=None)
    s.ipa.to_csv(name+'.ipa', encoding='utf-8', index=False, header=None)
    s.word.to_csv(name+'.word', encoding='utf-8', index=False, header=None)