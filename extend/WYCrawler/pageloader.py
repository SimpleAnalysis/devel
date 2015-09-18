#!/usr/bin/env python
# -*- coding:utf-8 -*-

# Copyright (c) 2013 DY.Feng <yyfeng88625@gmail.com>
# All rights reserved

# pylint:disable-all

"""页面加载类


"""

# $Id$
__author__ = [
    'DY.Feng <yyfeng88625@gmail.com>',
]
__version__ = '$Revision: 0.1 $'

import re
import chardet
import traceback

from utils import XPath
import HTMLParser
import logging
# from os.path import basename
import tempfile
import os
import codecs
import networkmanager

HTML_PARSER = HTMLParser.HTMLParser()


class PageLoader(object):

    """页面结构类"""
    _reg_html = re.compile(
        r"<meta.*?charset\s*=\s*[\"']?([A-Za-z-\d]+)["
        r"\"\s'/]",
        re.IGNORECASE | re.MULTILINE | re.DOTALL)

    def __new__(cls, *args, **kwargs):

        cls.logger = logging.getLogger(
            'Crawler.PageLoader.%s' % cls.__name__)
        return object.__new__(cls, *args, **kwargs)

    logger = logging.getLogger('Crawler.PageLoader')

    #: 页面编码
    encoding = 'inherit_crawler'

    @property
    def xhtml(self):
        """取出页面预编译的XPath。

        :return: :rtype:
        """

        # 把页面预编译XPath
        if self._xhtml is None:
            if self.html:
                self._xhtml = XPath(self.html)
            else:
                self.logger.warning(
                    'Page have not content.XPath will not compile. %s'
                    % self.cur_url)

        return self._xhtml

    def __init__(self):

        self.info = None

        #: 页面内容，unicode。
        self.html = None

        #: 经过xpath预编译的页面。假如页面接收到的内容为空，则 `self.xhtml=None`。
        self._xhtml = None
        self.network = None

        #: 管理这个页面的爬虫类Crawler。
        self.crawler = None

        #: 这个页面一开始请求的url。
        self.begin_url = None

        #: 这个页面的url。
        self.cur_url = None

        #: 页面获取到的Cookie。
        self.cookies = None
        self.order = None
        self.response = None

    def _guess_encoding(self, response):
        """猜测页面编码.

        :param response: requests的响应包。
        :return: 页面编码.
        """

        # 如果有预设置页面编码则采用默认的
        if self.encoding:
            return self.encoding

        # TODO:去除多余代码，加快chardet猜测
        # 去除javascript代码
        # pageInfo['rawData'] = self.codeRegJavascript.sub('',
        # pageInfo['rawData'])
        # 去除xml代码
        # pageInfo['rawData'] = self.codeRegXMLHeader.sub('', pageInfo['rawData'])

        # 正则搜索页面编码
        result = PageLoader._reg_html.search(response.text)

        if not result:
            # 正则搜索不到则采用chardet猜测
            result = chardet.detect(response.content)
            # 可信度大于0.5
            if result['confidence'] >= 0.5:
                return result['encoding']
            else:
                return response.encoding
        else:
            return result.groups()[0]

    def _process_response(self, response, crawler, sender, info):
        """处理由Network类发过来的响应包.

        :param response: requests的响应包.
        :param crawler: 目前的爬虫类.
        :param info: 由上一级PageLoader传递下来的额外信息.
        """

        self.crawler = crawler
        if self.encoding == 'inherit_crawler':
            self.encoding = self.crawler.encoding
        self.network = crawler.network
        self.cur_url = response.url

        self.encoding = self.encoding or self._guess_encoding(response)

        # 设置编码
        response.encoding = self.encoding

        # 页面源码
        self.html = HTML_PARSER.unescape(response.text)

        try:
            self.parse(response, info)
        except Exception, err:
            receiver_class_name = self.crawler.__class__.__name__ + '.' + \
                self.__class__.__name__

            self.logger.error(
                '==================================================')
            self.logger.error('Page Loader:\t%s' % receiver_class_name)
            if sender:
                self.logger.error('Page Sender:\t%s:%s' %
                                  (sender.__class__.__name__,
                                   str(self.order))
                                  )
                self.logger.error('Sender Url:\t' + sender.cur_url)

                _fd, sender_name = tempfile.mkstemp(
                    dir=crawler.dump_dir,
                    prefix=sender.__class__.__name__ + '.',
                    suffix='.html')

                sender_file = open(sender_name, 'wb')

                sender_file.write(
                    sender.response.text.encode(
                        sender.response.encoding,
                        'ignore')
                )

                sender_file.close()
                os.close(_fd)

                self.logger.error('Dump Sender File:\t%s' % sender_name)

            self.logger.error('From Url:\t%s' % self.begin_url)

            # self.logger.error('Urls History:')
            #
            # for index, his in enumerate(response.history):
            #     self.logger.error('%s: %s' % (index, his.url))

            self.logger.error('End Url:\t%s' % response.url)

            _fd, receiver_name = tempfile.mkstemp(dir=crawler.dump_dir,
                                                  prefix=receiver_class_name +
                                                  '.',
                                                  suffix='.html')

            # receiver_name = receiver_class_name + '.html'
            receiver_file = codecs.open(receiver_name, 'w',
                                        encoding=response.encoding,
                                        errors='ignore')
            receiver_file.write(response.text)
            receiver_file.close()
            os.close(_fd)

            self.logger.error('Dump Receiver File:\t%s' % receiver_name)
            self.logger.error(traceback.format_exc())
            self.logger.error(
                '==================================================')

            self.crawler.on_parse_error(err)
            raise RuntimeWarning('Pageloader Parse Error.')

    # TODO:是不是该重构下,把response,info等去除,而改为类成员.
    #  不过这样的话,就决定了这个类是不可重入的.
    def parse(self, response, info):
        """解析响应包。

        :param response:
        :param info: 上个PageLoader传递下来的额外信息。
        :raise:
        """
        raise NotImplementedError

    def switch_proxy(self):
        try:
            old_proxy = self.response.connection.proxy_manager.keys()[0]
        except IndexError:
            old_proxy = None
        self.crawler.network.switch_proxy(old_proxy)

    def make_url(self, url):
        """根据本页面的base-url来重新拼装需要的url，例如相对路径变成绝对路径。

        :param url:
        :return: :rtype:
        """

        # TODO:如果url是u'http://www.66law.cn/lawyer/胡开梁律师/'，request还是能解析出来的,
        # 不要人为解码，否则url入库的时候会出现编码错误
        #
        # if isinstance(url, unicode):
        #     url = url.encode(self.encoding)

        return networkmanager.make_url(self.cur_url, url)

    def link_to(self, method, url, receiver, info=None, **kwargs):
        """向某个页面发去一个请求。

        :param method: POST or GET or PUT。
        :param url: 请求的url，支持相对路径。
        :param receiver: 接收数据的PageLoader。
        :param info: 额外传递的数据。
        :param params: GET方法参数，字典或者字符串。
        :param data: POST方法参数，字典或者字符串。
        :param headers: HTTP头，字典。
        :param cookies: 如果设置为None，则使用上个PageLoader传递下来的cookies，
                如果设置了，则覆盖此次请求，设置为{}则表明清空cookies。Dict或者CookieJar对象。
        :param files: (optional) Dictionary of 'filename': file-like-objects
            for multipart encoding upload.
        :param auth: (optional) Auth tuple or callable to enable
            Basic/Digest/Custom HTTP Auth.
        :param timeout: 定义请求超时秒数,可以覆盖全局超时秒数
        :param allow_redirects: (optional) Boolean. Set to True by default.
        :param proxies: (optional) Dictionary mapping protocol to the URL of
            the proxy.
        :param stream: (optional) whether to immediately download the response
            content. Defaults to ``False``.
        :param verify: (optional) if ``True``, the SSL cert will be verified.
            A CA_BUNDLE path can also be provided.
        :param cert: (optional) if String, path to ssl client cert file (.pem).
            If Tuple, ('cert', 'key') pair.

        """

        info = info or self.info

        # 把link_to所在的行数作为优先级,有点黑魔法，行数越小，优先级别越高
        order = traceback.extract_stack()[-2][1]

        url = url.strip().strip('#')

        # 设定来源
        kwargs['headers'] = kwargs.pop('headers', {})
        kwargs['headers']['Referer'] = kwargs[
            'headers'].pop('Referer', self.cur_url)

        if url:
            # 处理相对路径
            url = self.make_url(url)
            kwargs['cookies'] = kwargs.pop('cookies', self.cookies)

            self.network.add_request(method, url, receiver, order, self,
                                     info,
                                     **kwargs)
        else:
            self.logger.warning('Blank url.')

            # TODO:讨论使用boom还有没有意义

            # def duplicate_add(self, item, value):
            #     """
            #
            #     :param itme:
            #     :param value:
            #     """
            #     return self.crawler.duplicate_add(item, value)
            #
            # def duplicate_exist(self, item, value):
            #     """
            #
            #     :param itme:
            #     :param value:
            #     """
            #     return self.crawler.duplicate_exist(item, value)
