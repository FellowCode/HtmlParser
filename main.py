import requests
from html_parser import HtmlParser

with open('index.html', 'r', encoding='utf-8') as f:
    s = str(f.read())
    p = HtmlParser(html_s=s)
    print(p.root.select('.logo p')[0].text)