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
        section_res = [["", ""], ]
        for i in range(0, len(section)):
            word = section[i]
            if i + 1 < len(section) and section[i + 1] == "of":
                word += " of"
            if word == "of":
                continue
            w_spec = self.specT[word]
            #print("w_spec", w_spec)
            if i == 0 and isInit == True:
                if w_spec[0:3] == "弗/夫" or w_spec[0:3] == "东/栋" or \
                        w_spec[0:3] == "西/锡" or w_spec[0:3] == "南/楠":
                    init = w_spec[2]
                    w_spec = init + w_spec[2:]
            elif i == len(section) - 1 and isBack == True:
                if w_spec[-3:] == "海/亥":
                    w_spec = w_spec[0:-3] + "亥"
            pairs = []
            rests = []
            res = ["", ]
            pos = 0
            for i in range(0, len(w_spec)):
                if w_spec[i] == '/':
                    pairs.append((w_spec[i - 1], w_spec[i + 1]))
                    if i - 1 > pos:
                        rests += w_spec[pos: i - 1]
                    else:
                        rests.append("")
                    pos = i + 2
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
            #print(res, rests, pairs)
            for res_num in range(0, len(res)):
                res[res_num] += rests[len(pairs)]
            w_spec = res
            #print("w_spec", w_spec)
            female_res = copy.deepcopy(section_res)
            #print("femaleT", self.femaleT)
            if word in self.femaleT:
                for item in female_res:
                    item[0] += self.femaleT[word]
                    item[1] += "female: {} -> {} ".format(word, self.femaleT[word])
            else:
                female_res = []
            gen_res = []
            if needGen == True and word in self.genT:
                res = copy.deepcopy(section_res)
                for item in self.genT[word].split("/"):
                    temp_res = copy.deepcopy(res)
                    for seq in temp_res:
                        seq[0] += item
                        seq[1] += "generic: {} -> {} ".format(word, item)
                    gen_res += temp_res
            spec_res = []
            res = copy.deepcopy(section_res)
            for item in w_spec:
                temp_res = copy.deepcopy(res)
                for seq in temp_res:
                    seq[0] += item
                spec_res += temp_res
            section_res = spec_res + female_res + gen_res
        #print("section_res", section_res)
        return section_res

    def merge(self):
        self.res += self.combine(self.struct, True, True, False)
        if self.mainIndex != -1:
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

'''
test = Result()
test.saveGen("0", "genT0 ")
test.saveGen("1", "genT1 ")
test.saveMainIdx(1)
test.saveSpec("0", "specT0 ")
test.saveSpec("1", "specT1 ")
test.saveSpec("2", "specT2 ")
test.saveSpecFemale("0", "femaleT0 ")
test.saveSpecFemale("2", "femaleT2 ")
test.saveStruct(["0", "1", "2"])
test.merge()
'''