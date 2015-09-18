#!/usr/bin/python
# -*- coding:utf-8 -*-

# Copyright (c) 2015 yu.liu <showmove@qq.com>
# All rights reserved

from extend.WYCrawler import PageLoader


class Beijing_details(PageLoader):

    """
        BeiJing firm details
    """

    def parse(self, dummy_response, dummy_info):
        """
            Parse:
        """
        keyword = {}
        head = self.xhtml.execute('//table[@class="over-work"]//th')
        text = self.xhtml.execute('//table[@class="over-work"]//td')
        content = dict(zip([i.to_text().strip() for i in head],
                           [k.to_text().strip() for k in text]
                           ))

        keyword['url'] = self.cur_url

        # keyword['Uid'] =

        keyword['cname'] = content[u'事务所中文全称']

        keyword['ename'] = content[u'事务所英文名称']

        keyword['area'] = content[u'所在区县']

        keyword['addr'] = content[u'事务所地址']

        keyword['zip'] = content[u'邮编']

        keyword['areaitem'] = content[u'事务所地址']

        keyword['just'] = content[u'主管司法局']

        keyword['number'] = ''

        keyword['startdate'] = ''

        keyword['people'] = content[u'律师事务所主任']

        keyword['branch'] = content[u'总所/分所']

        keyword['status'] = content[u'执业状态']

        keyword['explain'] = ''

        keyword['organization'] = content[u'组织形式']

        keyword['money'] = content[u'注册资金(万元)']

        keyword['phone'] = content[u'办公电话']

        keyword['fax'] = content[u'传真']

        keyword['email'] = content[u'E-mail']

        keyword['content'] = content[u'律所简介']

        keyword['prodate'] = 0

        keyword['index_url'] = content[u'事务所主页']

        keyword['create_time'] = ''

        keyword['mianji'] = content[u'场所面积(平米)']

        keyword['check_year'] = ''

        keyword['check_year_type'] = ''

        keyword['lawyers'] = ''

        self.crawler.put_datebase(keyword)


class BeiJing_Content(PageLoader):

    """
        BeiJing firm list
    """

    def parse(self, dummy_response, dummy_info):
        """
            Parse:
        """
        for item in self.xhtml.execute('//table[@class="sultable"]//tr//a/@href'):
            self.link_to(
                'GET', 'http://xkyw.bjsf.gov.cn' + item, Beijing_details)
