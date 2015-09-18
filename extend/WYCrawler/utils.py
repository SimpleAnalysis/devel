#!/usr/bin/env python
# -*- coding:utf-8 -*-

# Copyright (c) 2013 DY.Feng <yyfeng88625@gmail.com>
# All rights reserved

# pylint:disable-all

"""工具模块包

"""

#$Id$
__author__ = [
    'DY.Feng <yyfeng88625@gmail.com>',
]
__version__ = '$Revision: 0.1 $'

# import lxml
from lxml.html.clean import Cleaner
import lxml.html as HTML
# import lxml.html.soupparser as HTML
from lxml.html import HtmlElement
from lxml.etree import XPathError, tostring

import HTMLParser

HTML_PARSER = HTMLParser.HTMLParser()

Cleaner.safe_attrs_only = False
Cleaner.safe_attrs = False
Cleaner.annoying_tags = False
Cleaner.style = True
Cleaner.meta = False
Cleaner.page_structure = False
Cleaner.processing_instructions = False
Cleaner.embedded = False


class XPath(object):
    """XPath工具类，简化lxml操作。"""

    def __init__(self, content=None):
        """初始化

        :param content: 需要预编译的内容。
        """

        #TODO: Cleaner误杀实在太严重了
        #self.cleaner = Cleaner()
        # This is True because we want to activate the javascript filter
        #self.cleaner.scripts = clear_scripts
        #self.cleaner.javascript = clear_scripts

        if content is not None:
            if isinstance(content, HtmlElement):
                self._parser_content = content
            else:
                self.compile(content)

    def compile(self, content):
        """把内容预编译成xml树，加快xpath表达式运行。

        :param content: 需要预编译的内容，unicode文本。

        """

        self._parser_content = HTML.fromstring(content)

        #self._parser_content = self.cleaner.clean_html(
        #    HTML.document_fromstring(content))

    def execute(self, *arg, **kwargs):
        """运行XPath表达式。

        :param path: xpath表达式。
        :return: 返回结果列表，有可能是字符串或者XPath对象。例如：

                * ``//a/@href`` 返回一个包含所有a标签href属性的字符串列表
                * ``//div[@class='test']`` 返回一个 XPath 列表。
        """
        try:
            return [unicode(x).strip()
                    if isinstance(x, basestring)
                    else XPath(tostring(x))
                    for x in self._parser_content.xpath(*arg, **kwargs)]

        except XPathError, err:
            print err
            return None

    def to_html(self):
        """返回html文本。"""
        return HTML_PARSER.unescape(tostring(self._parser_content, pretty_print=True))

        #return HTML.tostring(self._parser_content)

    def to_text(self):
        """返回本节点文本内容,不包含子节点。"""
        return unicode(self._parser_content.text_content())




