import requests
import copy
from queue import Queue

class HtmlParser:

    content = None

    def __init__(self, url=None, html_s=None):
        if url:
            html_s = requests.get(url).content.decode('utf-8')
        self.content = html_s
        #print(html_s)
        dom, self.text = self.parse(html_s, level=-1, parent=None)

        self.dom = dom[0]

    def select(self, selector):
        return self.dom.select(selector)

    @staticmethod
    def parse(html_s, level, parent):
        i = 0

        tags = []
        open_tag = False
        start_text = 0
        start_tag = 0               #index of start tag
        while i < len(html_s):
            #find open tag
            if html_s[i] == '<' and html_s[i + 1] != '!':
                open_tag = True
                start_tag = i
                j = i
                while html_s[j] != '>':
                    j += 1
                if html_s[j - 1] == '/':
                    open_tag = False
                    j -= 1
                tag_data = html_s[i + 1:j]
                tags.append(HtmlTag(tag_data, level+1, parent))
                unclosed = ['img', 'meta', 'link']
                if tags[-1].name in unclosed:    #img, meta is not open tag
                    open_tag = False
                start_text = j + 1
                i = j+1

            #find close tag
            if open_tag:
                tag_level = 1
                while open_tag and i < len(html_s)-1:
                    if html_s[i] == '<' and html_s[i + 1] != '/' and html_s[i + 1] != '!':
                        tag_level += 1
                        j=i
                        unclosed = ['img', 'meta', 'link']
                        while html_s[j]!='>':
                            j+=1
                        tag_name = html_s[i+1:j].split(' ')[0]
                        #print(tag_name)
                        if tag_name in unclosed:
                            tag_level -= 1
                        i=j
                    if html_s[i] == '/' and html_s[i + 1] == '>':
                        tag_level -= 1
                    if html_s[i] == '<' and html_s[i + 1] == '/':
                        tag_level -= 1
                        if tag_level == 0:
                            j = i+1
                            while html_s[j] != '>':
                                j += 1
                            if html_s[i + 2:j] == tags[-1].name:
                                html = html_s[start_text:i]           #html inner tag
                                tags[-1].html = html
                                tags[-1].parse(html)                  #recursive parse inner tags
                                open_tag = False
                                html_s = html_s[:start_tag] + html_s[j+1:]      #remove html inner tag
                                i -= i - start_tag
                                break
                    i += 1
            i += 1
        return tags, html_s

class HtmlTag:
    name = ''
    attrs = None
    tag_data = ''
    childrens = []
    text = ''
    level = 0
    html = ''
    parent = None

    def __init__(self, tag_data, level, parent):
        self.parent = parent
        self.tag_data = tag_data
        self.parse_tag_data()
        self.level = level
        self.attrs = {}

    def __str__(self):
        if len(self.childrens) > 0:
            childrens = ': {}'.format(self.childrens)
        else:
            childrens = ''
        return self.name + childrens

    def __repr__(self):
        return '{}'.format(self.name)

    def parse(self, html_s):
        self.html = html_s
        self.childrens, self.text = HtmlParser.parse(html_s, self.level, self)

    def parse_tag_data(self):                      #parsing data inner <>
        self.name = self.tag_data.split(' ')[0]    #tag
        if self.tag_data.find(' ')>-1:
            attrs = self.tag_data[self.tag_data.find(' ') + 1:]
            d = {}
            i = -1
            key = ''
            value = ''
            is_key = True
            in_quotes = False
            while i < len(attrs)-1:
                i += 1
                if attrs[i] == attrs[i-1] == ' ':
                    continue
                if attrs[i] == '=':
                    is_key = False
                    continue
                if not in_quotes and attrs[i] == ' ':    #new element of data
                    is_key = True
                    continue
                if is_key and attrs[i] != ' ':
                    key += attrs[i]
                elif attrs[i] not in '\"\'':
                    value += attrs[i]
                else:
                    in_quotes = not in_quotes
                    if not in_quotes:                #save element of data
                        key = copy.copy(key)
                        value = copy.copy(value)
                        d[key] = value
                        key = ''
                        value = ''

            if key not in d:
                d[key] = value

            if 'class' in d:
                d['class'] = d['class'].split(' ')

            self.attrs = d

    def select(self, cmd):
        selectors = cmd.split(' ')
        q = Queue()
        q.put({'element': self, 'selectors': selectors})
        results = []
        while not q.empty():
            data = q.get()
            elem = data['element']
            elem.parse_tag_data()
            selectors = data['selectors']
            s_classes = None
            if '.' in selectors[0]:
                s_classes = self.get_group_list('.', selectors[0])     #list of classes
            s_ids = None
            if '#' in selectors[0]:
                s_ids = self.get_group_list('#', selectors[0])[0]      #id

            name = copy.copy(selectors[0])                      #clean name
            if '.' in name:
                name = name[:name.find('.')]
            if '#' in name:
                name = name[:name.find('#')]

            for child in elem.childrens:
                q.put({'element': child, 'selectors': selectors})

            name_check = True
            classes_check = True
            ids_check = True

            if name != '':
                name_check = elem.name == name
            if s_classes:
                for s_class in s_classes:
                    if ('class' not in elem.attrs) or (s_class not in elem.attrs['class']):
                        classes_check = False
                        break
            if s_ids:
                ids_check = 'id' in elem.attrs and elem.attrs['id'] == s_ids

            if name_check and classes_check and ids_check:
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


