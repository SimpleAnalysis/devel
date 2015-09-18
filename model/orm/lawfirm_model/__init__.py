#!/usr/bin/python
# -*- coding:utf-8 -*-

# Copyright (c) 2015 yu.liu <showmove@qq.com>
# All rights reserved

# pylint:disable-all

from ..SqlAcharModel import *
Base_to = declarative_base()


class agencydataModel(RawdataModel):

    """

        原始数据模型。

    """
    __encrypt_columns__ = ('url', 'referer')  # 'source_data', 'referer',)


class LawyerModel(WarehouseModel):

    """ 律师中间库模型

    """
    cname = Column(String(20), nullable=False, doc="中文名")

    oldname = Column(String(20), default='', doc="曾用名")

    birthdate = Column(Integer(), default='', doc="出生日期")

    birthdate_type = Column(Integer, default='', doc="生日类型(0公历,1农历)")

    sex = Column(Integer(), default='', doc="性别(0女1男)")

    photo = Column(String(255), default='', doc="免冠照片")

    marriage = Column(Integer(), default='', doc="婚姻情况(词典id)")

    school = Column(String(100), default='', doc="毕业学校")

    education = Column(String(20), default='', doc="最高学历")

    nation = Column(String(20), default='', doc="民族")

    zhengzhi = Column(String(20), default='', doc="政治面貌")

    addr = Column(String(200), default='', doc="通讯地址")

    areacode = Column(String(200), default='', doc="所在地区")

    tags = Column(String(255), default='', doc="标签")

    card = Column(String(100), default='', doc="职称")

    lawfirm = Column(String(200), default='', doc="所在律所")

    just = Column(String(200), default='', doc="主管机关")

    title_num = Column(String(100), default='', doc="资格证号")

    lawyer_code = Column(String(200), default='', doc="执业证号")

    title_date = Column(String(20), default='', doc="资格证获得日期")

    lawyer_date = Column(String(20), default='', doc="执业证获得日期")

    lawyer_status = Column(String(200), default='', doc="职业状态")

    lawyer_note = Column(String(200), default='', doc="状态说明")

    mobile = Column(String(20), default='', doc="常用手机")

    tel = Column(String(200), default='', doc="办公电话")

    fax = Column(String(200), default='', doc="传真")

    web_url = Column(String(255), default='', doc="微博地址")

    email = Column(String(200), default='', doc="邮箱")

    content = Column(String(255), default='', doc="简介")

    prodate = Column(String(200), default='', doc="上班时间")

    cname_lawfirm_lawyer_code = Column(
        String(255), default='', doc="名称+律所+执业证号(用于去从)")

    check_year = Column(Integer(), default='', doc="最后审核年份")

    check_year_type = Column(Integer(), default='', doc="年审是否及格 1：合格 2:不合格")

    __md5_columns__ = ('cname_lawfirm_lawyer_code',)


class agencyModel(WarehouseModel):

    """
        #事务所信息
        #ID，中文名,英文名,地区,详细地址,邮编,所属区县，主管司法局,执业证号,发证日期,事务所主任
        #, 总/分所, 职业状态, 状态说明, 组织形式, 注册资金, 办公电话, 传真, 邮箱, 简介 
        #__encrypt_columns__ = ('url', 'referer')#'source_data', 'referer',)
    """
    Uid = Column(String(200), default=0, doc='uid')

    index_url = Column(String(200), doc=u'官方网址')

    cname = Column(String(200), doc=u'中文名')

    ename = Column(String(200), doc=u'英文名')

    area = Column(String(200), doc=u'地区')

    addr = Column(String(200), doc=u'详细地址')

    Zip = Column(String(200), doc=u'邮编')

    areaitem = Column(String(200), doc=u'所属区县')

    just = Column(String(200), doc=u'主管司法局')

    number = Column(String(200), doc=u'执业证号')

    startdate = Column(String(200), doc=u'发证日期')

    people = Column(String(200), doc=u'事务所主任')

    branch = Column(String(200), doc=u'总/分所')

    status = Column(String(200), doc=u'职业状态')

    explain = Column(String(200), doc=u'状态说明')

    organization = Column(String(200), doc=u'组织形式')

    money = Column(String(200), doc=u'注册资金')

    phone = Column(String(200), doc=u'办公电话')

    fax = Column(String(200), doc=u'传真')

    email = Column(String(200), doc=u'邮箱')

    content = Column(String(255), doc=u'简介')

    prodate = Column(String(200), doc=u'工作时间')

    create_time = Column(String(200), doc=u'成立时间')

    mianji = Column(String(200), doc=u'面积')

    check_year = Column(Integer(), default=0, doc=u'年度考核')
    # 年份
    check_year_type = Column(Integer(), default=0, doc=u'年度考核ID')
    # 1.及格，2.不及格

    lawyers = Column(MEDIUMTEXT, doc="律师")

    __md5_columns__ = ('cname',)


class AgencyMainModel(WarehouseModel):

    referer = None
    # 资源的url
    url = None
    # md5一下某些字段,作为唯一标记
    md5_identity = None
    # 资源来源，eg:某个Crawler，某个Processer
    come_from = None
    # 父仓库数据id
    #parent_id = None
    update_datetime = None
    insert_datetime = None

    id = Column(Integer(), doc="ID", primary_key=True, autoincrement=True)

    # 名称
    name = Column(String(30), doc="名称")

    # 曾用名
    old_name = Column(String(30), doc="曾用名")

    # 机构类型
    a_type = Column(Integer(), doc="机构类型")

    # 地区编号
    areacode = Column(Integer())

    # 街道地址
    street = Column(String(100))

    # Email
    email = Column(String(50))

    # 联系电话
    tel = Column(String(30))

    tel400 = Column(String(30))
    # 投诉电话
    call = Column(String(30))

    # 传真
    fax = Column(String(30))

    # 官方网站
    url = Column(String(255))

    # 父机构ID
    pid = Column(Integer())

    # 律所云关联ID
    rid = Column(Integer())

    # 创建时间
    input_time = Column(Date)

    # 来源
    # from = Column(String(255))

    # ifaudit审核状态
    ifaudit = Column(Integer())

    # 审核人
    auditor = Column(String(20))

    # 审核时间
    audittime = Column(Integer())

    # 快车律所法院关联ID
    ltrid = Column(Integer())
    lsrid = Column(Integer())
    flrid = Column(Integer())

    __md5_columns__ = ('name',)


