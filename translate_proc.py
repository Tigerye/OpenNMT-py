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


sp_pattern = r"<@sp\d{1,3}@>"
pattern = r'\d+|[零一二三四五六七八九十百千万亿兆]+'


class PrePostProc(object):

    def __init__(self):
        self._key2val = dict()
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


    def replace_num(input_string):
        unk1 = " <@nu"
        unk2 = "@> "
        unk_map = {}
        input_string, retmap = replace_sp(input_string)
        match_list = re.findall(pattern, input_string)
        input_list = list(input_string)
        seen = set()
        for target in match_list:
            num_target = isChinese(target)
            index = re.search(target, input_string).span()
            num = random.sample(range(200), 1)[0]
            if len(seen) == 199:
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
                else :
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

if __name__ == '__main__':
    input = '金逸影视营收额为100亿元，截止2018年1月31号'
    p = PrePostProc()
    a= {
        '北京':'beijing',
        '金逸':'jinyi'
        }
    p.set_data(a)
    tk = list(jieba.cut(input))
    out_tk, rep=p.pre_proc_zh_py(tk)
    out_str = ' '.join(out_tk)
    print(out_str)
    tmp_cut_str, rep2val_nu = p.pre_proc_zh_nu(out_str)

    print(tmp_cut_str)
    print(rep2val_nu)

    print(out_tk)
    print(rep)
