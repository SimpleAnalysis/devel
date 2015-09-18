#!/usr/bin/env python
# _*_coding:utf-8_*_

# Copyright (c) 2013 DY.Feng <yyfeng88625@gmail.com>
# All rights reserved

# pylint:disable-all

"""定向爬虫主模块

"""

# $Id$
__author__ = [
    'DY.Feng <yyfeng88625@gmail.com>',
]
__version__ = '$Revision: 0.1 $'

from networkmanager import NetworkManager, ServerError
from gevent.pool import Pool
import logging
import logging.config
from configure import LOG_CONF
# from pybloomfilter import BloomFilter
from gevent.lock import RLock
import httplib
# LOG_CONF = {
# 'version': 1,
# 'formatters': {
# 'WYFormatter': {
# 'format': '%(asctime)s [%(levelname)s][%(name)s]'
#                       '[%(filename)s:%(lineno)d] %(message)s',
#         }
#     },
#     'handlers': {
#         'consoleHandler': {
#             'class': 'logging.StreamHandler',
#             'stream': 'ext://sys.stdout',
#             'formatter': 'WYFormatter',
#         },
#         'fileHandler': {
#             'level': 'ERROR',
#             'class': 'logging.FileHandler',
#             'filename': 'dump.log',
#             'formatter': 'WYFormatter',
#         },
#     },
#     'loggers': {
#         '': {
#             'handlers': ['consoleHandler', 'fileHandler'],
#             'level': 'ERROR',
#             'propagate': True
#         },
#         'Crawler': {},
#
#     },
# }
#
logging.config.dictConfig(LOG_CONF)


class Crawler(object):
    """定向爬虫类"""

    http_debuglevel = 0

    #: 预定义网页编码。
    encoding = None

    #: 设置User Agent，有时候模拟Google Bot会有事倍功半的效果。
    user_agent = 'Mozilla/5.0 (compatible; MSIE 9.0; Windows NT 6.1; Trident/5.0)'

    # 页面语言，有些网站会以这个为标记实现国际化
    accept_language = 'zh_CN'

    # 可接受的数据类型
    accept_mine = 'text/html,application/xhtml+xml,' \
                  'application/xml;q=0.9,*/*;q=0.8'

    #: 最大重定向次数，防止重定向陷阱。
    max_redirects = 20

    #: 每个爬虫的最大并发连接数。
    max_connections = 10

    #: 超时。
    timeout = 360

    #: 最大失败尝试次数。
    max_retries = 1000

    #: 每次尝试后递增休眠间隔。
    #: 例如 ``sleep_seconds = 2`` ,那么第一次连接失败会休眠2秒，第二次会休眠4秒，第三次会休眠6秒。
    sleep_seconds = 1

    #: Bloom容量
    bloom_capacity = 10000000

    #: Bloom预计错误率
    bloom_error_rate = 0.0001

    #: HTTP代理
    proxies = None

    #: 错误日志存放处
    dump_dir = 'dump/'
    is_stop = True
    stopped = False
    name = None

    retry_with_broken_content = False
    retry_with_no_content = False

    #: 如果服务器遇到这些error code，当做正常页面处理
    ignore_server_error_code = ()

    #: 如果服务器遇到这些error code，不进行重试，直接忽略掉
    do_not_retry_with_server_error_code = ()

    lock = None
    logger = logging.getLogger('Crawler')


    def __init__(self):
        httplib.HTTPConnection.debuglevel = self.http_debuglevel
        self.network = NetworkManager(crawler=self)

        self.pool = Pool()
        self.lock = RLock()
        self.bloom_filters = {}
        self.name = self.__class__.__name__
        self._status = {
            'process_count': 0,
            'is_stop': True,
            'run_seconds': 0,
            'crawler_name': self.name,
        }



        # def sync_bloom(self):

        #     """强行同步Bloom到文件"""

    #
    #     while not self.is_stop:
    #         for key in self.bloom_filters.keys():
    #             self.bloom_filters[key].sync()
    #         gevent.sleep(1)



    def work(self):
        """启动爬虫。"""

        if self.lock.acquire(blocking=False):
            self.logger.info('Starting crawler %s' % self.name)
            self.stopped = False
            self._status['is_stop'] = False
            self.pool.spawn(self.run)
            self.pool.join()
            self.network.join()
            self._status['is_stop'] = True
            self.logger.info('Finished crawler %s' % self.name)
            self.lock.release()

    def on_server_error(self, response):
        """服务器错误回调。

        :param response:
        :raise ServerError:
        """
        self.logger.warning('Something wrong with server.')
        raise ServerError('Error Code:%s' % response.status_code)


    def on_proxies_error(self, proxy):
        pass

    def on_parse_error(self, error):
        """页面分析错误回调

        :param error:
        """

    def fetch_proxies(self):
        pass

    def stop(self):
        """停止爬虫。


        """
        self.logger.info('Stopping crawler %s' % self.name)
        self.stopped = True
        while not self.network._request_queue.empty():
            self.network._request_queue.get()


    def status(self):
        """返回爬虫状态。


        :return: :rtype:
        """
        return self._status


    def run(self):
        """这里编写启动爬虫的工作。
        必须重载此函数,推倒第一块多米诺骨牌。

        """
        raise NotImplementedError

        # def join(self, timeout=None):
        #     """等待爬虫完成所有工作。
        #
        #     :param timeout: 当所有的网络任务都完成后，等待超时的秒数。
        #     """
        #
        #     self.network.join()
        #     # TODO:是否定时同步Bloom
        #     # g=gevent.spawn(self.sync_bloom)
        #     self.pool.join(timeout=timeout, raise_error=True)
        #     self.is_stop = True


        # def _get_bloom_filter(self, item):
        #     """获取Bloom过滤器。
        #
        #     :param item: 你自己定义的Bloom名称。
        #     :return:
        #     """
        #     if item not in self.bloom_filters:
        #         file_name = self.__class__.__name__ + '_' + item + '.dat'
        #         try:
        #             bloom = BloomFilter.open(file_name)
        #         except OSError:
        #             bloom = BloomFilter(
        #                 self.bloom_capacity,
        #                 self.bloom_error_rate,
        #                 file_name,
        #             )
        #
        #         self.bloom_filters[item] = bloom
        #
        #     return self.bloom_filters[item]


        # TODO:讨论使用boom还有没有意义

        # def duplicate_add(self, item, value):
        #     """把数据项添加到Bloom。
        #
        #     :param item: 你自己定义的Bloom名称。
        #     :param value: 数据值，可以是任意类型。
        #     :return: 如果数据项已经在Bloom里则返回True，否则返回False。
        #     """
        #     bloom = self._get_bloom_filter(item)
        #     return bloom.add(value)
        #
        # def duplicate_exist(self, item, value):
        #     """测试数据项是否在Bloom里。
        #
        #     :param itme: 你自己定义的Bloom名称。
        #     :param value: 数据值，可以是任意类型。
        #     :return: 有则返回True，否则返回False。
        #     """
        #     bloom = self._get_bloom_filter(item)
        #     return value in bloom


