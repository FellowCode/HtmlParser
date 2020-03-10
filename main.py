from html_jparser.core import HtmlParser

p = HtmlParser(url='https://easypassword.ru/accounts/login/')
print(p.root.select('input[name=csrfmiddlewaretoken]')[0].attrs)

p = HtmlParser(html_s=open('index.html', 'r', encoding='utf-8').read())
print(p.root)