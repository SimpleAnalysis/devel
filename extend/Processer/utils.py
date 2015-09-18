#!/usr/bin/env python
# -*- coding:utf-8 -*-

# Copyright (c) 2013 DY.Feng <yyfeng88625@gmail.com>
# All rights reserved


"""工具集.


"""

#$Id$
__author__ = [
    'DY.Feng <yyfeng88625@gmail.com>',
]
__version__ = '$Revision: 0.1 $'

from HTMLParser import HTMLParser
import re

import codecs
import os
from os import makedirs
import errno


class _DeHTMLParser(HTMLParser):

    def __init__(self):
        HTMLParser.__init__(self)
        self.__text = []

    def handle_data(self, data):
        text = data.strip()
        if text:
            text = re.sub('[ \t\r\n]+', ' ', text)
            self.__text.append(text)

    def handle_starttag(self, tag, attrs):
        if tag in ('p', 'br', 'li', 'div', 'tr'):
            self.__text.append('\n')
        elif tag in ('td',):
            self.__text.append(' ')
    #
    # def handle_startendtag(self, tag, attrs):
    #     if tag == 'br':
    #         self.__text.append('\n\n')

    def text(self):
        return ''.join(self.__text).strip()


RE_SCRIPT = re.compile(r'<script.*?>[\W\w]*?</script>', re.I)  # Script
RE_STYLE = re.compile(r'<\s*style[^>]*>[^<]*<\s*/\s*style\s*>', re.I)  # style
RE_HEAD = re.compile(r'<\s*head[^>]*>.*<\s*/\s*head\s*>', re.I)  # head标签
RE_DOCTYPE = re.compile(r'<!doctype.*?>', re.I)  # doctype标签

# import BeautifulSoup
# from html2text import HTML2Text


def dehtml(text):
    """清除html标签

    :param text:
    :return: :rtype:
    """
    text = RE_SCRIPT.sub('', text)  # 去掉SCRIPT
    text = RE_STYLE.sub('', text)  # 去掉style
    text = RE_HEAD.sub('', text)  # 去掉head
    text = RE_DOCTYPE.sub('', text)
    parser = _DeHTMLParser()
    parser.feed(text)
    parser.close()
    return parser.text()


RE_COMBINE = re.compile(r'\n+')
RE_WINDOWS = re.compile(r'\r')


def format_text(text):
    """整理文本，多个换行转成一个换行，不可见字符去掉。

    :param text:
    :return: :rtype:
    """
    text = just_readable(text)
    text = RE_WINDOWS.sub('', text)
    #text = '\n'.join([line.strip() for line in text.split('\n')])
    text = RE_COMBINE.sub('\n', text).strip()
    return re.sub(r'\n+', '\n', text)


def html_to_text(html):
    """把html代码整理出text格式。

    :param html: html代码。
    :return:
    """

    # TODO: dehtml 这个其实不大可靠，有些页面会弄不出来
    return format_text('\n' + dehtml(html))


def text_to_html(text):
    """把text转成html，就是把回车换成<br>。

    :param text:
    :return: :rtype:
    """
    return text.replace('\r', '').replace('\n', '<br>')


RE_CHINESE = re.compile(ur'[^\u4e00-\u9fbf\uFF00-\uFFEF\x30-\x39]')
RE_NUMBER = re.compile(ur'[^\x30-\x39]')
RE_ALPHABET = re.compile(ur'[^\x61-\x7a\x41-\x5a]')
# readable_re = re.compile(
#     ur'[^\u4e00-\u9fbf\uFF00-\uFFEF\x30-\x39\x30-\x39\x61-\x7a\x41-\x5a]')
RE_READABLE = re.compile(ur'[\u2000-\u206F]')


def normalize_whitespaces(text):
    """把所有的unicode空格都归一化为标准空格。
http://en.wikipedia.org/wiki/Space_%28punctuation%29#Spaces_in_Unicode

    :param text:
    :return:
    """
    return re.sub(ur'[\ue5e5\u0020\u00A0\u1680\u180E\u2000-\u200D\u202F\u205F\u2060\u3000\uFEFF]', ' ', text)


def strip_whitespaces(text):
    """清除所有的空格，包括全角，千奇百怪的“空格”。

    :param text:
    :return: :rtype:
    """
    return normalize_whitespaces(text).replace(' ', '')


def normalize_numeric(text):
    """把数字归一化。

    :param text:
    """
    text = re.sub(
        u'[0oO\u041e\u25cb\uff2f\u3007\u039f\u03bf\u20dd\u25ef\u2b58\u1F315]', u'零', text)
    return text


