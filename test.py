#!/usr/bin/env python
# -*- coding:utf-8 -*-

# Copyright (c) 2015 yu.liu <showmove@qq.com>
# All rights reserved


if __name__ == '__main__':

    a = "3223402392800"
    # for item in a[1:]:
    keys = []
    for i in range(1, len(a) + 1, 2):
        #print i#
        if a[1:i] != '00' and a[1:i] != '':
            keys.append(
                'Key' + a[0] + a[1:i] + '0' * (len(a) - 1 - len(a[1:i])))
    for item in keys:
        print item
