import requests
from html_parser import HtmlParser

with open('index.html', 'r', encoding='utf-8') as f:
    s = str(f.read())
    p = HtmlParser(url='https://easypassword.ru')
    #p = HtmlParser(html_s=s)
    #print(p.content)
    print(p.select('.content h1')[0].text)