import os, subprocess


with open('/root/workspace/OpenNMT-py/my-shell/sentiment/sentiment_test_set_p/1/positive_en', 'r') as f:
    for line in f:
        l = line.strip()
        cmd = ['curl', '-d', f'text={l}', 'http://text-processing.com/api/sentiment/']
        print(subprocess.check_output(cmd))
