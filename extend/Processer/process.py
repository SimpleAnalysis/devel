#!/usr/bin/env python
# -*- coding:utf-8 -*-

# Copyright (c) 2013 yu.liu <showmove@qq.com>
# All rights reserved


"""Analysis of data


"""

#: 载入数据库
from model.Loading import *

#: 载入配置
from configure import SourceToAnalysis

#: 载入线程模块
import threading

#: 载入QUEUE
from Queue import Queue

#: 试过使用线程池！如果小任务速度还行，但是大任务太占用内存
#: from multiprocessing import Pool, Process as MuPro, Lock
import sys


class Function_error(Exception):

    """ 用户定义方法调用出错

    """


class Function_does(AttributeError):

    """用户定义方法不存在

    """


class SqlQuery_TimeOut(OperationalError):

    """数据库搜索出现问题

    """


class Runing:

    """线程类

    """

    def __init__(self, data, func, point, from_data, to_data):
        """构造函数
        args:
            data = [{'name',[...],...}] 一个区分线程用的数据结构
            func = to_analysis    一个执行该分析的方法
            point = 从ORM中返回的模型SESSION
            from_data = 来源库
            to_data = 去往库
        returns:
            None
        """
        self.data = data
        self.job = Queue(maxsize=30)
        self.point = point
        self.func = func
        self.source = from_data
        self.to = to_data
        self.lock = threading.Lock()
        #self.lock = Lock()

    def __async_Runing__(self, pid, tablename):
        """执行线程中的任务

        """
        # print "Process = %s" % tablename
        #sys.stdout('Process = %s \n'% tablename)
        for item in self.source:
            if item.__name__ == tablename:
                self.point.set_tablename(tablename=item)
                # self.point.set_filter(filter = '%s <= id and id <= %s' % (rid[0], rid[1]), limit = None)
                # for pid in rid:

                self.point.set_filter(filter='id in %s' % repr(
                    tuple([int(i[0]) for i in pid])).replace(',)', ')'), limit=None)
                p = self.point.query()
                for old in p:
                    # print old.id, old.url
                    for todat in self.to:
                        try:
                            func = self.func[todat.__name__](old, todat)
                        except Function_error:
                            raise Function_error, 'Function error'
                        except Function_does:
                            raise Function_does, 'Not function'

    def queue_works(self, pid, item):
        """创建QUEUE 
           TODO：探讨是否使用线程锁？
           with self.lock:
                self.job.put()

        """
        with self.lock:
            #self.job.put(threading.Thread(target = self.__async_Runing__, args=( ((int(min(rid)[0])), int(max(rid)[0])), item)))
            # print pid
            self.job.put(
                threading.Thread(target=self.__async_Runing__, args=(pid, item)))

    def run(self):
        """运行函数

        """

        thread = []
        thread_num = 0
        for item in self.data:
            #pl = Pool(processes = 3)
            for rid in self.data[item]:
                #pl.apply_async(self.__async_Runing__, (rid, item))
                # for pid in rid:
                while True:
                    if not self.job.empty():
                        t = self.job.get()
                        t.start()
                        thread.append(t)
                        break
                    else:
                        self.queue_works(rid, item)
            # pl.close()
            # pl.join()

        for t in thread:
            t.join()

        #runtime = datetime.datetime.now() - time


class Process(object):

    """Process"""

    def __init__(self, dbname, **keyword):
        """load init

        """
        self._func = {}
        self.dbname = dbname
        self.keyword = keyword
        self.Analy = SourceToAnalysis()[dbname]
        self.point = query(dbname, filter='', limit=100)
        self.query_retry = 0
        self.max_query_retry = 10
        func_name = 'to_%s'
        if keyword.get('UPDATE') == True:
            if isinstance(self.Analy.get('Update'), dict):
                self.Analy = self.Analy['Update']
            else:
                self.Analy['From'] = self.Analy['To']
            func_name = 'to_update_%s'
        elif keyword.get('EDIT') == True:
            if isinstance(self.Analy.get('Edit'), dict):
                self.Analy = self.Analy['Edit']
            func_name = 'to_edit_%s'
        elif keyword.get('QUERY') == True:
            if isinstance(self.Analy.get('Query'), dict):
                sefl.Analy = self.Analy['Query']
            else:
                self.Analy['From'] = self.Analy['To']
            func_name = 'to_query_%s'
        for todat in self.Analy['To']:
            self._func[todat.__name__] = getattr(
                self, func_name % todat.__name__)

    def set_default_point(self):
        self.point = query(self.dbname, filter='', limit=100)

    def works(self):
        """Create work list 

        """
        count = {}
        index = {}
        for base in self.Analy['From']:
            count[base.__name__] = []
            index[base.__name__] = []
            # self.point.set_tablename(tablename=base.id)

            #import pdb
            # pdb.set_trace()
            if self.keyword.has_key('filter'):
                self.point.set_filter(self.keyword['filter'], limit=None)
            else:
                self.point.set_filter('', limit=None)
            self.point.session_status()
            try:
                result = self.point.session.execute(
                    'select id from %s where %s' % (base.__name__, self.keyword['filter'])).fetchall()
            except SqlQuery_TimeOut:
                self.point.session.close()
                if self.query_retry < self.max_query_retry:
                    time.sleep(1)
                    self.works()
                    self.query_retry += 1
                else:
                    raise OperationalError, "query time Out"

            self.query_retry = 0
            self.point.session.close()
            for item in result:  # self.point.query():
                count[base.__name__].append(item)

        for item in count:
            index[item].extend([count[item][i:i + 50]
                                for i in range(0, len(count[item]), 50)])

        return index

    def runing_works(self):

        data = self.works()
        if not data:
            return
        run = Runing(
            data, self._func, self.point, self.Analy['From'], self.Analy['To'])
        run.run()


if __name__ == '__main__':
    p = Process('Judgment', filter='id > 300 and id < 500')
    #i = p.works()
    result = p.runing_works()
