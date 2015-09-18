#!/usr/bin/python
# -*- coding:utf-8 -*-

# Copyright (c) 2015 yu.liu <showmove@qq.com>
# All rights reserved

# pylint:disable-all


from SqlAcharModel import *

Base_to = declarative_base()


class ReplaceModel(BaseModel):

    """关联关键字模型

    """
    url = Column(String(1000), index=True, doc=u'这个资源的url')

    md5_identity = Column(BINARY(16), unique=True, index=True, doc=u'唯一标记')

    content = Column(MEDIUMTEXT, doc=u'正文内容，不包括署名', nullable=False)

    case_number = Column(String(200), doc=u'文书字号', nullable=False)

    JiebaKey = Column(String(200), doc=u'我们的关键词')

    itsKey = Column(String(200), doc=u'无讼关键词')

    __md5_columns__ = ('case_number',)


class ot_rawdata_judgement_court_gov_cn_old(JudgmentModel, Base_to):

    """
    http://www.court.gov.cn/zgcpwsw/ 中国裁判文书中间库

    """


class ot_rawdata_judgement_court_gov_cn(RawdataModel, EncryptModel, Base_to):

    """原始库
    http://www.court.gov.cn/zgcpwsw/ 中国裁判文书中间库

    """


class Replace(ReplaceModel, Base_to):

    """ 关键词对比库 """
