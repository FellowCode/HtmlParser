import requests
from html_parser import HtmlParser

with open('index.html', 'r', encoding='utf-8') as f:
    s = str(f.read())
    HtmlParser(html_s=s)