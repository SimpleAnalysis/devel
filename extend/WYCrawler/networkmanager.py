#!/usr/bin/env python
# _*_coding:utf-8_*_

# Copyright (c) 2013 DY.Feng <yyfeng88625@gmail.com>
# All rights reserved

# pylint:disable-all

"""网络流控制类


"""

# $Id$
# from requests.packages.urllib3.connectionpool import HTTPConnectionPool

__author__ = [
    'DY.Feng <yyfeng88625@gmail.com>',
]
__version__ = '$Revision: 0.1 $'

import requests
from gevent.queue import PriorityQueue, Empty
from gevent.lock import BoundedSemaphore, RLock
from gevent.pool import Group
import gevent
#

from requests.packages.urllib3.exceptions import MaxRetryError
import logging
from requests.exceptions import ConnectionError, Timeout

from requests.cookies import RequestsCookieJar, cookiejar_from_dict
from requests.compat import cookielib

from urlparse import urljoin, urlsplit, urlunsplit, parse_qs
from os.path import basename
import socket
import inspect

from Queue import Queue


# import httplib
# httplib.HTTPConnection.debuglevel = 5

class ServerErrorWithoutRetry(Exception):

    """这个服务器异常不进行重试"""


class TryAgain(Exception):

    """这个异常会导致重试。"""


class NoContent(TryAgain):

    """网络返回没内容。"""


class BreakenContent(TryAgain):

    """返回的内容是不全的（没有</html>）。"""


class ServerError(TryAgain):

    """服务器错误。"""


