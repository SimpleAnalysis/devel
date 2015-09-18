#!/usr/bin/python
# -*- coding:utf-8 -*-

# Copyright (c) 2015 yu.liu <showmove@qq.com>
# All rights reserved

# pylint:disable-all


try:
    from extend.Processer.process import Process
except ImportError:
    from NewProject.extend.Processer.process import Process
#from inspection.analyse import Analyse
#from model.orm.Judgment import ot_judgment_diffed, ot_judge_base, ot_rawdata_judgement_court_gov_cn_old as Otraw
from inspection.extend_analysis import JudgmentProcesser
from model.orm.Judgmentold import ot_rawdata_judgement_court_gov_cn_old as Otraw
from model.Loading import insert_database
from pybamboo import Bamboo
import time
import json
import re


class JudgmentAnalysis(Process):

    def to_ot_rawdata_judgement_court_gov_cn_old(self, old_data, todat):
        """分析方法，开始对数据进行分析

        目前只更新中间库的原被告和律师律所。
        其他信息并未更新。
        如有其他需求！可在中间库更新至结果库时进行进一步的分析。

        """
        analy = Analyse()
        analy.text = old_data.content_all
        new = Otraw()
        _header, part, content, case_sign = analy.split_to_four_parts()

        clients_attr, lawyers_attr = analy.guess_clients_lawyers(
            part.split('\n'))

        clients_attr[u'原告'] = list(set(clients_attr[u'原告']))
        clients_attr[u'被告'] = list(set(clients_attr[u'被告']))
        lawyers_attr[u'原告'] = list(set(lawyers_attr[u'原告']))
        lawyers_attr[u'被告'] = list(set(lawyers_attr[u'被告']))
        new.clients_attr = clients_attr
        new.lawyers_attr = lawyers_attr

        #plaintiff = ';'.join(u"%s:%s:%s" % client for client in clients_attr[u'原告'])
        #defendant = ';'.join(u"%s:%s:%s" % client for client in clients_attr[u'被告'])
        #plaintiff_lawyers = ';'.join(u"%s:%s" % lawyer for lawyer in lawyers_attr[u'原告'])
        #defendant_lawyers = ';'.join(u"%s:%s" % lawyer for lawyer in lawyers_attr[u'被告'])
        #new.lawyer_name = ''
        #new.firm_name = ''
        lawyers = []
        frim = []
        for item in lawyers_attr:
            for x, y in lawyers_attr[item]:
                if x:
                    lawyers.append(x.strip())

                if y:
                    frim.append(y.strip())

        # print new.lawyer_name, new.firm_name
        new.lawyer_name = ",".join(lawyers)
        new.firm = ",".join(frim)

        print old_data.id, old_data.url, new.lawyer_name, new.firm

        new.id = old_data.id
        point = insert_database('Judgmentold', tablename=todat, editor=new)
        point.update()


def runing_starting(start, end):
    """若要使用多个线程进行更新，可以使用这个方法
    args:
        start = 起始ID
        end = 结束ID
    #: 需要思考如何才可以动态的更新！
    #: 当然！使用侦听的方式！来侦听库的ID变化是个很好的办法。


    """
    for i in range(int(start), int(end), 50):
        p = JudgmentAnalysis(
            'Judgmentold', filter='id > %s and id < %s' % (i, i + 50))
        p.runing_works()


def run():
    """JudgmentAnalysis

    args <数据库名称>
    filter <条件>

    #可以根据ID范围进行更新.
    """

    # 7363479
    # for i in range(533272, 1000000, 50):
    #    p = JudgmentAnalysis('Judgmentold', filter='id >%s and id < %s' %(i, i+50))
    #    p.runing_works()

    # for i in range(1437324, 2000000, 50):
    #    p = JudgmentAnalysis('Judgmentold', filter='id >%s and id < %s' %(i, i+50))
    #    p.runing_works()

    # for i in range(2500010, 3000000, 50):
    #    p = JudgmentAnalysis('Judgmentold', filter='id >%s and id < %s' %(i, i+50))
    #    p.runing_works()

    for i in range(3241488, 4000000, 50):
        p = JudgmentAnalysis(
            'Judgmentold', filter='id >=%s and id <= %s' % (i, i + 50))
        p.runing_works()
    for i in range(4000000, 5000000, 50):
        p = JudgmentAnalysis(
            'Judgmentold', filter='id >%s and id < %s' % (i, i + 50))
        p.runing_works()
    for i in range(5000000, 6000000, 50):
        p = JudgmentAnalysis(
            'Judgmentold', filter='id >%s and id < %s' % (i, i + 50))
        p.runing_works()
    for i in range(6000000, 7363479, 50):
        p = JudgmentAnalysis(
            'Judgmentold', filter='id >%s and id < %s' % (i, i + 50))
        p.runing_works()
