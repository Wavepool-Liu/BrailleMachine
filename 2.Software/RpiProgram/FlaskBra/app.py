from flask import Flask,request
from bs4 import BeautifulSoup
import requests
app = Flask(__name__)

summary = "无资讯信息"

def get_summary(result):
    url = 'https://baike.baidu.com/item/'
    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) '
                      'Chrome/67.0.3396.99 Safari/537.36'}
    r = requests.get(url=url + result, headers=headers)
    soup = BeautifulSoup(r.text, 'lxml')
    summary = soup.find('div', attrs={'class': 'lemma-summary'}).text
    if summary is None:
        try:
            url = 'https://baike.baidu.com' + soup.find('div', {'class': "para", 'label-module': "para"}).a['href']
            r = requests.get(url=url, headers=headers)
            soup = BeautifulSoup(r, 'lxml', features="html.parser")
            summary = soup.find('div', attrs={'class': 'lemma-summary'})
        except:
            print('Could not find this entry: ' + result)
            return None
    return summary

@app.route('/')
def index():
    return 'Hello World'


@app.route('/postlwp', methods=["POST", "GET"])
def Post_Data():
    global summary
    data = request.get_data(as_text=True)
    summary = get_summary(data)
    return summary[:40]

if __name__ == '__main__':
    app.debug = True # 设置调试模式，生产模式的时候要关掉debug
    app.run(host="0.0.0.0",port="10086")