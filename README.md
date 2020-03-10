# html-jparser
Library for parsing html with JQuery element selection. Very easy to use.

## Installing
Library on PyPi: https://pypi.org/project/html-jparser/0.1/
```
pip install html-jparser
```

## Using
First you need to initialize the class object with __url__ or __html_s__ keyword argument.
```python
from html_jparser.core import HtmlParser

p = HtmlParser(url='https://easypassword.ru/')
# Or for example read html string from file
p = HtmlParser(html_s=open('index.html', 'r', encoding='utf-8').read())
```

The html tag tree starts with root. Root is an abstract tag containing all the tags of an html document. For example, for normal html, the root child would be the html tag. The __children__ attribute of each tag contains a list of children tags.
```python
print(p.root)
# root: [html]
print(p.root.children)
# [html]
print(p.root.children[0])
# html: [head, body]
```
Each tag contains a __select__ method that takes a jQuery select string and returns a list of found tags among child. Select on root tag equally select on parser object.
```python
header = p.root.children[0].children[1].select('h1.center-align')
# Or
header = p.root.select('body h1.center-align')
# equally
header = p.select('body h1.center-align')
```
Each tag contains __attrs__ (attributes dictionary), __comments__ (list of string), __text__ (string), __parent__ (HtmlTag obj), __tag__ (name), __children__ (list of HtmlTag objects).
