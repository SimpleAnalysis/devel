#!/usr/bin/python
# -*- coding:utf-8 -*-

# Copyright (c) 2015 yu.liu <showmove@qq.com>
# All rights reserved

# pylint:disable-all


from SqlAcharModel import *

Base_to = declarative_base()


class ot_judgment_diffed(BaseModel, Base_to):

    """汇总对比表 """
    judgmentid = Column(Integer(), unique=True, index=True, doc='文书ID')
    url = Column(String(200), doc=u'url地址', nullable=False)

    plaintiff = Column(Text, doc='原告信息')
    plaintiff_lawyers = Column(
        Text, doc=u'原告律师, 格式:殷大丽:天津事务所;张志琳:天津事务所', nullable=False)
    defendant = Column(Text, doc=u'被告, 多个属性以:分隔，多个人以 ; 区分', nullable=False)
    defendant_lawyers = Column(
        Text, doc=u'被告律师, 格式:殷大丽:天津事务所;张志琳:天津事务所', nullable=False)

    header = Column(Text, doc=u'头部')
    firsthead = Column(Text, doc=u'台头')
    content = Column(Text, doc=u'内容')
    case_sign = Column(String(255), doc=u'文书署名', nullable=False)


class ot_rawdata_judgement_court_gov_cn_old(JudgmentModel, Base_to):

    """
    http://www.court.gov.cn/zgcpwsw/ 中国裁判文书中间库

    """


class ot_rawdata_judgment_openlaw_old(JudgmentModel, Base_to):

    """
     openlaw

    """
    __md5_columns__ = ('case_number',)

    __encrypt_columns__ = ('url', 'content', 'content_all', 'referer',)


class ot_judgment_inspection(BaseModel, Base_to):

    judgmentid = Column(Integer(), unique=True, index=True, doc='文书ID')

    plaintiff = Column(String(250), doc=u'原告', nullable=False)
    plaintiff_lawyers = Column(
        String(250), doc=u'原告律师, 格式:殷大丽:天津事务所;张志琳:天津事务所', nullable=False)
    defendant = Column(
        String(250), doc=u'被告, 多个属性以:分隔，多个人以 ; 区分', nullable=False)
    defendant_lawyers = Column(
        String(250), doc=u'被告律师, 格式:殷大丽:天津事务所;张志琳:天津事务所', nullable=False)
    case_sign = Column(String(200), doc=u'文书署名', nullable=False)
    case_type = Column(String(200), doc=u'文书类型', nullable=False)
    case_number = Column(String(200), doc=u'文书字号', nullable=False)
    department = Column(String(200), doc=u'审理机构', nullable=False)
    title = Column(String(200), doc=u'标题', nullable=False)
    firm = Column(String(200), doc=u'机构列表', nullable=False)


class ot_judge_inspection(BaseModel, Base_to):

    judgmentid = Column(Integer(), unique=True, index=True, doc='文书ID')

    #names = Column(TEXT, doc=u'名称信息')
    people = Column(TEXT, doc=u'被告 与 原告')

    lawyers = Column(TEXT, doc=u'被告律师与原告律师')

    firms = Column(TEXT, doc=u'律师事务所')

    case_sign = Column(String(200), doc=u'文书署名', nullable=False)


class ot_judge_analyze(BaseModel, Base_to):

    title = Column(String(200), doc=u'标题')
    court = Column(String(200), doc=u'法院')
    sn = Column(String(200), doc=u'文书字号')
    content = Column(TEXT, doc=u'内容')


class ot_judge_anyou(BaseModel, Base_to):

    """案由表

    """
    anyou_name = Column(String(200), doc=u'案由名称')


class ot_judge_anyou_old(BaseModel, Base_to):

    """旧案由表

    """
    new_id = Column(Integer, doc="新的案由ID")
    anyou_name = Column(String(200), doc=u'别名')