class AgencyInfoModel(WarehouseModel):

    '''
        -------------  ----------------  ---------------  ------  ------  -----------------  ------  -------------------------------  
        aid            int(11) unsigned  (NULL)           NO      PRI     (NULL)                      关联ot_agency_main.id    
        weibo          varchar(500)      gbk_chinese_ci   YES                                         微博,多个以","隔开  
        wx_dy_num      varchar(30)       gbk_chinese_ci   YES                                         微信订阅号            
        wx_dy_img      varchar(255)      gbk_chinese_ci   YES                                         微信订阅号二维码   
        wx_fw_num      varchar(30)       gbk_chinese_ci   YES                                         微信服务号            
        wx_fw_img      varchar(255)      gbk_chinese_ci   YES                                         微信服务号二维码   
        jianjie        text              gbk_chinese_ci   YES             (NULL)                      简介                     
        map_open       int(11)           (NULL)           NO              0                           地图功能开关         
        map_x          varchar(50)       utf8_general_ci  NO                                          地图x坐标              
        map_y          varchar(50)       utf8_general_ci  NO                                          地图y坐标              
        map_zoom       varchar(50)       utf8_general_ci  NO                                          地图位置               
        map_level      tinyint(4)        (NULL)           NO              0                           地图类别               
        traffic1       varchar(200)      utf8_general_ci  NO                                          交通路线(公车)       
        traffic2       varchar(200)      utf8_general_ci  NO                                          交通路线(地铁)       
        photo          varchar(200)      utf8_general_ci  NO                                          办公楼图片            
        officehours    varchar(100)      utf8_general_ci  NO                                          办公时间               
        memo           text              utf8_general_ci  YES             (NULL)                      备注                     
        input_time     int(11)           (NULL)           NO              (NULL)                      创建时间               
        _mask_sync_v2  timestamp         (NULL)           NO              CURRENT_TIMESTAMP           数据更新时间   

    '''
    id = None
    referer = None
    # 资源的url
    url = None
    # md5一下某些字段,作为唯一标记
    md5_identity = None
    # 资源来源，eg:某个Crawler，某个Processer
    come_from = None
    # 父仓库数据id
    parent_id = None
    update_datetime = None
    insert_datetime = None

    aid = Column(Integer(), doc="关联ID", primary_key=True)
    weibo = Column(String(500))
    wx_dy_num = Column(String(30))
    wx_dy_img = Column(String(255))
    wx_fw_num = Column(String(30))
    wx_fw_img = Column(String(255))
    jianjie = Column(MEDIUMTEXT)
    map_open = Column(String(50))
    map_x = Column(String(50))
    map_y = Column(String(50))
    map_zoom = Column(String(50))
    map_level = Column(Integer())
    traffic1 = Column(MEDIUMTEXT)
    traffic2 = Column(MEDIUMTEXT)
    photo = Column(String(255))
    officehours = Column(String(255))
    memo = Column(MEDIUMTEXT)
    input_time = Column(Integer())
    _mask_sync_v2 = Column(Date)


class AreaModel(RawdataModel):

    ''' 法院'''
    area = Column(String(200))
    addr = Column(String(200))
    Link = Column(String(200))


class AgencyLawfirmModel(WarehouseModel):

    id = None
    referer = None
    # 资源的url
    url = None
    # md5一下某些字段,作为唯一标记
    md5_identity = None
    # 资源来源，eg:某个Crawler，某个Processer
    come_from = None
    # 父仓库数据id
    parent_id = None
    update_datetime = None
    insert_datetime = None
    uid = Column(Integer(), doc="关联ID", primary_key=True)
    lawyer_code = Column(String(100), doc="执业证号")
    mianji = Column(String(30), doc="面积")
    nature = Column(Integer(), doc="组织形式")
    registered = Column(Integer(), doc="设立资产")
    registered_cn = Column(String(10), doc="设立资产(格式:万|##,单位:万(人民币,美元))")
    founding_time = Column(Integer(), doc="设立时间")
    scale = Column(Integer(), doc="人员规模")
    check_year = Column(Integer(), doc="年度考核年份(记录最新年份考核)")
    check_year_type = Column(Integer(), doc="年度考核结果(1及格,2不及格)")
    lawyer_code_img = Column(String(255), doc="执业证正面")
    check_year_img = Column(String(255), doc="年检页")
    fuwulingyu = Column(MEDIUMTEXT, doc="服务领域")
    zhuanyeyanjiu = Column(MEDIUMTEXT, doc="专业研究")
    input_time = Column(Integer(), doc="创建时间")
    _mask_sync_v2 = Column(Date, doc="数据更新时间")


class bdoldmodel(WarehouseModel):
    referer = None
    # 资源的url
    url = None
    # md5一下某些字段,作为唯一标记
    md5_identity = None
    # 资源来源，eg:某个Crawler，某个Processer
    come_from = None
    # 父仓库数据id
    parent_id = None
    update_datetime = None
    insert_datetime = None
    area = Column(String(200))
    name = Column(String(200))
    stee = Column(String(200))
    phone = Column(String(200))
