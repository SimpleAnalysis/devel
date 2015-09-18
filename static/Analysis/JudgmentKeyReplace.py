#!/usr/bin/python
# -*- coding:utf-8 -*-

# Copyright (c) 2015 yu.liu <showmove@qq.com>
# All rights reserved

# pylint:disable-all


"""Analysis of data


"""


try:
    from extend.Processer.process import Process
except ImportError:
    from NewProject.extend.Processer.process import Process

from model.Loading import insert_database
from model.orm.Replace import ot_judgment_keywords
from model.orm.Judgment216 import Replace
from pybamboo import Bamboo
import time, json
import re
########################################################################


class JudgmentAnalysis(Process):
    
    def to_Replace(self, old, todat):
        new = Replace()
        
        its = ot_judgment_keywords
        self.point.set_tablename(its)
        #self.point.set_tablename(olds)
        self.point.set_filter(filter = 'case_number = %s and keywords != "" ' % old.case_number, limit = 1)
        old_data = self.point.query()
        if not old_data:
            return
        
        
        

    
def run():
    """JudgmentAnalysis
    
    args <数据库名称>
    filter <条件>
    
    扩展：
    指定一个区域ID进行分析
    for i in range(13038, 104105, 20):
        p = JudgmentAnalysis('Judgment', filter = '%d <= id and  id <= %d ' % (i, i + 20))
        p.runing_works()
    注意：绝对不要尝试 %d < id < %d 这样的条件会使得性能下降几百倍

    """
    p = JudgmentAnalysis('Judgment', filter = 'id = 96183')
    p.runing_works()
    #for i in range(13038, 104105, 20):
    #    p = JudgmentAnalysis('Judgment', filter = '%d <= id and  id <= %d ' % (i, i + 20))
    #    p.runing_works()

