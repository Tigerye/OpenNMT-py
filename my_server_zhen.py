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
from translate_proc import PrePostProc

import codecs
from subword_nmt.apply_bpe import BPE

import str_utils


app = Flask(__name__)


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


def _get_input_func(input_str):
    tmp_list = list()
    tmp_list.extend(input_str)
    for item in tmp_list:
      yield item
    return

opt = None
translator = None
logger = None
proc = None
bpe = None


def merge_dict(a,b):
    for k in b.keys():
        if not k in a.keys():
            a[k] = b[k]
    return a


def _bpe_proc_lines(input_lst):
    res = []
    for item in input_lst:
        item_ = bpe.process_line(item)
        if len(item_) > 0:
            res.append(item_)
    return res


def _unzip_list(origin_pred):
    res = []
    for i in range(len(origin_pred)):
        item = origin_pred[i]
        res.append(item[0])
    return res


def _translate(input_text):

    cut = cut_input(input_text,'lst')
    # replace entity
    cuted, rep2val = proc.pre_proc_zh_py(cut)
    tmp_cut_str = ' '.join(cuted)
    tmp_cut_str, rep2val_nu = proc.pre_proc_zh_nu(tmp_cut_str)

    rep2val = merge_dict(rep2val,rep2val_nu)
    print(' rep2val = {}'.format(rep2val))
    # split sentence
    tmp_sents = str_utils.split_as_sentence(tmp_cut_str,type='zh')
    # bpe
    # tmp_cut_str = bpe.process_line(tmp_cut_str)
    tmp_bpes = _bpe_proc_lines(tmp_sents)
    print('bpe-res = {}'.format(tmp_bpes))
    # cut = tmp_cut_str.split()
    # print('cut = {}'.format(cut))
    # infer
    cut_gen = _get_input_func(tmp_bpes)
    score,prediction = translator.translate(
      src=cut_gen,
      tgt=None,
      src_dir=opt.src_dir,
      batch_size=opt.batch_size,
      attn_debug=opt.attn_debug
    )

    # output_str = prediction[0][0]
    # output_lst = prediction[0]
    output_lst = _unzip_list(prediction)
    output_str = '/'.join(output_lst)
    print('ori = {}'.format(output_str))
    # replace entity
    output_str = proc.post_proc(output_str,rep2val)
    print('rep ent = {}'.format(output_str))
    # bpe decode
    output_str = proc.proc_bpe(output_str)
    print('rep bpe = {}'.format(output_str))

    return score,output_str


@app.route('/translate/zh2en/',methods=['GET','POST'])
def tran_zh2en_interface():

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
    return json.dumps(res)


if __name__ == '__main__':

    parser = _get_parser()
    opt = parser.parse_args()

    logger = init_logger(opt.log_file)

    translator = _get_translator(opt)

    proc = PrePostProc()
    proc.load_data('py_ent_dict.txt')

    c = codecs.open('/root/workspace/translate_data/my_corpus_v6.zh-cut.processed6-bpe-code', encoding='utf-8')
    m = -1
    sp = '@@'
    voc = None
    bpe = BPE(c, m, sp, voc, None)

    app.debug = True
    app.run(host='0.0.0.0',port=5000, extra_files=['py_ent_dict.txt'])