def normalize_parentheses(text):
    """括号归一化成半角的()。

    :param text:
    :return: :rtype:
    """
    text = re.sub(ur'[（﹙【［〔[]', '(', text)
    text = re.sub(ur'[）﹚】］〕\]]', ')', text)
    return text


def just_chinese(text):
    return RE_CHINESE.sub(' ', text)


def just_number(text):
    return RE_NUMBER.sub(' ', text)


def just_alphabet(text):
    return RE_ALPHABET.sub(' ', text)


def just_readable(text):
    return RE_READABLE.sub('', text)


def multiple_replace(text, adict):
    rx = re.compile('|'.join(map(re.escape, adict)))
    return rx.sub(lambda match: adict[match.group(0)], text)


CN_NUM_DICT = {u'零': 0, u'一': 1, u'二': 2, u'三': 3, u'四': 4, u'五': 5, u'六': 6, u'七': 7, u'八': 8, u'九': 9, u'十': 10,
               u'百': 100, u'千': 1000, u'万': 10000,
               u'０': 0, u'１': 1, u'２': 2, u'３': 3, u'４': 4, u'５': 5, u'６': 6, u'７': 7, u'８': 8, u'９': 9,
               u'壹': 1, u'贰': 2, u'叁': 3, u'肆': 4, u'伍': 5, u'陆': 6, u'柒': 7, u'捌': 8, u'玖': 9, u'拾': 10,
               u'佰': 100, u'仟': 1000, u'萬': 10000, u'亿': 100000000,
               }


def chinese_to_digit(string):
    """

    :param string:
    :return: :rtype:
    """
    count = 0
    result = 0
    tmp = 0
    billion = 0
    while count < len(string):
        tmp_chr = string[count]
        # print tmpChr
        tmp_num = CN_NUM_DICT.get(tmp_chr, None)
        if tmp_num is None:
            try:
                tmp_num = int(tmp_chr)
            except ValueError:
                pass

        # 如果等于1亿
        if tmp_num == 100000000:
            result = result + tmp
            result = result * tmp_num
            # 获得亿以上的数量，将其保存在中间变量Billion中并清空result
            billion = billion * 100000000 + result
            result = 0
            tmp = 0
        # 如果等于1万
        elif tmp_num == 10000:
            result = result + tmp
            result = result * tmp_num
            tmp = 0
        # 如果等于十或者百，千
        elif tmp_num >= 10:
            if tmp == 0:
                tmp = 1
            result = result + tmp_num * tmp
            tmp = 0
        # 如果是个位数
        elif tmp_num is not None:
            tmp = tmp * 10 + tmp_num
        count += 1
    result = result + tmp
    result = result + billion
    return result


# from sqlalchemy import and_, func
#
# def column_windows(session, column, windowsize):
#     """Return a series of WHERE clauses against
#     a given column that break it into windows.
#
#     Result is an iterable of tuples, consisting of
#     ((start, end), whereclause), where (start, end) are the ids.
#
#     Requires a database that supports window functions,
#     i.e. Postgresql, SQL Server, Oracle.
#
#     Enhance this yourself !  Add a "where" argument
#     so that windows of just a subset of rows can
#     be computed.
#
#     """
#
#     def int_for_range(start_id, end_id):
#         if end_id:
#             return and_(
#                 column >= start_id,
#                 column < end_id
#             )
#         else:
#             return column >= start_id
#
#     query = session.query(column, func.row_number().over(order_by=column).label('rownum')).from_self(column)
#     if windowsize > 1:
#         query = query.filter("rownum %% %d=1" % windowsize)
#
#     intervals = [_id for _id, in query]
#
#     while intervals:
#         start = intervals.pop(0)
#         if intervals:
#             end = intervals[0]
#         else:
#             end = None
#         yield int_for_range(start, end)


def windowed_query(query, model, windowsize):
    """把本来要返回的一个大型记录集分解，分批查询，一个个返回，这样就可以防止查询的记录过大。

    :param query: 查询对象。
    :param model: 模型类。
    :param windowsize: 窗口大小。
    """
    last_id = 0
    cols = True
    while cols:
        cols = query.filter(model.id > last_id).limit(windowsize).all()

        for col in cols:
            last_id = col.id
            yield col

            # for whereclause in column_windows(
            #         q.session,
            #         column, windowsize):
            #     for row in q.filter(whereclause).order_by(column):
            #         yield row


# TODO:哪个版本好呢？
def page_query(query, model, page_size):
    """分页查询，把所有的记录分批返回。

    :param query: 查询对象。
    :param model: 模型类。
    :param page_size: 每页的大小。
    """

    first = query.first()
    first = first and first.id - 1 or 0
    while True:
        records = query.filter(model.id > first).limit(page_size).all()
        # 这里close是为了防止mysql gone away，因为如果你不close，他的pool也就保持着不敢recycle，从而超时。
        query.session.close()
        if records:
            yield records
        else:
            break
        first = records[-1].id


