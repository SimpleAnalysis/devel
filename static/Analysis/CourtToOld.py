#!/usr/bin/python
# -*- coding:utf-8 -*-

# Copyright (c) 2015 yu.liu <showmove@qq.com>
# All rights reserved

"""更新中间库。
   原因： 最新的中间库使用的parent_id是指向OLD的表的。

"""

from extend.Processer.process import Process
from inspection.extend_analysis import JudgmentProcesser

#from model.orm.SearchExtend import ot_judge_search_extend_old
from model.orm.Judgment import ot_rawdata_judgement_court_gov_cn_old
from model.Loading import insert_database, returns_session
from extend.Processer.utils import *
from extend.WYCrawler.utils import XPath
from inspection.analyse import Analyse

#: 载入案由配置以及地区配置
from configure import anyou_replace, Area_duct, case_mode, OFFICE
#from StringIO import StringIO
#from hashlib import md5
from configure import PROXY
#: 载入基础模块
import time
import json
import re
import arrow
import sys
import requests

reload(sys)
sys.setdefaultencoding('utf-8')
actions_id, actions, replace, anyou_alias = anyou_replace('Judgment')
area = Area_duct()


class JudgmentAnalysis(Process):

    def to_ot_rawdata_judgement_court_gov_cn_old(self, old, todat):

        new = ot_rawdata_judgement_court_gov_cn_old()
        new.url = old.url
        new.referer = old.url

        analy = Analyse()
        try:
            raw_html = XPath(old.source_data).execute(
                '//*[@id="ws"]/table')[0].to_html()
        except IndexError:
            print '[Error] Analyse: url = %s' % new.url

            # Request Get
            for item in PROXY:

                r = requests.get(
                    new.url, proxies={'http': 'http:%s:59274' % item}, timeout=30)
                if r.ok:
                    break
            if not r.ok:
                raise Exception,\
                    'Get faild url = %s' % old.url

            to = old.__class__()
            to.id = old.id
            to.source_data = r.text
            raw_html = XPath(to.source_data).execute(
                '//*[@id="ws"]/table')[0].to_html()
            point = insert_database(
                'Judgment', tablename=to.__class__, editor=new)
            point.update()
            return
        text = html_to_text(HTML_PARSER.unescape(raw_html))
        try:
            text = re.sub('//W3C//DTD HTML 4.0 Transitional//EN\'>', '', text)
        except:
            pass
        analy.text = text
        new.content_all = analy.text

        _header, part, content, case_sign = analy.split_to_four_parts()

        new.clients_attr, new.lawyers_attr = analy.guess_clients_lawyers(
            part.split('\n'))

        end_date = analy.guess_end_date(case_sign)
        new.end_date = end_date

        case_sign_key = analy.guess_case_sign(case_sign.split('\n'))
        head_key = analy.guess_header_types(_header.split('\n'))

        new.content = part + content

        new.case_sign = case_sign
        new.case_number = head_key['case_number']
        new.department = head_key['department']
        new.type = head_key['type']
        new.title = head_key['title']
        new.case_type = head_key['case_type']

        new.procedure = new.procedure or analy.guess_procedure(new.case_number)

        new.replace_data = json.dumps(analy._replace_data(part))

        new.chief_judge = ",".join(case_sign_key[u'审判长'])
        new.acting_judges = ",".join(case_sign_key[u'代理审判员'])
        new.judge = ",".join(case_sign_key[u'审判员'])
        new.clerk = ",".join(list(set(case_sign_key[u'书记员'])))

        new.input_time = arrow.now().timestamp

        # if (not new.chief_judge and not new.judge and not new.acting_judges.strip()) or \
        #   (u'事务所' not in new.plaintiff_lawyers and u'事务所' not in new.defendant_lawyers):
        #    return

        new.parent_id = old.id
        print 'Runing String <ot_rawdata_judgement_court_gov_cn_old> parent_id = %s , url = %s' % (old.id, old.url)

        point = insert_database(
            'Judgment', tablename=ot_rawdata_judgement_court_gov_cn_old, editor=new)
        point.insert()


def runing_starting(start, end):
    """若要使用多个线程进行更行，可以使用这个方法
    args:
        start = 起始ID
        end = 结束ID
    #: 需要思考如何才可以动态的更新！
    #: 当然！使用侦听的方式！来侦听库的ID变化是个很好的办法。


    """
    for i in range(int(start), int(end), 50):
        p = JudgmentAnalysis(
            'SearchExtend', filter='id >= %s and id <= %s' % (i, i + 50))
        p.runing_works()


def run():
    """JudgmentAnalysis

    args <数据库名称>
    filter <条件>

    """
    for i in xrange(1404, 8000000, 100):
        p = JudgmentAnalysis(
            'Judgmentold',
            filter='id >= %s and id <= %s and id NOT IN (SELECT parent_id FROM `ot_rawdata_judgement_court_gov_cn_old` WHERE parent_id !="")' % (i, i + 100))
        p.runing_works()
    #p = JudgmentAnalysis('Judgmentold', filter = 'id = 2')
    # p.runing_works()
