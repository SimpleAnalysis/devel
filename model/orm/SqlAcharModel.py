#!/usr/bin/python
# -*- coding:utf-8 -*-

# Copyright (c) 2015 yu.liu <showmove@qq.com>
# All rights reserved

# pylint:disable-all


import re
import sqlalchemy
from sqlalchemy import create_engine
from sqlalchemy import Column
from sqlalchemy.types import CHAR, Integer, String
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
from sqlalchemy.ext.declarative import declared_attr, has_inherited_table
from sqlalchemy.orm.interfaces import MapperExtension
from sqlalchemy.orm import validates, relationship
from sqlalchemy.ext.compiler import compiles
from sqlalchemy.sql import expression
from sqlalchemy.event import listens_for, listen
from sqlalchemy import DDL
from sqlalchemy.exc import SQLAlchemyError, OperationalError
from sqlalchemy import *
from sqlalchemy.dialects.mysql import MEDIUMTEXT, MEDIUMBLOB
from datetime import datetime
from hashlib import md5
import string
import random

from ..Loading import returns_session
from functools import wraps


def with_session(func):

    @wraps(func)
    def wappr(self, new, **kwargs):

        module = new.__module__.split('.')[-1]
        import pdb
        pdb.set_trace()
        Session = returns_session(module)
        result = None
        session = Session()
        try:
            result = func(self, new, session=session)
            session.commit()

        except SQLAlchemyError, err:
            self.logger.error(err.message)
            session.rollback()
        finally:
            session.close()

        return result

        # return result

    return wappr


try:
    from NewProject.extend.utils.rpc import Client
except ImportError:
    from extend.utils.rpc import Client

client = Client('http://192.168.3.235:12082/bee/RPC')


class MediumPickle(PickleType):

    """MEDIUMBLOB字段类型。

    """
    impl = MEDIUMBLOB


class BaseModel(object):

    """最基础的sqlalchemy ORM模型，需要id字段，表名称规范。
    """
    id = Column(Integer, primary_key=True, autoincrement=True)

    @declared_attr
    def __tablename__(cls):
        s1 = re.sub('(.)([A-Z][a-z]+)', r'\1_\2', cls.__name__)
        return re.sub('([a-z0-9])([A-Z])', r'\1_\2', s1).lower()


class EncryptModel(object):

    """加密用模型。

    """
    salt = Column(CHAR(4), doc=u'加密用key', nullable=False)
    __encrypt_columns__ = ('url', )

    @staticmethod
    def _on_init(target, args, kwargs):
        target.salt = ''.join(random.sample(string.ascii_letters, 4))

    @staticmethod
    def _on_load(target, context):
        if target.id:
            for col in target.__encrypt_columns__:
                setattr(target, col, client.call(
                    'AesService.aesDecrypt', getattr(target, col), target.salt))

    @staticmethod
    def _before_change(mapper, connection, target):
        for col in target.__encrypt_columns__:
            setattr(target, col, client.call(
                'AesService.aesEncrypt', getattr(target, col), target.salt))

    @classmethod
    def __declare_first__(cls):
        listen(cls, 'load', cls._on_load)
        listen(cls, 'init', cls._on_init)
        listen(cls, 'before_update', cls._before_change)
        listen(cls, 'before_insert', cls._before_change)


def md5_columns(columns, encoding):
    try:
        return md5(u''.join([u'%s ' % unicode(column) for column in columns]).encode(encoding)).digest()
    except:
        return md5(u''.join([u'%s ' % column.decode(encoding) for column in columns]).encode(encoding)).digest()


class WarehouseExtension(MapperExtension):

    """仓库表扩展，负责数据清洗等。

    """
    #logger = logging.getLogger('DataCenter.WarehouseExtension')

    def _before_change(self, mapper, connection, instance):
        """数据库改变前。
        """

        def _strip_string(mapper, dummy_connection, instance):
            """清洗字符串."""
            charset = 'utf8'

            for prop in mapper.iterate_properties:
                if isinstance(prop, sqlalchemy.orm.ColumnProperty):
                    key = prop.key
                    attr = getattr(instance, key)

                    # 把原本是date类型字段却赋值为datetime的错误自动修正。
                    if isinstance(prop.columns[0].type, sqlalchemy.Date) and \
                            isinstance(attr, datetime):
                        setattr(instance, key, attr.date())

                    if isinstance(attr, unicode):
                        attr = attr.encode(charset, 'ignore').decode(
                            charset)
                        setattr(instance, key, attr.strip())
                    elif isinstance(attr, basestring):
                        setattr(instance, key, attr.strip())

        instance.update_datetime = datetime.now()
        _strip_string(mapper, connection, instance)
        # 取出需要hash的字段

        if instance.__md5_columns__:
            # 先对md5 columns排序，防止人为失误，顺序不同而导致md5不一样
            values = filter(None, [getattr(instance, col) for col in
                                   sorted(instance.__md5_columns__)])

            # 检查需要md5签名的字段是否为None
            for col in instance.__md5_columns__:
                if getattr(instance, col) is None:
                    self.logger.error('Field `%s` is None as md5 columns where parent_id=%s' %
                                      (col, instance.parent_id)
                                      )

            if values:
               # 把字段值用空格连接再hash
                instance.md5_identity = md5_columns(values, 'utf8')

    def before_update(self, mapper, connection, instance):
        self._before_change(mapper, connection, instance)

    def before_insert(self, mapper, connection, instance):
        instance.insert_datetime = datetime.now()
        self._before_change(mapper, connection, instance)


