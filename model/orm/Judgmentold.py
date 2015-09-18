#!/usr/bin/python
# -*- coding:utf-8 -*-

# Copyright (c) 2015 yu.liu <showmove@qq.com>
# All rights reserved

# pylint:disable-all


from SqlAcharModel import *

Base_to = declarative_base()


class ot_rawdata_judgement_court_gov_cn_old(JudgmentModel, Base_to):

    firm_name = Column(String(255))
    lawyer_name = Column(String(255))

    """
    http://www.court.gov.cn/zgcpwsw/ 中国裁判文书中间库

    """
