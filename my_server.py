# coding = utf-8

# @time    : 2019/6/12 10:48 AM
# @author  : alchemistlee
# @fileName: my_server.py
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


app = Flask(__name__)


def main(opt):
    ArgumentParser.validate_translate_opts(opt)
    logger = init_logger(opt.log_file)

    translator = build_translator(opt, report_score=True)
    src_shards = split_corpus(opt.src, opt.shard_size)
    tgt_shards = split_corpus(opt.tgt, opt.shard_size) \
        if opt.tgt is not None else repeat(None)
    shard_pairs = zip(src_shards, tgt_shards)

    for i, (src_shard, tgt_shard) in enumerate(shard_pairs):
        logger.info("Translating shard %d." % i)
        translator.translate(
            src=src_shard,
            tgt=tgt_shard,
            src_dir=opt.src_dir,
            batch_size=opt.batch_size,
            attn_debug=opt.attn_debug
            )


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


opt = None
translator = None
logger = None


def _translate(input_text):
    cuted = cut_input(input_text)
    score,prediction = translator.translate(
      src=cuted,
      tgt=None,
      src_dir=opt.src_dir,
      batch_size=opt.batch_size,
      attn_debug=opt.attn_debug
    )
    return score,prediction


@app.route('/translate/zh2en/',methods=['GET'])
def tran_zh2en_interface():
    input = request.args.get('in')
    score,pred = _translate(input)
    print(' score = %s , pred = %s ' % (str(score), str(pred)))


if __name__ == '__main__':

    parser = _get_parser()
    opt = parser.parse_args()

    logger = init_logger(opt.log_file)

    translator = _get_translator(opt)

    app.debug = True
    app.run(host='0.0.0.0')