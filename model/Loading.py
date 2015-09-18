#!/usr/bin/python
# -*- coding:utf-8 -*-

# Copyright (c) 2015 yu.liu <showmove@qq.com>
# All rights reserved

# pylint:disable-all

import time
try:
    from NewProject.configure import Config, Configuretion
except ImportError:
    from configure import Config, Configuretion

from orm.SqlAcharModel import SQLAlchemyError, OperationalError
from sqlalchemy.sql import func, select


def init_db(dbname=None):
    """"Initialization database """
    if dbname != None:
        exec('from orm.' + dbname + ' import create_engine, Base_to')
        engine = create_engine(Configuretion(dbname),
                               encoding=Config[dbname]['encoding'], echo=Config[dbname]['echo'])
        Base_to.metadata.create_all(engine)
    else:
        for item in Config:
            exec('from orm.' + item + ' import create_engine, Base_to')
            engine = create_engine(Configuretion(item),
                                   encoding=Config[item]['encoding'], echo=Config[item]['echo'])
            Base_to.metadata.create_all(engine)


class Opration(object):

    "Operation database"

    def __init__(self, session, **keyword):
        "Initialization "
        self.Session_load = session
        self.keyword = keyword

        #: Set query max retry count
        self.max_retry_time = 3

        #: Set query retry count
        self.retry = 0

        if keyword.has_key('editor'):
            self.set_value(keyword['editor'])
        else:
            self.editor = ''

    def session_status(self):
        "reload session"
        self.session = self.Session_load()

    def query(self):
        """Select table data

        args
            None
        returns
            yield data

        """
        self.session_status()
        try:
            if self.keyword['limit'] == None:
                query = self.session.query(self.keyword['tablename']).filter(
                    self.keyword['filter']).all()
            else:
                query = self.session.query(self.keyword['tablename']).filter(
                    self.keyword['filter']).limit(self.keyword['limit']).all()
        except OperationalError:
            self.retry += 1
            if self.retry > self.max_retry_time:
                raise OperationalError, 'RETRY OUT'
            time.sleep(3)
            self.session.close()
            self.query()

        self.session.close()

        if not query:
            return []
        self.retry = 0
        return query

    def set_value(self, value):
        "Set the update condition"
        self.editor = value

    def set_filter(self, filter=None, limit=500):
        "Set the search condition"
        self.keyword['filter'] = filter
        self.keyword['limit'] = limit

    def set_tablename(self, tablename):
        "Set the tablename"
        self.keyword['tablename'] = tablename

    def insert(self):
        "insert data"
        self.session_status()

        if self.editor == '':

            print 'Not insert data'
            return

        to = self.editor
        #to.name = 'test'
        self.session.add(to)
        try:
            self.session.commit()
        except SQLAlchemyError, err:
            print err[0:10]
        finally:
            self.session.close()

    def update(self):
        "update data"
        self.session_status()
        to = self.editor
        #to.name = 'test'
        self.session.merge(to)
        try:
            self.session.commit()

        except SQLAlchemyError, err:
            print err.message
            return err.orig.args[0]

        except TypeError, err:
            print err[0:10]

        finally:
            self.session.close()

    def delete(self):
        "Delete Data"

        self.session_status()
        self.session.query(self.keyword['tablename']).filter(
            self.keyword['filter']).delete(synchronize_session=False)
        try:
            self.session.commit()
        except SQLAlchemyError, err:
            print err[0:10]

        except TypeError, err:
            print err[0:10]

        finally:
            self.session.close()

    def Size(self):
        """Return min(id) and max(id)

        """
        self.session_status()
        to = self.keyword['tablename']
        try:
            result = self.session.query(
                func.min(to.id), func.max(to.id)).first()
        except:
            raise Exception, 'Not table %s, keyword = id' % to.__name__
        self.session.close()
        # if not result:
        return result
        # self.session.execute(select())


def insert_database(dbname, **keyword):
    """Insert data
    args 

         dbname 
         tablename = < 插入数据表名 >
         tablename.tabledata = < 新增的数据内容 >

    retures 

         point <Class Opration>

    """
    to_Session = returns_session(dbname)
    point = Opration(to_Session, **keyword)
    return point


def query(dbname, **keyword):
    """Search data
    args 

         dbname = < 数据库名称 >
         filter = <搜索条件>
         tablename = <表名称>
         limit = <显示行数>         
    retures 
         point <Class Opration>

    """

    to_Session = returns_session(dbname)
    point = Opration(to_Session, **keyword)
    return point


def returns_session(dbname):
    from orm.Judgment import sessionmaker, create_engine

    engine = create_engine(Configuretion(dbname),
                           pool_size=20, max_overflow=100,
                           encoding=Config[dbname]['encoding'], echo=Config[dbname]['echo'])
    to_Session = sessionmaker(expire_on_commit=False)
    to_Session.configure(bind=engine)

    return to_Session

if __name__ == '__main__':
    init_db()
    from orm.Sqlextend import SearchName, sessionmaker, Base_to, create_engine
    item = 'Sqlextend'
    engine = create_engine(Configuretion(
        item), encoding=Config[item]['encoding'], echo=Config[item]['echo'])

    to_Session = sessionmaker(expire_on_commit=False)
    to_Session.configure(bind=engine)
    #t_session = to_Session()
    insert = SearchName()
    point = Opration(to_Session, editor=insert, tablename=SearchName,
                     filter='name != ""', limit=10)

    for item in ['test12222', 'test23333', 'test32222', 'test']:
        insert.name = item
        point.set_value(insert)
        point.update()

    for item in point.query():
        insert.id = item.id
        insert.name = item.name
        point.set_value(insert)
        point.update
        print item.name
