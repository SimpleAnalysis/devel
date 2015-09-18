#!/usr/bin/python
# -*- coding:utf-8 -*-

# Copyright (c) 2015 yu.liu <showmove@qq.com>
# All rights reserved

from SqlAcharModel import *

Base_to = declarative_base()


class ot_rawdata_judgement_court_gov_cn_old(JudgmentModel, Base_to):

    """
    http://www.court.gov.cn/zgcpwsw/ 中国裁判文书中间库

    """
    firm_name = Column(String(255))
    lawyer_name = Column(String(255))


class ot_judge_search_extend_old(WarehouseModel, EncryptModel, Base_to):

    """判决书汇总表模型。

    """
    title = Column(String(200), doc=u'标题', nullable=False)

    content = Column(MEDIUMTEXT, doc=u'正文内容，不包括署名', nullable=False)

    content_md5 = Column(String(32), doc=u'正文内容md5', nullable=False)

    case_sign = Column(String(200), doc=u'文书署名', nullable=False)

    type = Column(String(100), doc=u'案例类型，民事/刑事/行政/其他', nullable=False)

    # 文书类型
    case_type = Column(String(200), doc=u'文书类型', nullable=False)

    case_type_id = Column(String(10), default='0', doc=u"文书类型id")

    # 文书字号
    case_number = Column(String(200), doc=u'文书字号', nullable=False)

    # 案由名称
    anyou = Column(String(200), doc=u'案由名称', nullable=False)

    # 案由id
    anyou_id = Column(BIGINT, doc=u'案由id', nullable=False)

    # 审理机构
    department = Column(String(200), doc=u'审理机构', nullable=False)

    # judges = Column(String(100), doc=u'审理法官,多个法官以 , 分隔', nullable=False)

    # 审判长
    chief_judge = Column(String(200), doc=u'审判长，中国是没有代理审判长的！')

    # 审判员
    judge = Column(String(200), doc=u'审判员')
    # 书记员
    clerk = Column(String(200), doc=u'书记员')

    # 代理审判员，可能有多个，以,分割
    acting_judges = Column(String(200), doc=u'代理审判员')

    plaintiff = Column(
        String(1200), doc=u'原告, 多个属性以:分隔，多个人以 ; 区分', nullable=False)

    plaintiff_lawyers = Column(
        String(1200), doc=u'原告律师, 格式:殷大丽:天津事务所;张志琳:天津事务所', nullable=False)

    defendant = Column(
        String(1200), doc=u'被告, 多个属性以:分隔，多个人以 ; 区分', nullable=False)

    defendant_lawyers = Column(
        String(1200), doc=u'被告律师, 格式:殷大丽:天津事务所;张志琳:天津事务所', nullable=False)

    # 审理程序
    procedure = Column(String(200), doc=u'审理程序')

    end_date = Column(Integer(), doc=u'裁判时间, 时间戳格式')

    # 地区id
    areacode = Column(Integer(), doc=u'地区编码')

    replace_data = Column(TEXT, doc=u'敏感数据替换')

    input_time = Column(Integer(), doc=u'进表时间')

    # 状态
    status = Column(Integer(), default=0, doc=u'状态', nullable=False)

    # 编辑状态
    base_check = Column(Integer(), default=0, doc=u'编辑状态', nullable=False)

    keys = Column(String(200), doc=u'关键词', default='', nullable=False)
    # md5一下文书字号,作为唯一标记
    __md5_columns__ = ('case_number', 'department')

    __encrypt_columns__ = ('content', 'url', 'referer')

    salt = Column(CHAR(4), doc=u'加密用key', nullable=False)
