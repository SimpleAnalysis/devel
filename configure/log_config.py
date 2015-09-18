#!/usr/bin/env python
# -*- coding:utf-8 -*-

# Copyright (c) 2015 yu.liu <showmove@qq.com>
# All rights reserved
"""日志配置文件

"""


def Crawler_log():
    """Crawler Configuration

    """
    LOG_CONF = {
        'version': 1,
        'formatters': {
            'WYFormatter': {
                'format': '%(asctime)s [%(levelname)s][%(name)s]'
                '[%(filename)s:%(lineno)d] %(message)s',
            }
        },
        'handlers': {
            'consoleHandler': {
                'class': 'logging.StreamHandler',
                'stream': 'ext://sys.stdout',
                'formatter': 'WYFormatter',
            },
            'fileHandler': {
                'level': 'ERROR',
                'class': 'logging.FileHandler',
                'filename': 'dump.log',
                'formatter': 'WYFormatter',
            },
        },
        'loggers': {
            '': {
                'handlers': ['consoleHandler', 'fileHandler'],
                'level': 'ERROR',
                'propagate': True
            },
            'Crawler': {},

        },
    }
    return LOG_CONF