class ot_judge_base(WarehouseModel, EncryptModel, Base_to):

    """判决书汇总表模型。

    """
    content = Column(MEDIUMTEXT, default='', doc=u'正文内容，不包括署名', nullable=False)

    content_md5 = Column(String(32), default='', doc=u'正文内容md5', nullable=False)

    content_safe = Column(MEDIUMTEXT, default='',  doc=u'正文内容safe')

    content_all = Column(TEXT, doc=u'正文内容，包括署名')

    case_sign = Column(String(300), default='', doc=u'文书署名', nullable=False)

    type = Column(
        String(20), default='', doc=u'案例类型，民事/刑事/行政/其他', nullable=False)

    # 文书类型
    case_type = Column(String(20), default='', doc=u'文书类型', nullable=False)

    case_type_id = Column(String(10), default='0', doc=u"文书类型id")

    # 文书字号
    case_number = Column(String(200), default='0', doc=u'文书字号', nullable=False)

    title = Column(String(255), default='', doc=u'文书标题')

    # 案由名称
    anyou = Column(String(200), default='', doc=u'案由名称', nullable=False)

    # 案由id
    anyou_id = Column(BIGINT, default='0', doc=u'案由id', nullable=False)

    # 审理机构
    department = Column(String(200), default='', doc=u'审理机构', nullable=False)

    chief_judge = Column(String(50), default='', doc=u'审判长')

    judge = Column(String(100), default='', doc=u'审判员')

    acting_judges = Column(
        String(100), default='', doc=u'代理审判员,多个以 , 分隔', nullable=False)

    clerk = Column(String(100), default='', doc=u'书记员')

    judges_extends = Column(String(100), default='', doc=u'审理法官拓展数据')

    plaintiff = Column(
        String(1200), default='', doc=u'原告, 多个属性以:分隔，多个人以 ; 区分', nullable=False)

    plaintiff_lawyers = Column(
        String(1200), default='', doc=u'原告律师, 格式:殷大丽:天津事务所;张志琳:天津事务所', nullable=False)

    defendant = Column(
        String(1200), default='', doc=u'被告, 多个属性以:分隔，多个人以 ; 区分', nullable=False)

    defendant_lawyers = Column(
        String(1200), default='', doc=u'被告律师, 格式:殷大丽:天津事务所;张志琳:天津事务所', nullable=False)

    # 审理程序
    procedure = Column(String(200), default='', doc=u'审理程序')

    end_date = Column(Integer(), default='0', doc=u'裁判时间, 时间戳格式')

    # 地区id
    areacode = Column(Integer(), default='0', doc=u'地区编码')

    base_check = Column(Integer(), default='0', doc=u'基本数据确认, 0未确认, 1确认')

    replace_data = Column(TEXT, doc=u'敏感数据替换')

    #replace_check = Column(Integer(), default='0', doc=u'敏感数据确认, 0未确认, 1确认')

    #class_data = Column(TEXT, default='',  doc=u'分类数据')

    #class_check = Column(Integer(), default='0', doc=u'分类数据确认, 0未确认, 1确认')

    #other_data = Column(TEXT, default='', doc=u'其它综合数据')

    #other_check = Column(Integer(), default='0', doc=u'其它综合数据确认, 0未确认, 1确认')

    #version = Column(Integer(), default='0', doc=u'版本')

    #pre_version = Column(Integer, default='0', doc='上个版本')

    status = Column(Integer(), default='0', doc=u'文书状态, -1废弃, 0未处理, 1正式, 2处理中')

    remark = Column(String(250), default='', doc=u'描述')

    input_time = Column(Integer(), default='0', doc=u'添加时间')

    #base_edit_flag = Column(Integer(), default='0', doc=u'基本信息编辑标志')

    #replace_edit_flag = Column(Integer(), default='0', doc=u'敏感信息编辑标志')

    #class_edit_flag = Column(Integer(), default='0', doc=u'分类信息编辑标志')

    #other_edit_flag = Column(Integer(), default='0', doc=u'综合信息编辑标志')

    #audit_edit_flag = Column(Integer(), default='0', doc=u'审核入库编辑标志')

    come_from = Column(String(250), index=True, doc=u'来源')

    from_host = Column(String(50), default='', doc='来源域名')

    url = Column(String(1000), index=True, default='')

    parent_id = Column(Integer(), default='0')

    #from_rid2 = Column(Integer(), default='0', doc='来源对应id')

    referer = Column(String(1000), index=True)

    md5_identity = Column(BINARY(16), unique=True, index=True)

    update_datetime = Column(TIMESTAMP, index=True)

    insert_datetime = Column(TIMESTAMP, index=True)

    #_MASK_SYNC_V2 = Column(TIMESTAMP, doc=u'数据更新时间')

    salt = Column(CHAR(4), default='', doc=u'加密用key', nullable=False)

    #base_edit_author = Column(Integer(), default='0', doc=u'基本信息操作人')

    #replace_edit_author = Column(Integer(), default='0', doc=u'敏感信息操作人')

    #class_edit_author = Column(Integer(), default='0', doc=u'分类信息操作人')

    #other_edit_author = Column(Integer(), default='0', doc=u'综合信息操作人')

    #keys = Column(String(255), default='', doc=u'关键字')

    #lawyer_name = Column(String(255), doc=u'律师名称')

    #firm_name = Column(String(255), doc=u'律所名')

    # md5一下文书字号,作为唯一标记
    __md5_columns__ = ('case_number', 'department')

    __encrypt_columns__ = ('content', 'url', 'referer')
