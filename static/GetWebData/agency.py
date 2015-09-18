#!/usr/bin/python
# -*- coding:utf-8 -*-

# Copyright (c) 2015 yu.liu <showmove@qq.com>
# All rights reserved

"""Get Lawyer_firm 

1. New method get page
2. New method update page

"""

#$Id$
__author__ = [
    'liuyu <showmove@qq.com>',
]
__version__ = '$Revision: 0.1 $'


from extend.WYCrawler import *
from agency_function import *
from model.Loading import insert_database
from model.orm.Agency import ot_agency_old


class Get_Html(Crawler):

    encoding = 'utf8'
    max_connections = 10
    timeout = 20
    point = insert_database('Agency', tablename=ot_agency_old)
    do_not_retry_with_server_error_code = (500,)

    def run(self):

        self.network.add_request(
            "get",
            "http://xkyw.bjsf.gov.cn/lawofficeaction.do?method=queryService&chaxun=lvsuocx&loname=%25&page.currentPage=1&page.totalPerPage=2090",
            BeiJing_Content, 1
        )

    def put_datebase(self, keyword):
        """ Insert new data to ot_agency_old

        """
        to = ot_agency_old(Get_Html)

        to.url = keyword['url']

        # to.Uid = keyword['Uid']

        to.cname = keyword['cname']

        to.ename = keyword['ename']

        to.area = keyword['area']

        to.addr = keyword['addr']

        to.Zip = keyword['zip']

        to.areaitem = keyword['areaitem']

        to.just = keyword['just']

        to.number = keyword['number']

        to.startdate = keyword['startdate']

        to.people = keyword['people']

        to.branch = keyword['branch']

        to.status = keyword['status']

        to.explain = keyword['explain']

        to.organization = keyword['organization']

        to.money = keyword['money']

        to.phone = keyword['phone']

        to.fax = keyword['fax']

        to.email = keyword['email']

        to.content = keyword['content']

        to.prodate = keyword['prodate']

        to.index_url = keyword['index_url']

        to.create_time = keyword['create_time']

        to.mianji = keyword['mianji']

        to.check_year = keyword['check_year']

        to.check_year_type = keyword['check_year_type']

        to.lawyers = keyword['lawyers']

        self.point.set_value(to)
        self.point.insert()
