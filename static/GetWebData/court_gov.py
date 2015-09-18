#!/usr/bin/python
# -*- coding:utf-8 -*-

# Copyright (c) 2015 yu.liu <showmove@qq.com>
# All rights reserved

"""Get court_gov.cn book

1. New method get page
2. New method update page

"""

#$Id$
__author__ = [
    'liuyu <showmove@qq.com>',
]
__version__ = '$Revision: 0.1 $'

import re
import random
import os
import json
import time
import requests

from datetime import datetime, timedelta
from extend.WYCrawler import *
from model.orm.Judgment216 import ot_rawdata_judgement_court_gov_cn as ot_court_gov
from model.Loading import insert_database
from configure import PROXY
from model.orm.SqlAcharModel import md5_columns
from extend.exists import timeloop


class Request_Error(Exception):
    pass


class Content(PageLoader):

    """Storage referee instrument
    1. Download details page
    2. Put mysql server
    """

    def parse(self, dummy_response, dummy_info):
        """Detail page put database

        """
        print 'Download url = %s' % self.cur_url

        new = ot_court_gov()
        new.url = self.cur_url
        new.source_data = self.html
        self.crawler.point.set_value(new)
        self.crawler.point.insert()


class Content_details(PageLoader):

    """Analysis court_gov details, Download details url 
    1. Cheking url True or False
    2. Download False url 
    """

    def parse(self, dummy_response, dummy_info):
        """Details download

        """
        details = self.xhtml.execute(
            '//tr[@class="tdbgs_odd" or @class="tdbgs_even"]//td[3]//a/@href')
        try:
            index = re.findall('page=(\d+)', self.cur_url)[0]
            print '[Get] index = %s, url = %s' % (index, self.cur_url)
        except IndexError:
            pass
        # with open('Page_index.json', 'w') as Page_write:
        #    Page_write(json.dumps({'index': index}))

        for detail in details:
            #: link = "http://www.gy.yn.gov.cn" + detail
            #: print '[GET] url = %s' % detail
            #: Check if the UNICODE code is repeated, but there is a problem with the MD5.
            #: self.crawler.point.set_filter(filter = "md5_identity='%s'" % md5_columns(detail.encode('utf8'), 'utf8'))
            #: if self.crawler.point.query():
            #:      continue
            self.link_to("GET", detail, Content)
        page_write = file('Page_write', 'a')
        try:
            page_write.write(str(index) + '\n')
        except NameError:
            pass
        except TypeError:
            pass
        finally:
            page_write.close()


class Paging(PageLoader):

    """Page for the site
    1. Get max page
    2. From 1 to max page index
    """

    def parse(self, dummy_response, dummy_info):
        """Site page next page

        """
        #: with the get max page index
        index = re.search(u'共<strong>(\d+)</strong>页', self.html)
        if index:
            self.crawler.max_page = int(index.groups()[0])
        #: Next page download
        number = []
        # print "[GET] MAX_PAGE = %s " % self.crawler.max_page
        if os.path.exists('Page_index'):
            with open('Page_index', 'r') as load:
                number = load.readlines()
        for i in xrange(self.crawler.max_page):
            if i in number:
                continue
            self.link_to('GET',
                         self.crawler.url +
                         '&page=%d' % (i),
                         Content_details)


class Get_Html(Crawler):

    """Download court_gov book

    """
    encoding = 'utf8'
    max_page = 1008323
    max_connections = 10
    timeout = 20
    point = insert_database('Judgment', tablename=ot_court_gov)
    do_not_retry_with_server_error_code = (500,)
    url = "http://www.court.gov.cn/extension/search.htm?keyword=%s&beginDate=%s&endDate=%s" % (
        '%25%25%25%25', '2015-01-01', '2015-12-12')

    def run(self):

        self.proxy = self.fetch_proxies()[random.randint(0, len(PROXY) - 1)]
        self.network.add_request(
            "GET",
            self.url,
            Paging, 1
        )

    def on_server_error(self, response):
        """Server response Error 
        :param response:
        :raise ServerError:
        """
        print "Response Code Error: Code = %s" % (response.status_code)
        self.proxy = self.fetch_proxies()[random.randint(0, len(PROXY) - 1)]

    def fetch_proxies(self):
        """ Add new proxy ip """

        return [{'http': 'http:' + proxy + ':59274'}
                for proxy in PROXY]

    def test_proxy(self, proxy):
        """ Test proxy ip  """

        try:

            response = requests.get(self.url, proxies=proxy, timeout=30)
            if response.ok:
                return True
            else:
                return False

        except Request_Error:
            return False


class Get_Html_Up(Get_Html):

    """Update Download

    """
    #: Set url date
    #: start = datetime.now() + timedelta(days = -1)
    #: end   = datetime.now() + timedelta(days = 0)
    #: timeloop(start, end)
    #: days = -day
    #: returns ['start' ..... 'end']
    date = timeloop(datetime.now() + timedelta(days=-1))

    #: date[0] = startday , date[1] = endday
    url = "http://www.court.gov.cn/extension/search.htm?keyword=%s&beginDate=%s&endDate=%s" % (
        '%25%25%25', date[0], date[-1])
