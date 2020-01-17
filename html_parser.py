import requests

class HtmlParser:



    def __init__(self, url=None, html_s=None):
        if url:
            html_s = requests.get(url).content.decode('utf-8')

        self.dom, self.text = self.parse(html_s, level=-1, parent=None)

        self.dom = self.dom[0]

        print(self.dom)

    @staticmethod
    def parse(html_s, level, parent):
        i = 0
        start_text = 0
        tags = []
        open_tag = False
        while i < len(html_s):
            if html_s[i] == '<' and html_s[i + 1] != '!':
                open_tag = True
                j = i
                while html_s[j] != '>':
                    j += 1
                if html_s[j - 1] == '/':
                    open_tag = False
                    j -= 1
                tag_data = html_s[i + 1:j]
                tags.append(HtmlTag(tag_data, level+1, parent))
                start_text = j + 1
                i=j+1

            if open_tag:
                tag_level = 1
                while open_tag and i < len(html_s)-1:
                    if html_s[i] == '<' and html_s[i + 1] != '/' and html_s[i + 1] != '!':
                        tag_level += 1
                    if html_s[i] == '/' and html_s[i + 1] == '>':
                        tag_level -= 1
                    if html_s[i] == '<' and html_s[i + 1] == '/':
                        tag_level -= 1
                        if tag_level == 0:
                            j = i+1
                            while html_s[j] != '>':
                                j += 1
                            if html_s[i + 2:j] == tags[-1].tag:
                                text = html_s[start_text:i]
                                tags[-1].parse(text, tags[-1])
                                open_tag = False
                                break
                    i += 1
            i+=1
        return tags, html_s


class HtmlTag:
    tag = ''
    attributes = {}
    childrens = []
    text = ''
    level = 0
    parent = None


    def __init__(self, tag_data, level, parent):
        self.parent = parent
        self.parse_tag_data(tag_data)
        self.level = level


    def __str__(self):
        if len(self.childrens)>0:
            childrens = ': {}'.format(self.childrens)
        else:
            childrens = ''
        return self.tag + childrens

    def __repr__(self):
        return self.__str__()

    def parse(self, html_s, parent):
        self.childrens, self.text = HtmlParser.parse(html_s, self.level, self.tag)

    def parse_tag_data(self, data):
        self.tag = data.split(' ')[0]
