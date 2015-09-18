#!/usr/bin/python
# -*- coding:utf-8 -*-

# Copyright (c) 2015 yu.liu <showmove@qq.com>
# All rights reserved

# pylint:disable-all


from SqlAcharModel import *

Base_to = declarative_base()


class test_old(JudgmentModel, Base_to):

    """
    http://www.court.gov.cn/zgcpwsw/ 中国裁判文书中间库
    """
    __md5_columns__ = ('case_number', 'department', )

    __encrypt_columns__ = ('url', 'content', 'content_all', 'referer',)


class SearchName(BaseModel, Base_to):

    name = Column(String(255), doc="名称")


class Basename(RawdataModel, Base_to):

    """
       原始库
    """

    @classmethod
    @with_session
    def add(self, new=None, session=None):

        session.add(new)


class ot_baidu_search_info(BaseModel, Base_to):

    title = Column(String(255), doc="标题")
    url = Column(String(255), unique=True, doc="链接地址")
    key = Column(String(255), doc="关键词")
