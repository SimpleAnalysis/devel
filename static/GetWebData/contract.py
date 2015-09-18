#!/usr/bin/python
# -*- coding:utf-8 -*-

# Copyright (c) 2015 yu.liu <showmove@qq.com>
# All rights reserved

# pylint: disable-all

"""一个操作案列

"""

#$Id$
__author__ = [
    'liuyu <showmove@qq.com>',
]
__version__ = '$Revision: 0.1 $'

from extend.WYCrawler import *

from model.orm.Sqlextend import *
from model.Loading import insert_database
import re
import random
import os


class Insert_Content(PageLoader):

    def parse(self, dummy_response, dummy_info):

        new = Basename()

        new.url = self.cur_url
        new.source_data = self.html
        new.add(new)
        # self.crawler.point.set_value(new)
        # self.crawler.point.insert()


class TianJingList(PageLoader):

    """
    天津事务所：分页
    """

    def parse(self, dummy_response, dummy_info):
        """
        parse:
        """
        urls = 'http://lg.tjsf.gov.cn/tianjinlawyermanager/justice/search/result.jsp?currentPage=%s'
        PageNumber = self.xhtml.execute('//div[@align="right"]')[0].to_text()
        PageNumber = re.findall('[0-9]+', PageNumber)[0]

        for Index in range(1, ((int(PageNumber) + 20) / 20) + 1):
            print urls % Index
            self.link_to("GET", urls % Index, TianJingContent)


class TianJingContent(PageLoader):

    """
    天津事务所：分页详情
    """

    def parse(self, dummy_response, dummy_info):
        """
        parse:
        """
        tbody = self.xhtml.execute('//table[@cellpadding="2"]')[0]
        for url in tbody.execute('//a[@target="_blank"]'):
            url = url._parser_content.get('href').replace(
                'show.jsp', 'showoffice.jsp')
            print 'http://lg.tjsf.gov.cn/tianjinlawyermanager/justice/search/%s' % url

            self.link_to("GET",
                         'http://lg.tjsf.gov.cn/tianjinlawyermanager/justice/search/%s' % url,
                         Insert_Content
                         )


class Get_Html(Crawler):

    encoding = 'gb2312'
    max_connections = 10
    timeout = 20
    point = insert_database('Sqlextend', tablename=Basename)
    do_not_retry_with_server_error_code = (500,)

    def run(self):

        self.network.add_request(
            "get",
            "http://lg.tjsf.gov.cn/tianjinlawyermanager/justice/search/result.jsp",
            Insert_Content, 1
        )
