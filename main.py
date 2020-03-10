import requests
from html_jparser import HtmlParser
import time

session = requests.Session()
r = session.get('https://smotret-anime.online/users/login')
ts = time.time()
p = HtmlParser(html_s=r.content.decode('utf-8'))
print('time parse', time.time() - ts)
ts = time.time()
input = p.select('#login-form input[type=hidden][name=csrf]')[0]
print('time select', time.time() - ts)
ts = time.time()
input2 = p.select('#login-form input[type=hidden][name=csrf]', cache=True)[0]
print('time select with cache', time.time() - ts)
path = input.get_path()
print(path)           # 0:1:3:0:0:1:0:0:0:0:0
ts = time.time()
print(p.get_tag(path))
print('time get_tag', time.time() - ts)