#!/usr/bin/env python
# -*- coding:utf-8 -*-

# Copyright (c) 2015 yu.liu <showmove@qq.com>
# All rights reserved


"""Configuretion ,this is system config. 
   配置结构：
   Config : 管理数据库链接信息 TYPE: DICT 
   Configuretion: 反正一个正确的ORM链接字符串 TYPE: FUNCTON RETURN:STRING
   Area_Duct: 返回地区搜索 TYPE: FUNCTION RETURN: FUNCTION
   Checking_area: 在地区库中使用模糊查询，查询全名: TYPE: FUNCTION RETURN: TRUE|FALSE
   anyou_replace: 案由信息和敏感信息 TYPE: FUNCTION RETURN: TUPLE
   case_mode: 返回文书类型列表 TYPE: TUPLE
   

"""
from .log_config import Crawler_log
from .proxy_config import Re_True_Proxy
from .agency_config import *
PROXY = Re_True_Proxy()

LOG_CONF = Crawler_log()

#: 配置数据库链接
#: 配置方式:
#：Config = { 'ORM_CLASS_FILE',{'DBTYPE':,'USERNAME':,'PASSWORD':,'IPADDRESS':,'PORT':,
#:            'DATABASE':,'ENCODING',:ECHO:}}
#: 扩展配置:
#: Config['ORM_CLASS_FILE'] = CONFIG['ORM_CLASS']
#: 使用这种方式可以配置相同的链接来指定不同的表


Config = {'Sqlextend':
          {'dbtype': 'mysql+mysqldb',
           'Username': 'dd',
           'Password': '12321',
           'Address': '192.168.1.216',
           'Port': '3306',
           'Database': 'lawyer_center',
           'encoding': 'utf-8',
           'echo': False
           },

           }
          }


#: 返回标准ORM链接字符串


def Configuretion(item):
    """Orm database configure

    Args: 
        Dict_key
    Returns:
        orm link config
    """
    return Config[item]['dbtype'] + '://' + \
        Config[item]['Username'] + ':' + \
        Config[item]['Password'] + '@' + \
        Config[item]['Address'] + ':' + \
        Config[item]['Port'] + '/' + \
        Config[item]['Database'] + '?charset=' + \
        Config[item]['encoding'].replace('-', '')


#: 配置分析
def SourceToAnalysis():
    """返回原数据和去往数据

       扩展 1：
       {'Judgment': 'From': [] ,'TO': [], 'EDIT': {'FROM':[], 'TO':[]}} ? 
       扩展 2：
       {'Judgment': 'From': [] ,'TO': [], 'UPDATA' : { ... }}?
       扩展有助于对数据进行更多的操作,更多操作请看PROCESS代码
       From : 默认来源
       To   : 默认去往

       EDIT : 修改   {FROM: [] , TO: []}
       UPDATA : 更新 {FROM: [] , TO: []}
       不设置EDIT、UPDATE则以TO为准,

    """
    #: 载入相应的ORM模块
    from model.orm.Judgment import ot_judge_base, ot_judgment_diffed, ot_judge_inspection
    from model.orm.Judgment216 import ot_rawdata_judgement_court_gov_cn
    from model.orm.AnalyzeTobase import ot_judge_analyze, ot_judge_base as tobase
    from model.orm.Judgmentold import ot_rawdata_judgement_court_gov_cn_old
    from model.orm.Sqlextend import test_old
    from model.orm.Judgment216 import Replace
    from model.orm.inspection import ot_process_error
    from model.orm.SearchExtend import ot_judge_search_extend_old
    #: 返回配置From = 来源库， To = 去往库
    SourceToAnalysis_data = {'Judgment':
                             {
                                 'From': [ot_judge_base, ],
                                 'To': [ot_judgment_diffed, ]
                             },
                             'AnalyzeTobase':
                             {
                                 'From': [ot_judge_analyze, ],
                                 'To': [test_old, ]
                             },
                             'Judgmentold':
                             {
                                 'From': [ot_rawdata_judgement_court_gov_cn, ],
                                 'To': [ot_rawdata_judgement_court_gov_cn_old, ]
                             },
                             'Replace':
                             {
                                 'From': [ot_judge_base, ],
                                 'To': [Replace, ]
                             },
                             'inspection':
                             {
                                 'From': [ot_judge_base, ],
                                 'To': [ot_process_error, ]
                             },
                             'SearchExtend':
                             {
                                 'From': [ot_rawdata_judgement_court_gov_cn_old, ],
                                 'To': [ot_judge_search_extend_old, ]
                             },
                             'UpdateBase':
                             {
                                 'From': [ot_judge_search_extend_old, ],
                                 'To': [ot_judge_search_extend_old, ]
                             }
                             }
    return SourceToAnalysis_data



