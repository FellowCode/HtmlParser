import requests
from html.parser import HTMLParser



import copy
from queue import Queue
from html.entities import name2codepoint

class HtmlParser:
    class CustomHTMLParser(HTMLParser):
        def __init__(self):
            super().__init__()
            self.root = HtmlTag('root', {})
            self.cur_tag = self.root

        def handle_starttag(self, tag, attrs):
            attrs = dict(attrs)
            if 'class' in attrs:
                attrs['class'] = attrs['class'].split(' ')

            t = HtmlTag(tag, attrs, parent=self.cur_tag)
            self.cur_tag.add_child(t)
            self.cur_tag = t

        def handle_endtag(self, tag):
            tags = []
            while self.cur_tag.tag != tag:
                tags.append(self.cur_tag)
                self.cur_tag = self.cur_tag.parent

            for t in tags:
                t.parent = self.cur_tag
                t.childrens = []

            self.cur_tag.childrens += tags
            self.cur_tag = self.cur_tag.parent

        def handle_data(self, data):
            self.cur_tag.text += data

        def handle_comment(self, data):
            self.cur_tag.add_comment(data)

        def feed(self, data):
            super().feed(data)
            return self.root

    def __init__(self, url=None, html_s=None):
        if url:
            html_s = requests.get(url).content.decode('utf-8')
        self.content = html_s
        p = self.CustomHTMLParser()
        self.root = p.feed(self.content)


class HtmlTag:

    def __init__(self, tag, attrs, parent=None):
        self.tag = tag
        self.attrs = attrs
        self.parent = parent
        self.childrens = []
        self.comments = []
        self.text = ''

    def add_child(self, c):
        self.childrens.append(c)

    def add_comment(self, c):
        self.comments.append(c)

    def __str__(self):
        if len(self.childrens) > 0:
            childrens = ': {}'.format(self.childrens)
        else:
            childrens = ''
        return self.tag + childrens

    def __repr__(self):
        return '{}'.format(self.tag)



    def select(self, cmd):
        selectors = cmd.split(' ')
        q = Queue()
        q.put({'element': self, 'selectors': selectors})
        results = []
        while not q.empty():
            data = q.get()
            elem = data['element']
            selectors = data['selectors']

            for child in elem.childrens:
                q.put({'element': child, 'selectors': selectors})

            s_classes = None
            if '.' in selectors[0]:
                s_classes = self.get_group_list('.', selectors[0])     #list of classes
            s_ids = None
            if '#' in selectors[0]:
                s_ids = self.get_group_list('#', selectors[0])[0]      #id

            tag = copy.copy(selectors[0])                      #clean name
            if '.' in tag:
                tag = tag[:tag.find('.')]
            if '#' in tag:
                tag = tag[:tag.find('#')]



            tag_check = True
            classes_check = True
            ids_check = True

            if tag != '':
                tag_check = elem.tag == tag
            if s_classes:
                for s_class in s_classes:
                    if ('class' not in elem.attrs) or (s_class not in elem.attrs['class']):
                        classes_check = False
                        break
            if s_ids:
                ids_check = 'id' in elem.attrs and elem.attrs['id'] == s_ids

            if tag_check and classes_check and ids_check:
                if len(selectors) == 1:
                    results.append(elem)
                else:
                    s = copy.deepcopy(selectors)
                    del s[0]
                    for child in elem.childrens:
                        q.put({'element': child, 'selectors': s})
        return results

    @staticmethod
    def get_group_list(char, selector):
        i = 0
        group = []
        tmp = ''
        is_group = False
        while i < len(selector):
            if selector[i] == char:
                if len(tmp) > 0:
                    group.append(tmp)
                tmp = ''
                is_group = True
            elif selector[i] == '.' or selector[i] == '#':
                if len(tmp) > 0:
                    group.append(tmp)
                tmp = ''
                is_group = False
            elif is_group:
                tmp += selector[i]
            i += 1
        if is_group:
            group.append(tmp)
        return group


