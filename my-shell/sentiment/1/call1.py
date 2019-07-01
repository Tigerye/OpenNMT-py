import os, subprocess


with open('/root/workspace/OpenNMT-py/my-shell/sentiment/sentiment_test_set_p/1/negative_en', 'r') as f:
    for line in f:
        l = line.strip()
        cmd = ['curl', '-X', 'POST', '-H',
               "Content-Type: application/json",
               '-H', "Cache-Control: no-cache",
               '-d', '[{{"id": "snt1", "text": {0} }}]'.format(l),
               'http://api.intellexer.com/analyzeSentiments?apikey=9d1375eb-e80c-49a1-832c-9a47c30b3f35']
        print(subprocess.check_output(cmd))
        __import__('ipdb').set_trace()
