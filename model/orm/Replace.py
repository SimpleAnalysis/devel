#!/usr/bin/python
# -*- coding:utf-8 -*-

# Copyright (c) 2015 yu.liu <showmove@qq.com>
# All rights reserved

# pylint:disable-all


from SqlAcharModel import *

Base_to = declarative_base()




class JudgmentKeywordModel(BaseModel, EncryptModel):
    """关联关键字模型

    """
    url = Column(String(1000), index=True, doc=u'这个资源的url')
    
    referer = Column(String(1000), index=True, doc=u'这个资源的referer url')
    salt = Column(CHAR(4), doc=u'加密用key', nullable=False)
  
    title = Column(String(200), doc=u'标题')

    department = Column(String(200), doc=u'审理机构')
    # 文书名称
    case_type = Column(String(200), doc=u'文书名称')
    # 文书字号
    case_number = Column(String(200), doc=u'文书字号', nullable=False)
    
    keywords = Column(String(200), doc=u'关键词')

    judgementData = Column(String(200), doc= u'审判日期')

    judgment_id = Column(String(200), doc=u'文书ID')

    __md5_columns__ = ('case_number',)

    __encrypt_columns__ = ('url',)
    

class ot_judgment_keywords(JudgmentKeywordModel, Base_to):
    """裁判文书关键词库"""
    
class ot_judge_base(WarehouseModel, EncryptModel, Base_to):
    """判决书汇总表模型。

    """
    url = Column(String(1000), index=True, doc=u'这个资源的url')
    
    referer = Column(String(1000), index=True, doc=u'这个资源的referer url')
    
    content = Column(MEDIUMTEXT, doc=u'正文内容，不包括署名', nullable=False)

    content_md5 = Column(String(32), doc=u'正文内容md5', nullable=False)

    case_sign = Column(String(200), doc=u'文书署名', nullable=False)

    case_number = Column(String(200), doc=u'文书字号', nullable=False)
    
    keys = Column(String(255), doc=u'裁判文书关键词')
    
    __md5_columns__ = ('case_number',)

    __encrypt_columns__ = ('content', 'url')
    
    