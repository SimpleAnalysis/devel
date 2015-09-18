#!/usr/bin/python
# -*- coding:utf-8 -*-

# Copyright (c) 2015 yu.liu <showmove@qq.com>
# All rights reserved

# pylint:disable-all


from SqlAcharModel import *

Base_to = declarative_base()


class ot_process_error(BaseModel, Base_to):

    """汇总对比表 """
    judge_id = Column(Integer, doc=u"文书ID")
    action = Column(String(200), doc=u'动作')
    user_name = Column(String(200), doc=u'操作用户')
    error = Column(String(200), doc=u'错误信息')
    addtime = Column(String(200), doc=u'添加时间')
