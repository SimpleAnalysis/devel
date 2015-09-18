#!/usr/bin/env python
# -*- coding:utf-8 -*-

# Copyright (c) 2015 yu.liu <showmove@qq.com>
# All rights reserved


"""代理配置文件

"""


PROXY = ['121.42.147.67', '115.28.132.254',
         '121.42.48.161', '115.28.167.14', '114.215.122.144']


def _remove_overdue(remove_ip=[]):
    """删除过期IP

    """
    for item in remove_ip:
        PROXY.remove(item)


def _add_proxy(proxy=[]):
    """新增加代理IP

    """
    PROXY.extend(proxy)


def Re_True_Proxy():

    _remove_overdue([])
    _add_proxy([])

    return PROXY
