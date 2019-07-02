# coding = utf-8

# @time    : 2019/7/1 12:40 PM
# @author  : alchemistlee
# @fileName: translate_proc.py
# @abstract:

from sliding_utils import *
import random
import re
import jieba
import cn2an

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

    def isChinese(self,word):
        for ch in word:
            if '\u4e00' <= ch <= '\u9fff':
                return True
        return False

    def replace_num(self,orow_zh):
        unk1 = " <@nu"
        unk2 = "@> "
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
            num = random.sample(range(200), 1)[0]
            if len(seen) == 199:
                print("again")
                break
            while num in seen:
                num = random.sample(range(200), 1)[0]
            seen.add(num)
            unkk = unk1 + str(num) + unk2
            try:
                inunk = False
                zh_index = re.search(row_zh[i], orow_zh).span()
                for unk in unks_zh:
                    unk_index = re.search(unk, orow_zh).span()
                    if zh_index[i] >= unk_index[0] and zh_index[i] <= unk_index[1]:
                        inunk = True
                        break
                    if inunk:
                        continue
                zh_list = zh_list[:zh_index[0]] + [unkk] + [''] * (len(row_zh[i]) - 1) + zh_list[zh_index[1]:]
                orow_zh = orow_zh[:zh_index[0]] + " " * len(row_zh[i]) + orow_zh[zh_index[1]:]
                if self.isChinese(row_zh[i]):
                    row_zh[i] = cn2an.cn2an(row_zh[i])
                ret_map[unkk.strip()] = row_zh[i]
            except:
                continue
        orow_zh = "".join(zh_list)
        return orow_zh, ret_map

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

                tmp_seed = random.randint(0,199)
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