class WarehouseModel(BaseModel):

    """数据仓库模型，数据中心所有数据表都是此模型。
    文字字段在入库前都会进行GBK字符过滤。

    """

    #logger = logging.getLogger('DataCenter.WarehouseModel')

    # 资源来源的url，注意并不是这个资源的url
    referer = Column(String(1000), index=True, doc=u'这个资源的referer url')

    # 资源的url
    url = Column(String(1000), index=True, doc=u'这个资源的url')

    # md5一下某些字段,作为唯一标记
    md5_identity = Column(BINARY(16), unique=True, index=True, doc=u'唯一标记')

    # 资源来源，eg:某个Crawler，某个Processer
    come_from = Column(String(250), index=True, doc=u'数据原始来源的父仓库')

    # 父仓库数据id
    parent_id = Column(Integer, index=True, doc=u'父仓库数据id')

    update_datetime = Column(TIMESTAMP, index=True, doc=u'数据更新时间')

    insert_datetime = Column(TIMESTAMP, index=True, doc=u'数据插入时间')

    __mapper_args__ = {'always_refresh': False,
                       'extension': WarehouseExtension(),
                       }

    __md5_columns__ = None

    def __init__(self, come_from_cls=None):
        """初始化仓库模型。

        :param come_from_cls: 数据来至哪个类？
        """

        if come_from_cls:
            self.come_from = come_from_cls.__name__


class RawdataModel(WarehouseModel):

    """原始数据表模型。

    """
    __md5_columns__ = ('url', )
    source_data = Column(MEDIUMTEXT, doc=u'网页源码内容')
    __encrypt_columns__ = ('url', 'source_data',)


class JudgmentModel(WarehouseModel, EncryptModel):

    """判决书模型。
    """
    salt = Column(CHAR(4), doc=u'加密用key', nullable=False)

    title = Column(String(200))

    # 审理机构
    department = Column(String(200), doc=u'审理机构')

    # 案件类别
    # case_type = Column(String(200), doc=u'案件类别,刑事,民事,行政,知产,执行,海事,国赔,其它')
    #
    # 文书类型
    # doc_type = Column(String(200), doc=u'文书类型,判决书,调解书,裁定书,裁决书,建议书,决定书,通知书,支付令,其它文书')

    # 文书名称
    case_type = Column(String(200), doc=u'文书名称')

    # 文书字号
    case_number = Column(String(200), doc=u'文书字号', nullable=False)

    # 案由名称
    # cause_of_action = Column(String(200), doc=u'案由名称', nullable=False)

    # 审理程序
    procedure = Column(String(200), doc=u'审理程序,一审,二审,破产,其他,申诉,再审,减刑假释')

    # 审判长
    chief_judge = Column(String(200), doc=u'审判长，中国是没有代理审判长的！')

    # 审判员
    judge = Column(String(200), doc=u'审判员')

    # 代理审判员，可能有多个，以,分割
    acting_judges = Column(String(200), doc=u'代理审判员')

    # 人民陪审员

    # 书记员
    clerk = Column(String(200), doc=u'书记员')

    # 审结日期
    end_date = Column(Date, doc=u'审结日期')

    replace_data = Column(MediumPickle, doc=u'敏感数据替换')

    # 当事人属性 原告/被告
    # {
    #     u'原告':[('张三','个人','男')],
    #     u'被告':[('万有集团','机构','')]
    # }
    clients_attr = Column(MediumPickle)

    # 律师属性 原告/被告
    # {
    #     u'原告':[('李叫云', '广东义法律师事务所')],
    #     u'被告':[('蒋武君','邵阳县联合法律服务所')]
    # }
    lawyers_attr = Column(MediumPickle)

    content_all = Column(MEDIUMTEXT, doc=u'全文内容包括署名，可能包括法院文书字号等')

    content = Column(MEDIUMTEXT, doc=u'正文内容，不包括署名')

    case_sign = Column(String(200), doc=u'文书署名')

    # md5一下文书字号,作为唯一标记
    __md5_columns__ = ('department', 'case_number',)

    __encrypt_columns__ = ('url', 'content', 'content_all', 'referer',)
