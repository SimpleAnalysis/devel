#!/usr/bin/env python
# -*- coding:utf-8 -*-

# Copyright (c) 2015 yu.liu <showmove@qq.com>
# All rights reserved

"""扩展模块


"""
from datetime import datetime, timedelta
from arrow import Arrow
# 设置时间列表函数


def timeloop(start=datetime.now() + timedelta(days=-1),
             end=datetime.now() + timedelta(days=0)):
    "生成一个字符串格式为YYYY-MM-DD形式的数组."
    if (type(start) is str) or (type(end) is str):
        start = start if type(
            start) is datetime else datetime.strptime(start, '%Y-%m-%d')
        end = datetime.now()
    # TODO:检查时间是否为字符串，如果是则转换为时间。

    rond = []
    for r_time in Arrow.range('day', start, end):
        rond.append(r_time.format('YYYY-MM-DD'))
    return rond


#: 成对括号匹配
def Dou_text(text):
    """匹配一对括号

    """
    data = []
    start = 0
    stop = 0
    for i in range(len(text)):
        if text[i] == u'（' or text[i] == '(':
            start = i
        if text[i] == u'）' or text[i] == ')':
            stop = i + 1

        if start and stop:
            data.append(text[start:stop])
            start = 0
            stop = 0
    return data
