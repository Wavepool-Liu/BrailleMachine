# coding=utf-8

import sys
import json
import base64
import time
import os
import re
from aip import AipSpeech
import requests
from bs4 import BeautifulSoup
# import tobraille.toBraille

API_KEY = 'FGes8DuixybiSCtCXUpn8u24'
SECRET_KEY = 'RAlc4lcou8GNpyNgiGUoZsswBdsn1A5r'

IS_PY3 = sys.version_info.major == 3

if IS_PY3:
    from urllib.request import urlopen
    from urllib.request import Request
    from urllib.error import URLError
    from urllib.parse import urlencode
    timer = time.perf_counter
else:
    from urllib2 import urlopen
    from urllib2 import Request
    from urllib2 import URLError
    from urllib import urlencode
    if sys.platform == "win32":
        timer = time.clock
    else:
        # On most other platforms the best timer is time.time()
        timer = time.time

class DemoError(Exception):
    pass

def fetch_token():
    """  TOKEN start """
    SCOPE = 'audio_voice_assistant_get'  # 有此scope表示有asr能力，没有请在网页里勾选，非常旧的应用可能没有
    TOKEN_URL = 'http://openapi.baidu.com/oauth/2.0/token'
    params = {'grant_type': 'client_credentials',
              'client_id': API_KEY,
              'client_secret': SECRET_KEY}
    post_data = urlencode(params)
    if (IS_PY3):
        post_data = post_data.encode( 'utf-8')
    req = Request(TOKEN_URL, post_data)
    try:
        f = urlopen(req)
        result_str = f.read()
    except URLError as err:
        result_str = err.read()
    if (IS_PY3):
        result_str =  result_str.decode()
    result = json.loads(result_str)
    if ('access_token' in result.keys() and 'scope' in result.keys()):
        if SCOPE and (not SCOPE in result['scope'].split(' ')):  # SCOPE = False 忽略检查
            raise DemoError('scope is not correct')
        return result['access_token']
    else:
        raise DemoError('MAYBE API_KEY or SECRET_KEY not correct: access_token or scope not found in token response')
    """  TOKEN end """

def says_api(content):
    client=AipSpeech('23670177',API_KEY,SECRET_KEY)
    if content is None:
        content = "无该咨询信息"
        result = client.synthesis(content, 'zh', 1, {'vol': 10,'per':4 })
    else:
        result = client.synthesis(content,'zh',1,{'vol':13,'per':4,'spd':3,'pit':6})
    if not isinstance(result,dict):
        with open('say.mp3','wb') as f:
            f.write(result)
    os.system('mpg123 say.mp3')

def getvoice(second,wavfile):
    print("Start recording "+str(second)+"S")
    os.system('arecord -D "plughw:1" -f S16_LE -r 16000 -d '+str(second)+' '+wavfile)
    print("Record Finish")

def voicetotext(token,wavfile):
    # 需要识别的文件
    AUDIO_FILE = wavfile  # 只支持 pcm/wav/amr 格式，极速版额外支持m4a 格式
    # 文件格式
    # FORMAT = "wav"  # 文件后缀只支持 pcm/wav/amr 格式，极速版额外支持m4a 格式
    FORMAT = AUDIO_FILE[-3:]  # 文件后缀只支持 pcm/wav/amr 格式，极速版额外支持m4a 格式
    CUID = '16019027'
    # 采样率
    RATE = 16000  # 固定值
    # 普通版
    DEV_PID = 1537  # 1537 表示识别普通话，使用输入法模型。根据文档填写PID，选择语言及识别模型
    ASR_URL = 'http://vop.baidu.com/server_api'

    with open(AUDIO_FILE, 'rb+') as speech_file:
        speech_data = speech_file.read()
    length = len(speech_data)
    if length == 0:
        raise DemoError('file %s length read 0 bytes' % AUDIO_FILE)
    speech = base64.b64encode(speech_data)
    if (IS_PY3):
        speech = str(speech, 'utf-8')
    params = {'dev_pid': DEV_PID,
              # "lm_id" : LM_ID,    #测试自训练平台开启此项
              'format': FORMAT,
              'rate': RATE,
              'token': token,
              'cuid': CUID,
              'channel': 1,
              'speech': speech,
              'len': length
              }
    post_data = json.dumps(params, sort_keys=False)
    req = Request(ASR_URL, post_data.encode('utf-8'))
    req.add_header('Content-Type', 'application/json')
    try:
        begin = timer()
        f = urlopen(req)
        result_str = f.read()
        print("Request time cost %f" % (timer() - begin))
    except URLError as err:
        print('asr http response http code : ' + str(err.code))
        result_str = err.read()

    if (IS_PY3):
        result_str = str(result_str, 'utf-8')
        reg = "[^0-9A-Za-z\u4e00-\u9fa5]"
        result_str = re.sub(reg, '', str(eval(result_str)["result"]))  # 利用正则表达式删除符号
    with open("result.txt", "w") as of:
        of.write(result_str)
    return result_str


def get_summary(Result):
    url = 'https://baike.baidu.com/item/'
    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/67.0.3396.99 Safari/537.36'}
    r = requests.get(url=url + Result, headers=headers)
    soup = BeautifulSoup(r.text, 'lxml')

    summary = soup.find('div', attrs={'class': 'lemma-summary'})

    if summary == None:
        try:
            url = 'https://baike.baidu.com' + soup.find('div', {'class': "para", 'label-module': "para"}).a['href']

            r = requests.get(url=url, headers=headers)
            soup = BeautifulSoup(r.text, 'lxml')

            summary = soup.find('div', attrs={'class': 'lemma-summary'})
        except:
            print('Could not find this entry: ' + result)
            return None

    return summary.text


if __name__ == '__main__':
    token = fetch_token()
    # getvoice(3,"result.wav")
    # result = voicetotext(token,"result.wav")
    # print(tobraille.toBraille.toBraille(result))
    # says_api(result)
    text=get_summary("海豚")
    says_api(text)