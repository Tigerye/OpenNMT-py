import string
import json
from collections import defaultdict
import re
import random
import cn2an
import pymysql as ps
import pypinyin
import spacy
from spacy import displacy
from collections import Counter
#import en_core_web_sm
import requests
import sys


unk_pattern = r"<@sp\d{1,3}@>|<@nu\d{1,3}@>"

#pattern2 = r'[zero |one |two ]+'
#re.findall(pattern2, "twoone and onetwo")

ent_address = "rm-uf67jlfy9n338fqa5.mysql.rds.aliyuncs.com"
ent_database = "rt"
ent_username = "rt"
ent_password = "jUOcnRR6ZoZ5"


def replace_symbol(input_string):
    """
    '@-@' -> '-'
    """
    return re.sub("@-@|@ - @", "-", input_string)


def remove_num_comma(input_string, mapp = None):
    pattern = r'\d[\d.，,]+\d'
    l = re.findall(pattern, input_string)
    for num in l:
        if ',' in num:
            tmp = re.sub(',', '', num)
            if mapp is not None:
                mapp[tmp] = num
            input_string = input_string.replace(num, tmp)
        elif '，' in num:
            print("，")
            tmp = re.sub('，', '', num)
            if mapp is not None:
                mapp[tmp] = num
            input_string = input_string.replace(num, tmp)
    if mapp is not None:
        return input_string, mapp
    return input_string


def is_number(x):
    if type(x) == str:
        x = x.replace(',', '')
    try:
        float(x)
    except:
        return False
    return True


def text2int_zh(input_string):
    pattern = r'[零一二三四五六七八九十百千万亿兆点]+'
    word_list = re.findall(pattern, input_string)
    for word in word_list:
        num = ch2arabic(word)
        if num:
            input_string = input_string.replace(word, num)
    return input_string


def text2int_en (textnum, numwords={}):
    units = [
        'zero', 'one', 'two', 'three', 'four', 'five', 'six', 'seven', 'eight',
        'nine', 'ten', 'eleven', 'twelve', 'thirteen', 'fourteen', 'fifteen',
        'sixteen', 'seventeen', 'eighteen', 'nineteen',
    ]
    tens = ['', '', 'twenty', 'thirty', 'forty', 'fifty', 'sixty', 'seventy', 'eighty', 'ninety']
    scales = ['hundred', 'thousand', 'million', 'billion', 'trillion']
    ordinal_words = {}
    ordinal_endings = []

    if not numwords:
        numwords['and'] = (1, 0)
        for idx, word in enumerate(units): numwords[word] = (1, idx)
        for idx, word in enumerate(tens): numwords[word] = (1, idx * 10)
        for idx, word in enumerate(scales): numwords[word] = (10 ** (idx * 3 or 2), 0)

    textnum = textnum.replace('-', ' ')

    current = result = 0
    curstring = ''
    onnumber = False
    lastunit = False
    lastscale = False

    def is_numword(x):
        if is_number(x):
            return True
        if word in numwords:
            return True
        return False

    def from_numword(x):
        if is_number(x):
            scale = 0
            increment = int(x.replace(',', ''))
            return scale, increment
        return numwords[x]

    for word in textnum.split():
        if word in ordinal_words:
            scale, increment = (1, ordinal_words[word])
            current = current * scale + increment
            if scale > 100:
                result += current
                current = 0
            onnumber = True
            lastunit = False
            lastscale = False
        else:
            for ending, replacement in ordinal_endings:
                if word.endswith(ending):
                    word = "%s%s" % (word[:-len(ending)], replacement)

            if (not is_numword(word)) or (word == 'and' and not lastscale):
                if onnumber:
                    # Flush the current number we are building
                    curstring += repr(result + current) + " "
                curstring += word + " "
                result = current = 0
                onnumber = False
                lastunit = False
                lastscale = False
            else:
                scale, increment = from_numword(word)
                onnumber = True

                if lastunit and (word not in scales):
                    # Assume this is part of a string of individual numbers to
                    # be flushed, such as a zipcode "one two three four five"
                    curstring += repr(result + current)
                    result = current = 0

                if scale > 1:
                    current = max(1, current)

                current = current * scale + increment
                if scale > 100:
                    result += current
                    current = 0

                lastscale = False
                lastunit = False
                if word in scales:
                    lastscale = True
                elif word in units:
                    lastunit = True

    if onnumber:
        curstring += repr(result + current)

    return curstring

