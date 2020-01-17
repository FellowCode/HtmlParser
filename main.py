import requests
from html_parser import HtmlParser

# with open('index.html', 'r', encoding='utf-8') as f:
#     s = str(f.read())
p = HtmlParser(url='https://easypassword.ru')
#print(p.content)
print(p.dom.childrens)