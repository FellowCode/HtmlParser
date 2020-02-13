from html_parser import HtmlParser

p = HtmlParser(url='https://easypassword.ru')
print(p.root)

with open('index.html', 'r', encoding='utf-8') as f:
    s = str(f.read())
    p = HtmlParser(html_s=s)
    print(p.root)
