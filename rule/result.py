import copy

class Result():
    def __init__(self):
        self.res = []
        self.genT = {}
        self.specT = {}
        self.femaleT = {}
    def saveGen(self, gen: str, genT: str):
        self.genT[gen] = genT
    def saveMainIdx(self, mainIndex):
        self.mainIndex = mainIndex
    def saveSpec(self, spec: str, specT: str):
        self.specT[spec] = specT
    def saveSpecFemale(self, spec: str, specT: str):
        self.femaleT[spec] = specT
    def saveStruct(self, struct: list):
        self.struct = struct
    def getRes(self) -> list:
        return self.res
    def combine(self, section: list, isInit: bool, isBack: bool, needGen: bool) -> list:
        def countChineseCharactors() -> int:
            count = 0
            for k in self.specT.keys():
                for ch in self.specT[k]:
                    count += 1
                    if ch == '/':
                        count -= 2
            return count
        #print(self.specT)
        #print(section)

        def multiRes(w_spec: list, is_init: bool, is_back: bool)->list:
            '''
            对每个单词内部的"/"进行解析，产生的结果作为返回值
            '''
            if is_init == True:
                if w_spec[0:3] == "弗/夫" or w_spec[0:3] == "东/栋" or \
                        w_spec[0:3] == "西/锡" or w_spec[0:3] == "南/楠":
                    init = w_spec[2]
                    w_spec = init + w_spec[3:]
            elif is_back == True:
                if w_spec[-3:] == "海/亥":
                    w_spec = w_spec[0:-3] + "亥"
            pairs = []
            rests = []
            res = ["", ]
            pos = 0
            for idx in range(0, len(w_spec)):
                if w_spec[idx] == '/':
                    pairs.append((w_spec[idx - 1], w_spec[idx + 1]))
                    if idx - 1 > pos:
                        rests += [w_spec[pos: idx - 1], ]
                    else:
                        rests.append("")
                    pos = idx + 2
            rests.append(w_spec[pos:])
            for pair_num in range(0, len(pairs)):
                for res_num in range(0, len(res)):
                    res[res_num] += rests[pair_num]
                temp = copy.deepcopy(res)
                for res_num in range(0, len(res)):
                    res[res_num] += pairs[pair_num][0]
                for temp_num in range(0, len(temp)):
                    temp[temp_num] += pairs[pair_num][1]
                res += temp
            for res_num in range(0, len(res)):
                res[res_num] += rests[len(pairs)]
            return res

        section_res = [["", ""], ]
        #print(section, section[0])
        if len(section) > 0 and section[0] == 'the':
            section = section[1:]
        for i in range(0, len(section)):
            word = section[i]
            if i + 1 < len(section) and section[i + 1] == "of":
                word += " of"
            if word == "of":
                continue
            w_spec = self.specT[word]
            #print("w_spec", w_spec)
            is_init = (i == 0 and isInit == True)
            is_back = (i == len(section) - 1 and isBack == True)
            w_spec = multiRes(w_spec, is_init, is_back)

            gen_res = []
            if needGen == True and word in self.genT:
                res = copy.deepcopy(section_res)
                for item in self.genT[word].split("/"):
                    temp_res = copy.deepcopy(res)
                    for seq in temp_res:
                        seq[0] += item
                        seq[1] += "generic: {} -> {} ".format(word, item)
                    gen_res += temp_res

            add_hyphen = False
            if countChineseCharactors() > 8 and i == 1 and \
                    section[i] != "with" and section[i] != "and" and \
                    needGen == False:
                add_hyphen = True
            #print(i, add_hyphen)
            spec_res = []
            res = copy.deepcopy(section_res)
            #print(w_spec)
            for item in w_spec:
                temp_res = copy.deepcopy(res)
                #print("item", item)
                for seq in temp_res:
                    if add_hyphen == True:
                        seq[0] = seq[0] + "-"
                    seq[0] += item
                    #print("seq", seq)
                spec_res += temp_res
            #print(spec_res, female_res, gen_res)

            female_res = []
            # print("femaleT", self.femaleT)
            if word in self.femaleT:
                w_female = self.femaleT[word]
                is_init = (i == 0 and isInit == True)
                is_back = (i == len(section) - 1 and isBack == True)
                w_female = multiRes(w_female, is_init, is_back)
                for item in w_female:
                    temp_res = copy.deepcopy(res)
                    for seq in temp_res:
                        if add_hyphen == True:
                            seq[0] = seq[0] + "-"
                        seq[0] += item
                        seq[1] += "female: {} -> {} ".format(word, item)
                    female_res += temp_res
            else:
                female_res = []

            section_res = spec_res + female_res + gen_res
        #print("section_res", section_res)
        return section_res

    def merge(self):
        self.res += self.combine(self.struct, True, True, False) #无通名翻译
        #print(self.res)
        if self.mainIndex > -1: # 有主要通名的翻译
            main_gen = self.struct[self.mainIndex]
            main_genT = self.genT[main_gen].split("/")
            for genT_item in main_genT:
                left = self.combine(self.struct[0:self.mainIndex], True, False, True)
                right = self.combine(self.struct[self.mainIndex+1:], False, True, True)
                for left_item in left:
                    for right_item in right:
                        name = left_item[0] + right_item[0] + genT_item
                        expression = left_item[1] + right_item[1] + "genric: {} -> {}".format(main_gen, genT_item)
                        self.res.append([name, expression])
        if self.mainIndex == -1: # 有通名，但通名是形容词的翻译
            self.res += self.combine(self.struct, True, True, True)