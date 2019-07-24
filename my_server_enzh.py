# coding = utf-8

# @time    : 2019/6/12 10:48 AM
# @author  : alchemistlee
# @fileName: my_server_zhen.py
# @abstract:

from __future__ import unicode_literals

from flask import Flask
from flask import request
from flask import render_template

from itertools import repeat

from onmt.utils.logging import init_logger
from onmt.utils.misc import split_corpus
from onmt.translate.translator import build_translator

import onmt.opts as opts
from onmt.utils.parse import ArgumentParser
from toolkit.cut_zh_corpus import cut_input

import json
import codecs
from  subword_nmt.apply_bpe import BPE
from translate_proc import PrePostProc

import str_utils
import nltk
import jieba


app = Flask(__name__)


# def main(opt):
#     ArgumentParser.validate_translate_opts(opt)
#     logger = init_logger(opt.log_file)
#
#     translator = build_translator(opt, report_score=True)
#     src_shards = split_corpus(opt.src, opt.shard_size)
#     tgt_shards = split_corpus(opt.tgt, opt.shard_size) \
#         if opt.tgt is not None else repeat(None)
#     shard_pairs = zip(src_shards, tgt_shards)
#
#     for i, (src_shard, tgt_shard) in enumerate(shard_pairs):
#         logger.info("Translating shard %d." % i)
#         print()
#         translator.translate(
#             src=src_shard,
#             tgt=tgt_shard,
#             src_dir=opt.src_dir,
#             batch_size=opt.batch_size,
#             attn_debug=opt.attn_debug
#             )


def _get_parser():
    parser = ArgumentParser(description='translate.py')

    opts.config_opts(parser)
    opts.translate_opts(parser)
    return parser


def _get_translator(opt):
    # ArgumentParser.validate_translate_opts(opt)
    print('hello 1')
    translator = build_translator(opt, report_score=True)
    return translator


def _get_input_func(input_lst):
    tmp_list = list()
    tmp_list.extend(input_lst)
    for item in tmp_list:
      yield item
    return


def _bpe_proc_lines(input_lst):
    res = []
    for item in input_lst:
        res.append(bpe.process_line(item))
    return res


def _tokenize_proc_lines(input_str):
    item_ = ' '.join(nltk.word_tokenize(input_str))
    return item_


def merge_dict(a,b):
    for k in b.keys():
        if not k in a.keys():
            a[k] = b[k]
    return a


opt = None
translator = None
logger = None
bpe = None
proc = None


def _unzip_list(origin_pred):
    res = []
    for i in range(len(origin_pred)):
        item = origin_pred[i]
        res.append(item[0])
    return res

def normal_cap(token_list):
    res = []
    for token in token_list:
        if token[0].isupper():
            tmp = token[0] + token[1:].lower()
            res.append(tmp)
        else:
            res.append(token)
    return res


def _translate(input_text):
    print(input_text)
    # tokenize
    cut = _tokenize_proc_lines(input_text)
    print('tok = {}'.format(cut))
    # split 2 list
    cut = cut.split()
    
    #TODO: 纯大写单词替换成只开头大写
    cut = normal_cap(cut)

    # replace entity
    print("cut you want: {}".format(" ".join(cut)))
    cuted, rep2val = proc.pre_proc_en_py(cut)
    print("sp_str: {}".format(cuted))
    print("sp_map: {}".format(rep2val))
    tmp_cut_str = ' '.join(cuted)
    tmp_cut_str, rep2val_nu = proc.pre_proc_en_nu(tmp_cut_str)
    print("input_text with unks: {}".format(tmp_cut_str))

    rep2val = merge_dict(rep2val, rep2val_nu)
    print(' rep2val = {}'.format(rep2val))

    # TODO
    #tmp_cut_str = tmp_cut_str.lower()

    # cut = cut_input(input_text)
    cut = str_utils.split_as_sentence(tmp_cut_str, type='en')
    tmp = []
    for item in cut:
        if len(item) != 0:
            tmp.append(item)
    cut = tmp
    print('cut-sentence : {} '.format(cut))

    # bpe
    cut = _bpe_proc_lines(cut)
    print('bpe = {}'.format(cut))

    # TODO: 大小写对BPE影响很大
    #cut = list(map(lambda x:x.lower(), cut)) 

    cut_gen = _get_input_func(cut)
    score,prediction = translator.translate(
      src=cut_gen,
      tgt=None,
      src_dir=opt.src_dir,
      batch_size=opt.batch_size,
      attn_debug=opt.attn_debug
    )

    output_lst = _unzip_list(prediction)
    output_str = ' '.join(output_lst)
    print('ori = {}'.format(output_str))
    # replace entity
    output_str = proc.post_proc(output_str, rep2val)
    print('rep ent = {}'.format(output_str))
    # bpe decode
    output_str = proc.proc_bpe(output_str)
    print('rep bpe = {}'.format(output_str))

    return score,output_str


@app.route('/translate/en2zh/', methods=['GET', 'POST'])
def tran_en2zh_interface():
    if request.method == 'POST':
        data = request.get_data()
        json_data = json.loads(data.decode("utf-8"))
        input = json_data['in']
    else:
        input = request.args.get('in')
    score,pred = _translate(input)
    print(' score = %s , pred = %s ' % (str(score), str(pred)))
    res = {
      "output": pred
    }
    return json.dumps(res, ensure_ascii=False)


if __name__ == '__main__':

    parser = _get_parser()
    opt = parser.parse_args()

    logger = init_logger(opt.log_file)

    translator = _get_translator(opt)

    c = codecs.open('/root/workspace/translate_data/my_corpus_v6.en.tok.processed6-bpe-code', encoding='utf-8')
    m = -1
    sp = '@@'
    voc = None
    bpe = BPE(c, m, sp, voc, None)

    proc = PrePostProc()
    proc.load_data('py_ent_dict.txt')

    app.debug = True
    app.run(host='0.0.0.0',port=5002)