def combine_num_en_inf(input_string, mapp = None):
    scales = ["hundred", "thousand", "million", "billion", "trillion", \
    "hundreds", "thousands", "millions", "billions", "trillions"]
    scale_map = {"hundred":100, "thousand":[0.1, "wanthousand"], "million":[100, "wanthousand"], \
    "billion":[10, "yibillion"], "trillion":1000000000000}
    input_list = input_string.split(" ")
    pattern = r'\d[\d.,]*\d|[0-9]'
    for i in range(1, len(input_list)):
        if input_list[i] in scales:
            if re.match(pattern, input_list[i-1]):
                scale = input_list[i]
                try:
                    num = float(input_list[i-1].replace(',',''))
                    if num == int(num):
                        num = int(num)
                except:
                    continue
                if scale[-1] == 's':
                    scale = scale[:-1]
                scale_num = scale_map[scale]
                try:
                    if scale == "billion" or scale == "million":
                        if float(scale_num[0] * num) == int(scale_num[0] * num):
                            res = str(int(scale_num[0] * num)) + scale_num[1]
                        else:
                            res = str(float(scale_num[0] * num)) + scale_num[1]
                    elif scale == "thousand":
                        if num >= 10:
                            if float(num / 10) == int(num/10):
                                res = str(int(num / 10)) + scale_num[1]
                            else:
                                res = str(float(num / 10)) + scale_num[1]
                        else:
                            if float(num) == int(num):
                                res = str(int(num)) + "qianthousand"
                            else:
                                res = str(float(num)) + "qianthousand"

                    else:
                        res = str(int(scale_num * num))
                except:
                    continue
                if mapp is not None:
                    mapp[res] = input_list[i-1] + " " + input_list[i]
                input_list[i] = res
                input_list[i-1] = ""
    if mapp is not None:
        return ' '.join(input_list), mapp
    return ' '.join(input_list)


def combine_num_en(input_string, mapp = None):
    scales = ["hundred", "thousand", "million", "billion", "trillion", \
    "hundreds", "thousands", "millions", "billions", "trillions"]
    scale_map = {"hundred":100, "thousand":1000, "million":1000000, \
    "billion":1000000000, "trillion":1000000000000}
    input_list = input_string.split(" ")
    pattern = r'\d[\d.,]*\d|[0-9] '
    for i in range(1, len(input_list)):
        if input_list[i] in scales:
            if re.match(pattern, input_list[i-1]):
                scale = input_list[i]
                try:
                    num = float(input_list[i-1].replace(',',''))
                except:
                    continue
                if scale[-1] == 's':
                    scale = scale[:-1]
                scale_num = scale_map[scale]
                try:
                    res = str(int(scale_num * num))
                except:
                    continue
                if mapp is not None:
                    mapp[res] = input_list[i-1] + " " + input_list[i]
                input_list[i] = res
                input_list[i-1] = ""
    if mapp is not None:
        return ' '.join(input_list), mapp
    return ' '.join(input_list)


def combine_num_zh(input_string, mapp = None):
    scales = ["万", "亿", "千", "百", "兆"]
    scale_map = {"百":100, "千":1000, "万":10000, "亿":100000000, "兆":1000000000000}
    input_list = input_string.split(" ")
    pattern0 = r'\d[\d.,]*\d|[0-9] '
    pattern = '\d[\d.]*\d[百|千|万|亿|兆]|[0-9][百|千|万|亿|兆]'
    pattern2 = r'\d[\d.,]*\d|[0-9]'
    input_list_gram = n_gram(input_list, 2)
    for input_space in input_list_gram:
        inputt = "".join(input_space.split(" "))
        if re.findall(pattern, inputt):
            s = re.findall(pattern, inputt)
            s = [inputt.index(s[0]), inputt.index(s[0]) + len(s[0])]
            quant = inputt[s[0]:s[1]]
            try:
                num = quant[:-1]
                scale = quant[-1]
                val = str(int(float(num) * scale_map[scale]))
                content = inputt[:s[0]] + val + inputt[s[1]:]
                if mapp is not None:
                    mapp[val] = inputt[s[0]:s[1]]
                input_string = re.sub(input_space, content, input_string)
            except:
                continue
    if mapp is not None:
        return input_string, mapp
    return input_string


