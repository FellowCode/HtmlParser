import requests
from html.parser import HTMLParser
from queue import Queue


class HtmlParser:
    """Html Parser"""
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
                tags += self.cur_tag.children
                self.cur_tag.children = []
                self.cur_tag = self.cur_tag.parent

            for t in tags:
                t.parent = self.cur_tag
                t.children = []

            self.cur_tag.children += tags
            self.cur_tag = self.cur_tag.parent

        def handle_data(self, data):
            self.cur_tag.text += data

        def handle_comment(self, data):
            self.cur_tag.add_comment(data)

        def feed(self, data):
            super().feed(data)
            return self.root

    def __init__(self, url=None, html_s=None):
        """url: string
        html_s: string"""
        if url:
            html_s = requests.get(url).content.decode('utf-8')
        self.content = html_s
        p = self.CustomHTMLParser()
        self.root = p.feed(self.content)

    def select(self, cmd):
        """Jquery select from root"""
        return self.root.select(cmd)


class Selector:
    """Jquery selector string parser
    cmd: string (jquery selector)
    tag: string
    cls: list of string (html classes)
    id: string
    attrs: dict (other attributes)"""
    cls_sep = '.'
    id_sep = '#'
    attr_sep = '[]'
    sep = ' '

    def __init__(self, cmd):
        """cmd: string (jquery selector without space)"""
        self.cmd = cmd
        self.tag = self.__clean_tag()
        self.cls = self.__clean_cls()
        self.id = self.__clean_id()
        self.attrs = self.__clean_attrs()

    def check_html_tag(self, html_tag):
        """Check selector suitable for html tag"""
        return self.__check_tag(html_tag) and self.__check_id(html_tag) \
               and self.__check_cls(html_tag) and self.__check_attrs(html_tag)

    def __check_tag(self, html_tag):
        if self.tag != '':
            return self.tag == html_tag.tag
        return True

    def __check_id(self, html_tag):
        if self.id != '':
            return self.id == html_tag.attrs['id']
        return True

    def __check_cls(self, html_tag):
        if len(self.cls) > 0:
            return self.cls in html_tag.attrs['class']
        return True

    def __check_attrs(self, html_tag):
        for key, value in self.attrs.items():
            if key not in html_tag.attrs or value != html_tag.attrs[key]:
                return False
        return True

    def __clean_tag(self):
        seps = self.cls_sep + self.id_sep + self.attr_sep
        for i, c in enumerate(self.cmd):
            if c in seps:
                return self.cmd[:i]
        return self.cmd

    def __clean(self, start_sep, stop_sep):
        if start_sep not in self.cmd:
            return []
        start = None
        cls_list = []
        for i, c in enumerate(self.cmd):
            if c in stop_sep and start:
                cls_list.append(self.cmd[start+1:i])
            if c == start_sep:
                start = i
        return cls_list

    def __clean_cls(self):
        stop_seps = self.cls_sep + self.id_sep + self.attr_sep
        return self.__clean(self.cls_sep, stop_seps)

    def __clean_id(self):
        stop_seps = self.cls_sep + self.id_sep + self.attr_sep
        _id = self.__clean(self.id_sep, stop_seps)
        if len(_id) > 0:
            return _id[0]
        return ''

    def __clean_attrs(self):
        if len(self.attr_sep) > 1:
            # if attr sep - brackets
            attrs = self.__clean(self.attr_sep[0], self.attr_sep[1])
        else:
            # if attr sep - symbol
            stop_seps = self.cls_sep + self.id_sep + self.attr_sep
            attrs = self.__clean(self.attr_sep[0], stop_seps)

        attrs_dict = {}
        for attr in attrs:
            key, value = attr.split('=')
            attrs_dict[key] = value
        return attrs_dict

    @staticmethod
    def parse(cmd):
        """Return list of Selector
        cmd: Jquery selector like string"""
        return [Selector(cmd_part) for cmd_part in cmd.split(Selector.sep)]


class HtmlTag:
    """Html tag info
    tag: string
    attrs: dict
    parent: HtmlTag
    children: list of HtmlTag
    comments: list of string
    text: string"""
    def __init__(self, tag, attrs, parent=None):
        self.tag = tag
        self.attrs = attrs
        self.parent = parent
        self.children = []
        self.comments = []
        self.text = ''

    def add_child(self, c):
        self.children.append(c)

    def add_comment(self, c):
        self.comments.append(c)

    def __str__(self):
        if len(self.children) > 0:
            return '{}: {}'.format(self.tag, self.children)
        else:
            return self.tag

    def __repr__(self):
        return self.tag

    def select(self, cmd, selector_cls=Selector):
        """Jquery select
        cmd: string (Jquery selector)
        selector_cls: custom Selector (optionally)"""
        q = Queue()
        q.put({'html_tag': self, 'selectors': selector_cls.parse(cmd)})
        results = []
        # BFS
        while not q.empty():
            data = q.get()
            html_tag = data['html_tag']
            selectors = data['selectors']

            for child in html_tag.children:
                q.put({'html_tag': child, 'selectors': selectors})

            if selectors[0].check_html_tag(html_tag):
                if len(selectors) == 1:
                    results.append(html_tag)
                else:
                    for child in html_tag.children:
                        q.put({'html_tag': child, 'selectors': selectors[1:]})
        return results
