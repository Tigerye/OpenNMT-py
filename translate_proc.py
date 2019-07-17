# coding = utf-8

# @time    : 2019/7/1 12:40 PM
# @author  : alchemistlee
# @fileName: translate_proc.py
# @abstract:
import string
from sliding_utils import *
import random
import re
import jieba
import cn2an
from new_trans_preproc import *
import spacy

nlp = spacy.load('en_core_web_sm')
sp_pattern = r"<@sp\d{1,3}@>"
pattern = r'\d+|[零一二三四五六七八九十百千万亿兆]+'
unit_map = {"元":"yuan", "美元":"dollars", "千克":"kg", "公里":"km", "米":"meters", "厘米":"cm","吨":"tons", "克":"grams", "小时":"hours", "分钟":"minutes", \
                        "秒":"seconds", "磅":"pounds","盎司":"ounces", "加仑":"gallon","夸脱":"quarts", "品脱":"pints","升":"liter","美分":"cents","英里":"miles", "%":"%", \
                        "英尺":"feet", "英尺":"inch", "码":"yard", "毫升":"ml", "平方英寸":"square inch", "平方英尺":"square feet", "英亩":"acre", "英里每小时":"mile per hour", "km / h":"km / h"}

class PrePostProc(object):

    def __init__(self):
        self._key2val = dict()
        self._val2key = dict()
        self._py_tpl = '<@sp%s@>'
        self._nu_tpl = '<@nu%s@>'

    def load_data(self, path):
        for line in open(path):
            line = line.strip()
            items = line.split('\t')
            if len(items) !=2 :
                print('wrong line , {}'.format(line))
                continue
            k = items[0]
            v = items[1]
            self._key2val[k] = v
            self._val2key[v] = k
        print('finish it ~ ')

    def _rep_in_lst(self, input_lst, rep_beg, rep_end, rep_val):
        input_lst[rep_beg] = rep_val
        for i in range(rep_beg + 1, rep_end + 1):
            input_lst[i] = ''
        return input_lst


    def randomString(stringLength=10):
        """Generate a random string of fixed length """
        letters = string.ascii_lowercase
        return ''.join(random.choice(letters) for i in range(stringLength))

    def isChinese(word):
        for ch in word:
            if '\u4e00' <= ch <= '\u9fff':
                try:
                    return cn2an.cn2an(word)
                except:
                    return  word
        return word

    def replace_sp(input_string):
        sp_list = re.findall(sp_pattern, input_string)
        sp_list = set(sp_list)
        ret_map = {}
        unique_keys = set()
        for sp in sp_list:
            key = randomString(12)
            while key in unique_keys:
                key = randomString(12)
            unique_keys.add(key)
            ret_map[key] = sp
            input_string = re.sub(sp, key, input_string)
        return input_string, ret_map


    def recover_sp(input_string, ret_map):
        for rad in ret_map.keys():
            input_string = re.sub(rad, ret_map[rad], input_string)
        return input_string

    def replace_unk(self, input_string):
        """
        replace all unk symbols in the input string with long random strings
        """
        sp_list = re.findall(unk_pattern, input_string)
        sp_list = set(sp_list)
        ret_map = {}
        unique_keys = set()
        for sp in sp_list:
            key = randomString(12)
            while key in unique_keys:
                key = randomString(12)
            unique_keys.add(key)
            ret_map[key] = sp
            input_string = re.sub(sp, key, input_string)
        return input_string, ret_map

    def recover_unk(self, input_string, ret_map):
        """
        recover all unk symbols from random strings according to the map from random string to unk
        """
        for rad in ret_map.keys():
            input_string = re.sub(rad, ret_map[rad], input_string)
        return input_string

    def find_all(self, strin, target):
        return [i for i in range(len(strin)) if strin.startswith(target, i)]

    def loc_unit_quantity(self, input_string, unit):
        start_idx = self.find_all(input_string, unit)
        ret = []
        for index in start_idx:
            flag = False
            curr = index - 1
            while curr >= 0:
                if input_string[curr].isdigit() or input_string[curr] == '.':
                    flag = True
                    curr -= 1
                elif input_string[curr] == ' ':
                    if flag:
                        ret.append([curr + 1, index + len(unit)])
                        break
                    else:
                        curr -= 1
                elif not input_string[curr].isdigit():
                    if flag:
                        ret.append([curr + 1, index + len(unit)])
                        break
                    else:
                        break
        return ret

    def replace_unit_zh(self, zh_input):
        zh_input, zh_retmap = self.replace_unk(zh_input)
        ret_map = {}
        seen = set()
        zh_input, preproc_map = num_preproc_zh(zh_input, map_flag = True)
        unk_map = {}
        pattern = r'\d+'
        pattern2 = r'[\d.]+'
        zh_match_list = re.findall(pattern, zh_input)
        zh_input_list = list(zh_input)
        for key in unit_map.keys():
            if key in zh_input:
                zh_quantity_list = self.loc_unit_quantity(zh_input, key)
                for zh_index in zh_quantity_list:
                    if len(seen) == 30:
                        print("more than 30 nu symbols in sentence: {}".format(zh_input))
                        return None, None
                    num, seen = generate_random(seen, 30)
                    unk = " <@nu" + str(num) + "@> "
                    zh_q = zh_input[zh_index[0]: zh_index[1]]
                    zh_n = re.findall(pattern2, zh_q)[0]
                    if zh_n in preproc_map.keys():
                        original = preproc_map[zh_n]
                        ret_map[unk] = re.sub(zh_n, original, "".join(zh_input_list[zh_index[0]:zh_index[1]]))
                    else:
                        ret_map[unk] = "".join(zh_input_list[zh_index[0]:zh_index[1]])
                    zh_input_list = zh_input_list[:zh_index[0]] + [unk] + \
                                    [''] * ((zh_index[1] - zh_index[0]) - 1) + zh_input_list[zh_index[1]:]
        zh_input = "".join(zh_input_list)
        zh_input = self.recover_unk(zh_input, zh_retmap)
        return zh_input, ret_map, seen

    def replace_unit_en(self, en_input):
        en_input, en_retmap = self.replace_unk(en_input)
        ret_map = {}
        seen = set()
        en_input, preproc_map = num_preproc_en(en_input, map_flag = True)
        unk_map = {}
        pattern = r'\d+'
        pattern2 = r'[\d.]+'
        en_match_list = re.findall(pattern, en_input)
        en_input_list = list(en_input)
        for val in unit_map.values():
            if val in en_input:
                en_quantity_list = self.loc_unit_quantity(en_input, val)
                for en_index in en_quantity_list:
                    if len(seen) == 30:
                        print("more than 30 nu symbols in sentence: {}".format(zh_input))
                        return None, None
                    en_q = en_input[en_index[0]: en_index[1]]
                    en_n = re.findall(pattern2, en_q)[0]
                    num, seen = generate_random(seen, 30)
                    unk = " <@nu" + str(num) + "@> "
                    if en_n in preproc_map.keys():
                        original = preproc_map[en_n]
                        ret_map[unk] = re.sub(en_n, original, "".join(en_input_list[en_index[0]:en_index[1]]))
                    else:
                        ret_map[unk] = "".join(en_input_list[en_index[0]:en_index[1]])
                    en_input_list = en_input_list[:en_index[0]] + [unk] + \
                                        [''] * ((en_index[1] - en_index[0]) - 1) + en_input_list[en_index[1]:]
        en_input = "".join(en_input_list)
        en_input = self.recover_unk(en_input, en_retmap)
        return en_input, ret_map, seen

    def replace_num_zh(self, zh_input, seen, ret_map):
        zh_input, zh_retmap = self.replace_unk(zh_input)
        pattern = r'\d+|[零一二三四五六七八九十百千万亿兆]+'
        zh_match_list = re.findall(pattern, zh_input)
        zh_input_list = list(zh_input)
        for target in zh_match_list:
            if len(seen) == 30:
                print("more than 30 nu symbols in sentence: {}".format(zh_input))
                return None, None
            zh_index = re.search(target, zh_input)
            if zh_index:
                zh_index = zh_index.span()
            else:
                continue
            num, seen = generate_random(seen, 30)
            unk = " <@nu" + str(num) + "@> "
            ret_map[unk] = "".join(zh_input_list[zh_index[0]:zh_index[1]])
            zh_input_list = zh_input_list[:zh_index[0]] + [unk] + \
                            [''] * (len(target) - 1) + zh_input_list[zh_index[1]:]
            zh_input = zh_input[:zh_index[0]] + " " * len(target) + \
                       zh_input[zh_index[1]:]
        zh_input = "".join(zh_input_list)
        zh_input = self.recover_unk(zh_input, zh_retmap)
        return zh_input, ret_map

    def replace_num_en(self, en_input, seen, ret_map):
        pattern = r'\d+|[零一二三四五六七八九十百千万亿兆]+'
        en_input, en_retmap = self.replace_unk(en_input)
        en_match_list = re.findall(pattern, en_input)
        en_input_list = list(en_input)
        for num_target in en_match_list:
            if len(seen) == 30:
                print("more than 30 nu symbols in sentence: {}".format(en_input))
                return None, None
            en_index = re.search(num_target, en_input)
            if en_index:
                en_index = en_index.span()
            else:
                continue
            num, seen = generate_random(seen, 30)
            unk = " <@nu" + str(num) + "@> "
            ret_map[unk] = "".join(en_input_list[en_index[0]:en_index[1]])
            en_input_list = en_input_list[:en_index[0]] + [unk] + \
                            [''] * (len(num_target) - 1) + en_input_list[en_index[1]:]
            en_input = en_input[:en_index[0]] + " " * len(num_target) + \
                       en_input[en_index[1]:]
        en_input = "".join(en_input_list)
        en_input = self.recover_unk(en_input, en_retmap)
        return en_input, ret_map

    def pre_proc_zh_nu(self, input_str):
        zh_input, ret_map, seen = self.replace_unit_zh(input_str)
        if zh_input is None and ret_map is None:
            return zh_input, ret_map
        zh_input, ret_map = self.replace_num_zh(zh_input, seen, ret_map)
        return zh_input, ret_map

    def pre_proc_en_nu(self, input_str):
        en_input, ret_map, seen = self.replace_unit_en(input_str)
        if en_input is None and ret_map is None:
            return en_input, ret_map
        en_input, ret_map = self.replace_num_en(en_input, seen, ret_map)
        return en_input, ret_map


    def replace_num(input_string):
        unk1 = " <@nu"
        unk2 = "@> "
        unk_map = {}
        input_string, retmap = replace_sp(input_string)
        match_list = re.findall(pattern, input_string)
        input_list = list(input_string)
        seen = set()
        search_num_zh = {}
        pattern = r'\d+|<@sp\d{1,3}@>|[零一二三四五六七八九十百千万亿兆]+|<@nu.*@>]'
        arow_zh = re.findall(pattern, orow_zh)
        unks_zh = [a for a in arow_zh if a[:4] == "<@sp"]
        row_zh = [a for a in arow_zh if a[:4] != "<@sp" and a[:4] != "<@nu"]
        ret_map = {}
        if len(row_zh) >= 180:
            return None
        zh_list = list(orow_zh)
        for i in range(len(row_zh)):
            if self.isChinese(row_zh[i]):
                try:
                    num_zh = cn2an.cn2an(row_zh[i])
                    num_zh = str(num_zh)
                except:
                    continue
            if row_zh[i] not in search_num_zh.keys():
                search_num_zh[row_zh[i]] = 0
            num = random.sample(range(30), 1)[0]
            if len(seen) == 29:
                print("again")
                break
            while num in seen:
                num = random.sample(range(30), 1)[0]
            seen.add(num)
            unk = unk1 + str(num) + unk2
            input_list = input_list[:index[0]] + [unk] + [''] * (len(target) - 1) + input_list[index[1]:]
            input_string = input_string[:index[0]] + " " * len(target) + input_string[index[1]:]
            unk_map[unk] = num_target
        input_string = "".join(input_list)
        input_string = recover_sp(input_string, retmap)
        return input_string, unk_map


    def pre_proc_zh_nu(self,  input_str):
        # num_res = re.findall(r'\d+|<@sp\d{1,3}@>|[零一二三四五六七八九十百千万亿兆]+|<@nu.*@>]',)
        # for item in num_res:
        input_str,rep_map = self.replace_num(input_str)
        return input_str, rep_map

    def spacy_ner(self, sentence):

        doc = nlp(sentence)
        ret = []
        for ent in doc.ents:
            ret.append((ent.text, ent.start_char, ent.end_char, ent.label_))
        return ret

    def name_tag_list(self, zh_input):
        zh_input_ner = self.spacy_ner(zh_input)
        ret = []
        for item in zh_input_ner:
            if item[3] == 'PERSON' or item[3] == 'ORG':
                ret.append(item[0])
        return ret

    def pre_proc_en_py(self, input_token):
        matched = list()
        rep2val = dict()
        name_list = self.name_tag_list(" ".join(input_token))

        for sub_window_size in range(1, 9):
            tmp_sliding = sliding_it(input_token, sub_window_size)
            for item in tmp_sliding:
                k1 = item[0]
                if k1 in self._val2key.keys():
                    new_item = (item[0], item[1], item[2], k1)
                    matched.append(new_item)
                else:
                    for name in name_list:
                        name1 = "".join(name.split(" "))
                        if name == k1 or name1 == k1:
                            new_item = (item[0], item[1], item[2], k1)
                            matched.append(new_item)

        no_dup = filter_overlap(matched)

        for item in no_dup:

            rand_cnt = 0
            replaced_str = None
            while rand_cnt < 10:

                tmp_seed = random.randint(0,29)
                tmp_rep = self._py_tpl % tmp_seed

                if tmp_rep in rep2val.keys():
                    rand_cnt +=1
                    continue
                else:
                    if item[3] in self._val2key.keys():
                        rep2val[tmp_rep] = self._val2key[item[3]]
                    else:
                        rep2val[tmp_rep] = item[3]
                    replaced_str = tmp_rep
                    break
            input_token = self._rep_in_lst(input_token, item[1], item[2], replaced_str)

        res_token = list()
        for i in range(len(input_token)):
            tmp = input_token[i]
            if tmp == '':
                continue
            else:
                res_token.append(tmp)

        return res_token, rep2val


    def pre_proc_zh_py(self, input_token):
        # input_token = list(jieba.cut(input_str))
        # print('input = {}'.format(input_token))
        matched = list()
        rep2val = dict()

        for sub_window_size in range(1, 9):
            tmp_sliding = sliding_it(input_token, sub_window_size)
            for item in tmp_sliding:
                k1 = item[0]
                if k1 in self._key2val.keys():
                    new_item = (item[0], item[1], item[2], k1)
                    matched.append(new_item)

        no_dup = filter_overlap(matched)

        for item in no_dup:

            rand_cnt = 0
            replaced_str = None
            while rand_cnt < 10:

                tmp_seed = random.randint(0,29)
                tmp_rep = self._py_tpl % tmp_seed

                if tmp_rep in rep2val.keys():
                    rand_cnt +=1
                    continue
                else:
                    rep2val[tmp_rep] = self._key2val[item[3]]
                    replaced_str = tmp_rep
                    break

            # tmp_id = self._pre_key2id[item[3]]
            # tmp_val = self._vals[tmp_id]
            # replaced_str = tmp_val
            input_token = self._rep_in_lst(input_token, item[1], item[2], replaced_str)

        res_token = list()
        for i in range(len(input_token)):
            tmp = input_token[i]
            if tmp == '':
                continue
            else:
                res_token.append(tmp)

        return res_token, rep2val

    def proc_bpe(self,input_str):
        input_str = re.sub(r'(@@ )|(@@ ?$)','',input_str)
        return input_str

    def post_proc(self, input_str, rep2val_map):
        for k in rep2val_map.keys() :
            tmp_val = rep2val_map[k]
            input_str = input_str.replace(k,str(tmp_val))
        return input_str

    def set_data(self,d):
        self._key2val =d
        for key,val in d.items():
            self._val2key[val] = key

if __name__ == '__main__':
    input1 = '金逸影视营收额为100,000亿元，截止2018年1月31号'
    tk = list(jieba.cut(input1))
    input = 'Google makes 10 billion dollars every year, until 01/31/2018, and my name is Sicheng Tang'
    p = PrePostProc()
    a= {
        '北京':'beijing',
        '金逸':'jinyi'
        }
    p.set_data(a)

    s, m = p.pre_proc_en_py(input.split(" "))
    print(s)
    print(m)
    """
    out_tk, rep=p.pre_proc_zh_py(tk)
    out_str = ' '.join(out_tk)
    print(out_str)
    tmp_cut_str, rep2val_nu = p.pre_proc_zh_nu(out_str)

    print(tmp_cut_str)
    print(rep2val_nu)

    print(out_tk)
    print(rep)

    input = 'jinyi cinema makes 10 billion dollars every year, until 01/31/2018'
    input1 = '金逸影视营收额为100亿元，截止2018年1月31号'
    s,m = num_preproc_en(input, True)
    a,b = num_preproc_zh(input1, True)
    print(s)
    print(m)
    print(a)
    print(b)
    """
