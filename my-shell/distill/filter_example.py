#-*- coding: utf8

fzh_w = open('/root/workspace/translate_data/my_corpus.zh.atok-v4-.train.under100', 'w')
fen_w = open('/root/workspace/translate_data/my_corpus.en.atok-v4-.train.under100', 'w')


with open('/root/workspace/translate_data/my_corpus.zh.atok-v4-.train') as fzh,\
    open('/root/workspace/translate_data/my_corpus.en.atok-v4-.train') as fen,\
    open('/root/workspace/translate_data/my_corpus.zh.atok-v4-.train.under100', 'w') as fzh_w,\
    open('/root/workspace/translate_data/my_corpus.en.atok-v4-.train.under100', 'w') as fen_w:



    for idx, (line_zh, line_en) in enumerate(zip(fzh, fen)) :
        line_zh_len = len(line_zh.split(' '))
        line_en_len = len(line_en.split(' '))

        if line_zh_len >= 100 or line_en_len >= 100:
            print(f"{idx} is being dropped.")
            continue 

        fzh_w.write(line_zh)
        fen_w.write(line_en)

        if idx % 100000 == 0:
            print(f"{idx} is done.")





