import requests
from html_jparser import HtmlParser
import time

session = requests.Session()
r = session.get('https://smotret-anime.online/users/login')
p = HtmlParser(html_s=r.content.decode('utf-8'))
print(p.select('#login-form input[type=hidden][name=csrf]'))