class NetworkManager(object):

    """网络控制类"""

    logger = logging.getLogger('Crawler.NetworkManager')

    def __init__(self, crawler):
        self._crawler = crawler
        self.proxy_pool = Queue()
        self._proxy_lock = RLock()
        max_connections = crawler.max_connections
        self._request_queue = PriorityQueue()
        self._request_semaphore = BoundedSemaphore(max_connections)

    def join(self):
        """等待队列里面的请求发送完成"""
        while not self._request_queue.empty():
            # self._process_request_from_queue()
            gevent.sleep(5)

    def request(self, method, url, **kwargs):
        """阻塞请求一个url。

        :param method:
        :param url:
        :param kwargs: 同add_request
        :return: :rtype: :raise err:
        """

        # 构造默认HTTP头
        default_header = {
            'Accept': self._crawler.accept_mine,
            'Accept-Language': self._crawler.accept_language,
            'User-Agent': self._crawler.user_agent,
            'Connection': 'keep-alive',
            'Accept-Encoding': 'gzip, deflate'
        }

        # 如果没有设置headers就使用全局设置
        kwargs['headers'] = kwargs.pop('headers', {})
        default_header.update(kwargs['headers'])
        kwargs['headers'] = default_header

        # 如果没有设置timeout就使用全局设置
        kwargs['timeout'] = kwargs.pop('timeout',
                                       self._crawler.timeout)

        session = requests.Session()
        session.max_redirects = self._crawler.max_redirects

        kwargs['cookies'] = kwargs.pop('cookies', {})

        # 设置代理
        kwargs['proxies'] = kwargs.pop('proxies', self._crawler.proxies)

        try_times = 0

        while try_times <= self._crawler.max_retries:
            try_times += 1
            try:
                self.logger.debug('[%s]>> %s' % (method.upper(), url))
                response = session.request(method, url, **kwargs)

                if self._crawler.retry_with_no_content and not response.content:
                    self.logger.warning('Page have no content.')
                    raise NoContent

                if self._crawler.retry_with_broken_content and '</html>' not in response.content:
                    self.logger.warning('Page content has been breaken.')
                    raise BreakenContent

                if response.status_code in self._crawler.do_not_retry_with_server_error_code:
                    self.logger.warning(
                        'Something wrong with server,but we DO NOT retry with it.')
                    raise ServerErrorWithoutRetry(
                        'Error Code:%s' % response.status_code)

                # 遇到非200错误
                if response.status_code != 200 and response.status_code not in self._crawler.ignore_server_error_code:
                    self._crawler.on_server_error(response)

                    # self.logger.warning('Something wrong with server.')
                    # raise ServerError, 'Error Code:%s' % response.status_code

            except (ConnectionError, Timeout, socket.timeout, socket.error, TryAgain,), err:
                # 好恶心的做法，代理发生错误居然没有特定的Exception
                if kwargs['proxies'] and any(
                        urlsplit(proxy).hostname in str(err.message) for proxy in kwargs['proxies'].values()):
                    # 代理有问题就切换呗
                    self.logger.debug(
                        'Proxy %s seems go down.', kwargs['proxies'])
                    self.switch_proxy(kwargs['proxies'].values()[0])

                    # self._crawler.on_proxies_error(kwargs['proxies'][0])

                # 如果发生重试异常和空白页异常的,就进行重试,否则把异常往上爆
                if isinstance(err, ConnectionError) and not isinstance(err.message, MaxRetryError):
                    raise err

                sleep_time = self._crawler.sleep_seconds * try_times

                self.logger.debug(err)

                self.logger.info('Try again with %s after %s '
                                 'seconds' % (url, sleep_time))

                gevent.sleep(sleep_time)
            except BaseException, err:
                # TODO:不知道是不是这里有捕获不了的gevent超时，稳定后删除。
                self.logger.error(type(err))
                self.logger.error(err)
            else:
                # 一切正常就跳出循环
                break
        else:
            # 超出最大重试次数,把最后一个异常(肯定是重试异常或者空白页面异常)向上爆
            raise err

        self.logger.debug('[%s]<< %s' % (method.upper(), url))

        merged_cookies = RequestsCookieJar()

        if not isinstance(kwargs['cookies'], cookielib.CookieJar):
            kwargs['cookies'] = cookiejar_from_dict(
                kwargs['cookies'])

        # 先更新旧的cookies
        response.cookies.update(kwargs['cookies'])

        # 再更新新的cookies，顺序不能乱
        merged_cookies.update(response.cookies)

        response.cookies = merged_cookies
        return response

    def switch_proxy(self, old_proxy=None):
        # 加锁，一个爬虫只能有一个协程在切换代理
        self.logger.debug('Try to switch proxy from %s.', old_proxy)
        with self._proxy_lock:

            # 不是你叫我切换代理我就会帮你切的，除非是你现在在用的代理跟现在设置的一样，
            # 否则有可能是其他线程已经切换过代理

            if old_proxy and old_proxy not in self._crawler.proxies.values():
                return

            while 1:
                try:
                    proxy = self.proxy_pool.get_nowait()
                    # 用之前先测试下能不能用，不能用的继续测试下一个
                    if self._crawler.test_proxy(proxy):
                        self._crawler.proxies = proxy
                        self.logger.info('Change network proxy as %s.', proxy)
                        break
                    else:
                        self.logger.debug(
                            'Old proxy %s does not work any more.Try another.', proxy)
                        continue
                except Empty:
                    # 代理队列里一个都不能用了，请求来些新代理吧
                    proxies = self._crawler.fetch_proxies()
                    self.logger.debug(
                        'Fetch %s proxies: %s', len(proxies), proxies)
                    for proxy in proxies:
                        self.proxy_pool.put(proxy)

    def test_proxy_with_keyword(self, url, keyword, proxy, **kwargs):
        self.logger.debug('Testing proxy: %s', proxy)
        try:
            return keyword in requests.get(url, proxies=proxy, timeout=self._crawler.timeout, **kwargs).content
        # except (ConnectionError, Timeout, socket.timeout, TryAgain):
        except Exception:
            return False

    def filter_available_proxies(self, proxies):
        _p = Group()
        results = _p.map(self._crawler.test_proxy, proxies)
        return [proxy for result, proxy in zip(results, proxies) if result]

    def _process_request_from_queue(self):
        """处理队列里面的请求"""

        if not self._request_queue.empty() and not self._crawler.stopped:
            if self._request_semaphore.acquire(blocking=False):
                # print len(self._crawler.pool),self._request_queue.qsize()
                order, receiver, method, url, sender, info, kwargs = \
                    self._request_queue.get()

                try:
                    response = self.request(method, url, **kwargs)

                    # TODO:要不要强制回收内存?
                    # import gc
                    # import objgraph
                    # 强制进行垃圾回收
                    # gc.collect()
                    # 打印出对象数目最多的 50 个类型信息
                    # objgraph.show_most_common_types(limit=50)

                    if inspect.isclass(receiver):
                        receiver = receiver()

                    receiver.cookies = response.cookies
                    receiver.order = order
                    receiver.response = response
                    receiver.begin_url = url

                    receiver._process_response(response, self._crawler,
                                               sender,
                                               info)

                    self.logger.debug('$$ ' + url)
                except (requests.exceptions.ConnectionError, requests.exceptions.HTTPError, ServerError), err:
                    self.logger.error(err)
                except ServerErrorWithoutRetry, err:
                    # 忽略这个异常
                    pass
                finally:
                    self._request_semaphore.release()
                    self._crawler.pool.spawn(
                        self._process_request_from_queue)
        gevent.sleep(0)

    def add_request(self, method, url, receiver, order, sender=None,
                    info=None,
                    **kwargs):
        """添加一个请求到队列.

        :param method: POST or GET or PUT.
        :param url: 请求的url,支持相对路径.
        :param receiver: 接收数据的PageLoader.
        :param order: 优先级,数字越小优先级越高.
        :param sender: 发送数据的PageLoader.
        :param info: 额外传递的数据.
        :param params: GET方法参数,字典或者字符串.
        :param data: POST方法参数,字典或者字符串.
        :param headers: HTTP头,会跟爬虫的默认HTTP头进行 *合并* ，字典.
        :param cookies: 如果设置为None,则使用上个PageLoader传递下来的cookies,
        如果设置了,则覆盖此次请求,设置为{}则表明清空cookies.Dict或者CookieJar对象.
        :param files: (optional) Dictionary of 'filename': file-like-objects
            for multipart encoding upload.
        :param auth: (optional) Auth tuple or callable to enable
            Basic/Digest/Custom HTTP Auth.
        :param 定义请求超时秒数,可以覆盖全局超时秒数
        :param allow_redirects: (optional) Boolean. Set to True by default.
        :param proxies: (optional) Dictionary mapping protocol to the URL of
            the proxy.
        :param stream: (optional) whether to immediately download the response
            content. Defaults to ``False``.
        :param verify: (optional) if ``True``, the SSL cert will be verified.
            A CA_BUNDLE path can also be provided.
        :param cert: (optional) if String, path to ssl client cert file (.pem).
            If Tuple, ('cert', 'key') pair.

        """

        if self._crawler.stopped:
            return

        url = url.strip()

        # 这里应该是request的一个小bug，如果data是字符串的话，POST请求头不会带有Content-Type: application/x-www-form-urlencoded
        if kwargs.get('data') and isinstance(kwargs['data'], basestring):
            kwargs['data'] = parse_qs(kwargs['data'])

        # while self._request_queue.qsize() > self._crawler.max_connections*3:
        # gevent.sleep(1)

        # 把请求加入队列
        self._request_queue.put(
            (order, receiver, method, url, sender, info,
             kwargs))

        self._crawler.pool.spawn(self._process_request_from_queue)


def make_url(base_url, url):
    """把相对地址扩展成完整地址。

    :param base_url: 相对地址所在的url。
    :param url: 相对地址。
    :return: 完整的地址。
    """
    url = urljoin(base_url, url)
    scheme, netloc, path, qs, anchor = urlsplit(url)
    return urlunsplit((scheme, netloc, path, qs, anchor))


def get_attachment(method, url, **kwargs):
    """下载附件并返回文件名和内容。

    :param method:
    :param url:
    :return: 元组，文件名，文件内容。
    """

    url = url.strip().strip('#')

    response = requests.request(method, url, **kwargs)
    filename = None

    # TODO:找不到这样的附件下载测试，所以也不知道正确与否
    # 根据http头的content-disposition获取文件名。
    if 'content-disposition' in response.headers:

        dispsition = [item.strip().lower() for item in response
                      .headers['content-disposition'].split(';')]

        dispsition = [x for x in dispsition if '=' in x]
        dispsition = [item.split('=', 1) for item in dispsition]

        dispsition = dict(
            (item[0].lower(), item[1].strip(r"\"").strip(r"'")) for item in dispsition)

        if 'filename' in dispsition:
            filename = dispsition['filename']

    if not filename:
        filename = basename(url)

    return filename, response.content
