# -*- coding: utf-8 -*-

import os, glob
import jieba


def process_line(line):
    line = line.replace('\n', '')
    line_sep = jieba.cut(line.strip())
    return ' '.join(line_sep)


def process_folder(path):
    if not os.path.exists(path):
        print(f"Cannot find {path}", file=sys.stderr)
        sys.exit(-1)

    for sub_folder in glob.glob(f'{path}/[0-9]*'):
        for sub_sub_folder in ['positive', 'negative']:
            this_folder = os.path.join(sub_folder, sub_sub_folder)
            read_write(this_folder)
            print(f'done {this_folder}')


def read_write(folder_path):
    with open(folder_path + '_zh', 'w') as fw:
        for fid in glob.glob(f"{folder_path}/*.txt"):
            _content = read_txt(fid)
            fw.write(_content + '\n')


def read_txt(path):
    content = []
    with open(path, 'r', encoding='utf-8') as f:
        for line in f:
            line = process_line(line)
            content.append(line)
        assert(len(content) == 1)
    return content[0]


if __name__ == '__main__':
    process_folder('sentiment_test_set_p')

    