# def page_query(q,table_cls, page_size):
#     offset = 0
#     while True:
#         records = q.limit(page_size).offset(offset).all()
#         if records:
#             yield records
#         else:
#             break
#         offset += page_size


import inspect


# def get_all_classes(obj, parent_cls, classes_name=None):
#     """获取某个对象里面，继承了指定祖父类的类。
#
#     :param obj: 要获取类的对象，可以是类/模块/包。
#     :param parent_cls: 祖父类。
#     :param classes_name: 如果指定了，则只获取类名在classes_name中的类，列表。
#     :return: 类列表。
#     """
#     classes_cls = []
#     for name, cls in inspect.getmembers(obj):
#
#         if inspect.isclass(cls) and issubclass(cls, parent_cls) \
#             and cls is not parent_cls:
#             classes_cls.append(cls)
#
#     if classes_name:
#         return filter(lambda cls: cls.__name__ in classes_name,
#                       classes_cls)
#     else:
#         return classes_cls


def get_parent_with_ancestor(cls, ancestor):
    """寻找一个继承了ancestor祖先的父类。
    ancestor
    +---- ancestor's son  <---获取这个
    +------- ...
    +------- ...
    +------------ me


    :param cls:
    :param ancestor:
    :return:
    """

    for parent_cls in inspect.getmro(cls):
        if ancestor in parent_cls.__bases__ and cls is not parent_cls \
                and parent_cls is not ancestor:
            return parent_cls


HTML_PARSER = HTMLParser()


def html_unescape(html):
    """html字符转移。 eg:&lt;变 <

    :param html:
    :return: :rtype:
    """
    return HTML_PARSER.unescape(html)


def makedirs_ignore_exist(name, mode=0777):
    """模仿mkdir -p。

    :param name:
    :param mode:
    :raise:
    """
    try:
        makedirs(name, mode)
    except OSError, err:
        # be happy if someone already created the path
        if err.errno != errno.EEXIST:
            raise


def dump_object_to_files(obj, path):
    """把对象输出到文件。

    :param obj: 要输出的对象，字符串/字典/列表/可str的对象。
    :param path: 输出的路径，如果对象是字符串，那么就会输出path.html的文件
    """
    if isinstance(obj, dict):
        makedirs_ignore_exist(path)
        for key in obj.keys():
            dump_object_to_files(obj[key], os.sep.join([path, key]))
    elif isinstance(obj, list):
        makedirs_ignore_exist(path)
        for index, item in enumerate(obj):
            dump_object_to_files(item, os.sep.join([path, str(index)]))
    elif isinstance(obj, basestring):
        with codecs.open(path + '.html', 'w+', encoding='utf-8') as _fb:
            _fb.write(obj)
    else:
        # 尝试字符串化
        dump_object_to_files(str(obj), path)


# TODO:之前的RPC控制，以后究竟是不是用好呢？
# from SimpleXMLRPCServer import SimpleXMLRPCServer, SimpleXMLRPCRequestHandler
# from SocketServer import ThreadingMixIn
# import logging
#
#
# class LoggingSimpleXMLRPCRequestHandler(SimpleXMLRPCRequestHandler):
#     logger = logging.getLogger('root.XMLRPCServer')
#
# SimpleXMLRPCRequestHandler居然不使用标准logging模块，TMD。
#     def log_message(self, format, *args):
#         self.logger.debug("%s - - [%s] %s" %
#                           (self.client_address[0],
#                            self.log_date_time_string(),
#                            format % args))
#
#
# class DataCenterRPCServer(ThreadingMixIn, SimpleXMLRPCServer): pass


# import time
# from datetime import datetime


# def timestamp(dt=datetime.now()):
#     time.mktime(datetime.now().timetuple())


# def get_date_range(self, date_range='~'):
#     begin, end = date_range.split('~')
#     begin = begin or '1990/1/1'
#     end = end or datetime.now()
#     return begin, end


def dbc_to_sbc(ustring):
    """把字符串全角转半角"""
    rstring = ""
    for uchar in ustring:
        inside_code = ord(uchar)
        if inside_code == 0x3000:
            inside_code = 0x0020
        else:
            inside_code -= 0xfee0
        if inside_code < 0x0020 or inside_code > 0x7e:  # 转完之后不是半角字符返回原来的字符
            rstring += uchar
        else:
            rstring += unichr(inside_code)
    return rstring


def group_list(lst, block):
    """把一个列表分组

    :param lst: 列表。
    :param block: 每组的个数。
    :return: :rtype:
    """
    size = len(lst)
    return [lst[i:i + block] for i in range(0, size, block)]