def num_preproc_en(input_string, map_flag = False):
    if map_flag:
        ret_map = {}
        try:
            input_string, ret_map = remove_num_comma(input_string, ret_map)
        except:
            input_string = input_string
        try:
            input_string, ret_map = combine_num_en_inf(input_string, ret_map)
        except:
            input_string = input_string
        return input_string, ret_map
    try:
        input_string = remove_num_comma(input_string)
    except:
        input_string = input_string
    try:
        input_string = combine_num_en(input_string)
    except:
        input_string = input_string
    """
    try:
        input_string = text2int_en(input_string)
    except:
        input_string = input_string
    """
    return input_string


def num_preproc_zh(input_string, map_flag = False):
    if map_flag:
        ret_map = {}
        try:
            input_string, ret_map = remove_num_comma(input_string, ret_map)
        except:
            input_string = input_string
        try:
            input_string, ret_map = combine_num_zh(input_string, ret_map)
        except:
            input_string = input_string
        return input_string, ret_map
    try:
        input_string = remove_num_comma(input_string)
    except:
        input_string = input_string
    try:
        input_string = combine_num_zh(input_string)
    except:
        input_string = input_string
    """
    try:
        input_string = text2int_zh(input_string)
    except:
        input_string = input_string
    """
    return input_string


def NER_service(input_string):
    link = "http://114.80.118.167:5009/test?in=" + input_string
    response = requests.get(url = link)
    s = response.text
    s = json.loads(s)[0]
    return s


def generate_random(seen, r):
    """
    keep generating random numbers
    """
    if not seen:
        num = 0
    else:
        num = max(seen) + 1
    seen.add(num)
    return num, seen


def editDistance(str1, str2, m , n):
    if m==0:
        return n
    if n==0:
        return m
    if str1[m-1]==str2[n-1]:
        return editDistance(str1,str2,m-1,n-1)
    return 1 + min(editDistance(str1, str2, m, n-1),    # Insert
                   editDistance(str1, str2, m-1, n),    # Remove
                   editDistance(str1, str2, m-1, n-1)    # Replac
                   )


def randomString(stringLength=10):
    """Generate a random string of fixed length """
    letters = string.ascii_lowercase
    return ''.join(random.choice(letters) for i in range(stringLength))


def isChinese(word):
    """Determine if the input string is Chinese and ensures that
    its pinyin is not similar to irrelevant common English words"""
    if word not in set(["和","的","有","由","又","地","阿","按","啊","们","喝","友","那么","我们", "元"]):
        for ch in word:
            if '\u4e00' <= ch <= '\u9fff':
                return True
        return False
    return False


def n_gram(token_list, n, c = " "):
    """
    given a token list, return the n-gram version of it
    """
    ret = []
    for l in range(1, n+1):
        for i in range(len(token_list)):
            if i + l <= len(token_list):
                ret.append(c.join(token_list[i:i+l]))
    return ret


def ch2arabic(word):
    """Convert Legal Chinese Numbers to Arabic Numbers, eg: 一万两千三百二十九 => 12329"""
    for ch in word:
        if '\u4e00' <= ch <= '\u9fff':
            try:
                return str(cn2an.cn2an(word))
            except:
                return  None
    return word


class DataCleanser(object):

    def __init__(self, zh_file, en_file):
        """
        Inputs should be absolute path to both Chinese and English files,
        files have to be aligned line to line and the Chinese corpus has to be
        tokenized, i.e. whitespaces between tokens. The default choice for 中文分词 is jieba
        """
        self._key2val = dict()
        self._py_tpl = '<@sp%s@>'
        self._nu_tpl = '<@nu%s@>'
        self.entity_map = self.LoadEntityDict(ent_address, ent_database, ent_username, ent_password)
        self.zh_entity = self.entity_map.keys()
        self.en_entity = []
        for key, val in self.entity_map:
            self.en_entity += val
        self.zh_path = zh_file
        self.en_path = en_file
        self.pattern = r'\d+|[零一二三四五六七八九十百千万亿兆]+'
        self.unit_map = {"元":"yuan", "美元":"dollars", "千克":"kg", "公里":"km", "米":"meters", "厘米":"cm","吨":"tons", "克":"grams", "小时":"hours", "分钟":"minutes", \
                        "秒":"seconds", "磅":"pounds","盎司":"ounces", "加仑":"gallon","夸脱":"quarts", "品脱":"pints","升":"liter","美分":"cents","英里":"miles", "%":"%", \
                        "英尺":"feet", "英尺":"inch", "码":"yard", "毫升":"ml", "平方英寸":"square inch", "平方英尺":"square feet", "英亩":"acre", "英里每小时":"mile per hour", "km / h":"km / h"}

    def LoadEntityDict(self, address, database, username, password):
        """address:rm-uf67jlfy9n338fqa5.mysql.rds.aliyuncs.com
           database: rt
           username: rt
           password: jUOcnRR6ZoZ5
           key of the map is the Chinese name and val is a list of English names including alias if available
        """
        entity_map = defaultdict(lambda : [])
        db = ps.connect(address, username, password, database)
        cursor = db.cursor()
        command1 = "select ent_keys, ent_val, type from zh_en_ent"
        command2 = "select alias, cn_name, en_name, type from entity"
        command3 = "select ent_keys, ent_val, type from en_zh_ent"
        cursor.execute(command1)
        for row in cursor.fetchall():
            if row[2] == 1 or row[0] == row[1] or row[1] is None or row[0] is None:
                continue
            for key in row[0].split(';'):
                entity_map[key].append(row[1])
        cursor.execute(command2)
        for row in cursor.fetchall():
            if row[1] == row[2] or row[1] is None or row[3] == 1 or row[2] is None:
                continue
            entity_map[row[1]].append(row[2])
            if row[0] is not None:
                entity_map[row[1]] += row[0].split(';')
        cursor.execute(command3)
        for row in cursor.fetchall():
            if row[2] == 2 or row[0] == row[1] or row[1] is None or row[0] is None:
                continue
            entity_map[row[1]].append(row[0])
        for key in entity_map.keys():
            val = entity_map[key]
            val = list(set(val))
            val = sorted(val, key = lambda a : -len(a))
            entity_map[key] = val
        return entity_map

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

    def replace_pinyin(self, zh_input, en_input, line_count, seen):
        """
        replace English tokens that have the same form as pinyin from Chinese corpus with
        sp_unk ranging from 0 to 30 and '@-@' -> '-'
        return None if there are more than 30 pinyin matchings to indicate that this sample
        should be dropped.
        """
        zh_input, zh_retmap = self.replace_unk(zh_input)
        en_input, en_retmap = self.replace_unk(en_input)
        zhtoken2num = {}
        zh_input_list = zh_input.split(" ")
        en_input_list = en_input.split(" ")
        for i in range(len(zh_input_list)):
            if len(seen) == 30:
                print("wait to be changed into logging and the \
                information is more than 30 sp unks in line_count")
                return None, None
            num = None
            token = zh_input_list[i]
            if token in zhtoken2num.keys():
                zh_input_list[i] = zhtoken2num[token]
            target = pypinyin.pinyin(token, style=pypinyin.Style.NORMAL)
            ll = [a[0] for a in target]
            target = "".join(ll)
            for j in range(len(en_input_list)):
                token_en = en_input_list[j].lower()
                if isChinese(token):
                    if token_en == target:
                        if num == None:
                            num, seen = generate_random(seen, 30)
                            unk = " <@sp" + str(num) + "@> "
                            zhtoken2num[token] = unk
                        zh_input_list[i] = unk
                        en_input_list[j] = unk
                        continue
                    if j + 1 < len(en_input_list):
                        token_en1 = en_input_list[j].lower() + en_input_list[j + 1].lower()
                        if token_en1 == target:
                            if num == None:
                                num, seen = generate_random(seen, 30)
                                unk = " <@sp" + str(num) + "@> "
                                zhtoken2num[token] = unk
                            zh_input_list[i] = unk
                            en_input_list[j] = unk
                            en_input_list[j + 1] = ""
                            continue
                    if j + 2 < len(en_input_list):
                        token_en2 = en_input_list[j].lower() + en_input_list[j + 1].lower() \
                        + en_input_list[j + 2].lower()
                        if token_en2 == target:
                            if num == None:
                                num, seen = generate_random(seen, 30)
                                unk = " <@sp" + str(num) + "@> "
                                zhtoken2num[token] = unk
                            zh_input_list[i] = unk
                            en_input_list[j] = unk
                            en_input_list[j + 1] = ""
                            en_input_list[j + 2] = ""
                            continue
                else:
                    continue
        row_zh = " ".join(zh_input_list)
        row_en = " ".join(en_input_list)
        row_zh = self.recover_unk(row_zh, zh_retmap)
        row_en = self.recover_unk(row_en, en_retmap)
        return row_zh, row_en

    def replace_entity(self, zh_input, en_input, line_count):
        """
        replace entity with <@sp[0-29]@> and the 30 symbols with replace_pinyin,
        only replace when the corresponding entity is also found
        """
        zh_input = replace_symbol(zh_input)
        en_input = replace_symbol(en_input)
        zh_input, zh_retmap = self.replace_unk(zh_input)
        en_input, en_retmap = self.replace_unk(en_input)
        seen = set()
        zhtoken2num = {}
        zh_input_list = zh_input.split(" ")
        zh_input_list_gram = n_gram(zh_input_list, 4)
        for token_space in zh_input_list_gram:
            if len(seen) == 30:
                print("wait to be changed into logging and the \
                information is more than 30 sp unks in line_count")
                return None, None, set()
            token = "".join(token_space.split(" "))
            if token in zhtoken2num.keys():
                unk = zhtoken2num[token]
                zh_input = re.sub(token_space, unk, zh_input)
                continue
            if len(self.entity_map[token]) > 0:
                for alias in self.entity_map[token]:
                    if alias in en_input:
                        if token in zhtoken2num.keys():
                            unk = zhtoken2num[token]
                        else:
                            num, seen = generate_random(seen, 30)
                            unk = " <@sp" + str(num) + "@> "
                            zhtoken2num[token] = unk
                        en_input = re.sub(alias, unk, en_input)
                        zh_input = re.sub(token_space, unk, zh_input)
        zh_input = self.recover_unk(zh_input, zh_retmap)
        en_input = self.recover_unk(en_input, en_retmap)
        return zh_input, en_input, seen

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


    def replace_sp(self, input_string):
        #entity + pinyin
        input_string = replace_symbol(input_string)
        input_string, ret_map = self.replace_unk(input_string)
        seen = set()
        zhtoken2num = {}
        if isChinese(input_string):
            print("chinese")
            zh_input = input_string
            zh_input_list = zh_input.split(" ")
            zh_input_list_gram = n_gram(zh_input_list, 4)
            for token_space in zh_input_list_gram:
                if len(seen) == 30:
                    print("more than 30 sp unks")
                    return None, None
                if token in zhtoken2num.keys():
                    unk = zhtoken2num[token]
                    zh_input = re.sub(token_space, unk, zh_input)
                    continue
                if len(self.entity_map[token]) > 0:
                    for alias in self.entity_map[token]:
                        if token in zhtoken2num.keys():
                            unk = zhtoken2num[token]
                        else:
                            num, seen = generate_random(seen, 30)
                            unk = " <@sp" + str(num) + "@> "
                            zhtoken2num[token] = unk
                        zh_input = re.sub(token_space, unk, zh_input)
            zh_input = self.recover_unk(zh_input, ret_map)
            return zh_input
        else:
            print("english")



    def replace_nu(input_string):
        return

    def replace_units(self, zh_input, en_input, line_count):
        """
        replace nums w/ units with <@nu[0-29]@> and share the 30 symbols with replace_num,
        only replace when the corresponding entity is also found
        """
        zh_input, zh_retmap = self.replace_unk(zh_input)
        en_input, en_retmap = self.replace_unk(en_input)
        seen = set()
        zh_input = num_preproc_zh(zh_input)
        en_input = num_preproc_en(en_input)
        unk_map = {}
        pattern = r'\d+'
        pattern2 = r'[\d.]+'
        en_match_list = re.findall(pattern, en_input)
        zh_match_list = re.findall(pattern, zh_input)
        en_input_list = list(en_input)
        zh_input_list = list(zh_input)
        for key in self.unit_map.keys():
            if key in zh_input and self.unit_map[key] in en_input:
                zh_quantity_list = self.loc_unit_quantity(zh_input, key)
                en_quantity_list = self.loc_unit_quantity(en_input, self.unit_map[key])
                for zh_index in zh_quantity_list:
                    for en_index in en_quantity_list:
                        if len(seen) == 30:
                            print("too many units wait to be changed into logging and the \
                            information is more than 30 nu unks in line_count")
                            return None, None, seen
                        zh_q = zh_input[zh_index[0]: zh_index[1]]
                        en_q = en_input[en_index[0]: en_index[1]]
                        zh_n = re.findall(pattern2, zh_q)
                        en_n = re.findall(pattern2, en_q)
                        if zh_n == en_n:
                            num, seen = generate_random(seen, 30)
                            unk = " <@nu" + str(num) + "@> "
                            zh_input_list = zh_input_list[:zh_index[0]] + [unk] + \
                                            [''] * ((zh_index[1] - zh_index[0]) - 1) + zh_input_list[zh_index[1]:]
                            en_input_list = en_input_list[:en_index[0]] + [unk] + \
                                            [''] * ((en_index[1] - en_index[0]) - 1) + en_input_list[en_index[1]:]
        zh_input = "".join(zh_input_list)
        en_input = "".join(en_input_list)
        zh_input = self.recover_unk(zh_input, zh_retmap)
        en_input = self.recover_unk(en_input, en_retmap)
        return zh_input, en_input, seen

    def replace_num(self, zh_input, en_input, seen, line_count):
        """
        replace numbers according to RE
        """
        pattern = r'\d+|[零一二三四五六七八九十百千万亿兆]+'
        zh_input, zh_retmap = self.replace_unk(zh_input)
        en_input, en_retmap = self.replace_unk(en_input)
        unk_map = {}
        en_match_list = re.findall(self.pattern, en_input)
        zh_match_list = re.findall(self.pattern, zh_input)
        en_input_list = list(en_input)
        zh_input_list = list(zh_input)
        for target in zh_match_list:
            if len(seen) == 30:
                print("too many numbers wait to be changed into logging and the \
                information is more than 30 nu unks in line_count")
                return None, None
            num_target = ch2arabic(target)
            if not num_target:
                continue
            if num_target in en_match_list:
                en_index = re.search(num_target, en_input)
                if en_index:
                    en_index = en_index.span()
                else:
                    continue
                zh_index = re.search(target, zh_input)
                if zh_index:
                    zh_index = zh_index.span()
                else:
                    continue
                num, seen = generate_random(seen, 30)
                unk = " <@nu" + str(num) + "@> "
                en_input_list = en_input_list[:en_index[0]] + [unk] + \
                                [''] * (len(num_target) - 1) + en_input_list[en_index[1]:]
                zh_input_list = zh_input_list[:zh_index[0]] + [unk] + \
                                [''] * (len(target) - 1) + zh_input_list[zh_index[1]:]
                en_input = en_input[:en_index[0]] + " " * len(num_target) + \
                           en_input[en_index[1]:]
                zh_input = zh_input[:zh_index[0]] + " " * len(target) + \
                           zh_input[zh_index[1]:]
                unk_map[unk] = [target, num_target]
        zh_input = "".join(zh_input_list)
        en_input = "".join(en_input_list)
        zh_input = self.recover_unk(zh_input, zh_retmap)
        en_input = self.recover_unk(en_input, en_retmap)
        return zh_input, en_input

    def data_process(self, zh_input, en_input, line_count, pinyin = True, Entity = True, Number = True, Units = True):
        """
        The main function to process data.
        """
        seen = set()
        if Entity:
            zh_input, en_input, seen = self.replace_entity(zh_input, en_input, line_count)
            print("not entity")
            if zh_input == None and en_input == None:
                print("In line {}, detected more than 30 unks".format(line_count))
                return None, None
        if pinyin:
            zh_input, en_input = self.replace_pinyin(zh_input, en_input, line_count, seen)
            print("not pinyin")
            if zh_input == None and en_input == None:
                print("In line {}, detected more than 30 unks".format(line_count))
                return None, None
        if Units:
            zh_input, en_input, seen = self.replace_units(zh_input, en_input, line_count)
            print("not units")
            if zh_input == None and en_input == None:
                print("In line {}, detected more than 30 unks".format(line_count))
                return None, None
        if Number:
            zh_input, en_input = self.replace_num(zh_input, en_input, seen, line_count)
            print("not number")
            if zh_input == None and en_input == None:
                print("In line {}, detected more than 30 unks".format(line_count))
                return None, None
        return zh_input, en_input

    def data_cleanse(self, lower, higher):
        with open(self.en_path, "r") as file_en, open(self.zh_path, "r") as file_zh, \
             open(self.en_path + ".processed5." + str(lower) + '-' + str(higher), "w") as file_en_processed, \
             open(self.zh_path + ".processed5." + str(lower) + '-' + str(higher), "w") as file_zh_processed:
             line_count = 0
             for en_input, zh_input in zip(file_en, file_zh):
                 if line_count < lower:
                     line_count += 1
                     continue
                 try:
                     zh_input, en_input = self.data_process(zh_input, en_input, line_count)
                 except:
                     print("en_input: {}".format(en_input))
                     print("zh_input: {}".format(zh_input))
                     print("on line {}, we got an error".format(line_count))
                     file_en_processed.write(en_input)
                     file_zh_processed.write(zh_input)
                     line_count += 1
                     continue
                 if zh_input == None and en_input == None:
                     continue
                 file_en_processed.write(en_input)
                 file_zh_processed.write(zh_input)
                 line_count += 1
                 if line_count == higher:
                     break
                 if line_count % 1 == 0:
                     print(line_count)


if __name__ == '__main__':
    cleanser = DataCleanser("demo.zh", "demo.en")
    lower, higher = int(sys.argv[1]), int(sys.argv[2])
    #input_zh = "最 不 发达国家 在 相关 的 三大 市场 享有 重大 优惠 幅度 的 出口 包括 鲜鱼 或 冻鱼 ( 在 不同 市场 优惠 幅度 在 10% 到 20% 之间 ) ； 章鱼 ( 8% ) ； 腌 金枪鱼 ( 9% 到 24% ) ； 鲜切花 ( 4% 到 12% ) ； 香草 ( 6% ) ； 丁香 ( 8% ) ； 烟草 ( 31% ) ； 石油 制剂 ( 4% 到 6% ) ； 尿素 ( 7% ) ； 皮革 ( 3% 到 22% ) ； 黄 麻布 ( 4% 到 14% ) ； 毛毯 ( 8% 到 9.5% ) ； 服装 ( 6% 到 13% ) ； 亚麻布 ( 12% ) ； 黄麻 产品 ( 3% ) ； 鞋类 ( 7% 到 25% ) ； 帽子 ( 2% 到 6% ) ； 和 接线 组 ( 2% 到 5% ) "
    #input_en = "LDC exports enjoying significant preferential margins in the relevant three major markets include , inter alia , fresh or frozen fish ( margin of 10 % to 22 % , depending on the market ) ; octopus ( 8 % ) ; preserved tuna ( 9 % to 24 % ) ; fresh cut flowers ( 4 % to 12 % ) ; vanilla ( 6 % ) ; cloves ( 8 % ) ; tobacco ( 31 % ) ; petroleum preparations ( 4 % to 6 % ) ; urea ( 7 % ) ; leather ( 3 % to 22 % ) ; jute fabrics ( 4 % to 14 % ) ; wool carpets ( 8 % to 9.5 % ) ; garments ( 6 % to 13 % ) ; linen ( 12 % ) ; jute products ( 3 % ) ; footwear ( 7 % to 25 % ) ; hats ( 2 % to 6 % ) ; and wiring sets ( 2 % to 5 % ) ."
    #result_zh, result_en = cleanser.data_process(input_zh, input_en, 0)
    cleanser.data_cleanse(lower, higher)
