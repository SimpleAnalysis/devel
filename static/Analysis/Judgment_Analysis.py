#!/usr/bin/python
# -*- coding:utf-8 -*-

# Copyright (c) 2015 yu.liu <showmove@qq.com>
# All rights reserved

# pylint:disable-all


"""提供文书POST和GET方式入库

   GET入库对应数据库为：ot_judge_analyze
   
"""

try:
    from extend.Processer.process import Process
except ImportError:
    from NewProject.extend.Processer.process import Process
from inspection.extend_analysis import JudgmentProcesser

from model.orm.Judgment import ot_judgment_diffed, ot_judge_base, ot_rawdata_judgement_court_gov_cn_old as Otraw
from model.orm.Sqlextend import test_old
from model.Loading import insert_database
#: 载入案由配置以及地区配置
from configure import anyou_replace, Area_duct, case_mode
from StringIO import StringIO
from hashlib import md5
import time
import json
import re
import arrow

__output__ = StringIO()
__infomation__ = StringIO()
__plai_people__ = StringIO()
__defan_people__ = StringIO()


def Open_buff():
    __output__ = StringIO()
    __infomation__ = StringIO()
    __plai_people__ = StringIO()
    __defan_people__ = StringIO()


def close_buff():
    __output__.close()
    __infomation__.close()
    __plai_people__.close()
    __defan_people__.close()


def insert_base(old, Update_id=0):
    area = Area_duct()
    actions_id, actions, replace, anyou_alias = anyou_replace('Judgment')
    new = ot_judge_base()
    for attr in ('content', 'case_sign', 'case_type', 'department', 'end_date'):
        if getattr(old, attr) is None:
            print >> __output__, u'【提示】%s 字段为空,请检查数据' % attr
            return
    # if old.case_type not in self.case_mode:
    #    return
    for mode in case_mode:
        if mode in old.case_type:
            new.case_type = mode
    if not new.case_type:
        print >>__output__, u'【提示】文书字号为空'
        return
    if old.content == '':
        print >> __output__, 'u你所访问的数据为空'
    new.content = '<p>' + '</p><p>'.join(old.content.split('\n')) + '</p>'
    new.content_md5 = md5(new.content.encode('utf8')).hexdigest()
    new.case_sign = '<p>' + '</p><p>'.join(old.case_sign.split('\n')) + '</p>'
    new.case_number = old.case_number

    new.type = new.case_type[:-3]
    #: 如果是仲裁,那属于民事
    if new.type == u'仲裁':
        new.type = u'民事'
    new.title = old.title
    if not new.title:
        new.title = old.content_all.split('\n')[0]

    Pules = {}
    #: 更新案由信息

    if new.type == u'行政':
        anyou = filter(lambda x: x in new.title, actions)
        if not anyou:
            anyou = filter(lambda x: x in old.content.split('\n')[0], actions)
            if anyou:
                anyou = anyou[0]
        else:
            for item in anyou:
                Pules[len(item)] = item
    else:
        anyou = filter(lambda x: x in old.content.split('\n')[0], actions)
        if not anyou:
            anyou = filter(lambda x: x in new.title, actions)
            for item in anyou:
                Pules[len(item)] = item
        else:
            anyou = anyou[0]
    if Pules:
        anyou = Pules[max(Pules)]

    new.anyou_id = actions_id[anyou.strip()]
    new.anyou = anyou
    # new.anyou_id = actions_id[new.anyou]

    new.department = old.department

    new.chief_judge = old.chief_judge

    new.judge = old.judge

    if old.acting_judges:
        new.acting_judges = old.acting_judges
    else:
        new.acting_judges = '无'

    new.clerk = old.clerk

    new.plaintiff = ';'.join(
        u"%s:%s:%s" % client for client in old.clients_attr[u'原告'])
    new.plaintiff_lawyers = ';'.join(
        u"%s:%s" % lawyer for lawyer in old.lawyers_attr[u'原告'])
    print >> __plai_people__, u'原告:%s, 律师:%s' % (
        new.plaintiff, new.plaintiff_lawyers)
    new.defendant = ';'.join(
        u"%s:%s:%s" % client for client in old.clients_attr[u'被告'])
    new.defendant_lawyers = ';'.join(
        u"%s:%s" % lawyer for lawyer in old.lawyers_attr[u'被告'])
    print >> __defan_people__, u'被告:%s, 律师:%s' % (
        new.defendant, new.defendant_lawyers)
    new.procedure = old.procedure

    new.end_date = arrow.get(old.end_date, 'Asia/Shanghai').timestamp

    # 分析地区
    area_item = area.ident(new.department.encode('gbk'))

    if area_item and area_item.get('staut') == 'timed out':
        new.areacode = area_item['areano']

    new.url = old.referer

    print >>__infomation__, old.case_sign
    new.replace_data = json.dumps(old.replace_data)
    # dic = {}
    # for k, v in old.replace_data.iteritems():
    #    if not re.match(ur".*(某|X|x|\*).*", k):
    #        dic.update({k:v})
    # new.replace_data = json.dumps(dic)
    new.input_time = arrow.now().timestamp
    if (not new.chief_judge and not new.judge and not new.acting_judges.strip()) or \
       (u'事务所' not in new.plaintiff_lawyers and u'事务所' not in new.defendant_lawyers):
        print >>__output__, u'不存在事务所或者署名信息'
        return
    print old.id
    if Update_id != 0:
        new.id = Update_id
        new.url = old.url
        point = insert_database(
            'Judgment', tablename=ot_judge_base, editor=new)
        point.update()
    else:
        point = insert_database(
            'Judgment', tablename=ot_judge_base, editor=new)
        point.insert()


class JudgmentAnalysis(Process):

    def to_test_old(self, old, todat):

        olds = Otraw
        new = test_old()
        new.title = old.title
        new.case_number = old.sn
        new.department = old.court
        new.case_type = old.title
        analy = JudgmentProcesser()
        analy.fuzzy_analyse(new, old.content)
        point = insert_base(new)
        return

    def to_ot_judgment_diffed(self, old, todat):
        olds = Otraw
        new = test_old()
        if old.url:
            if ('openlaw' in old.url):
                self.point.set_tablename(Open)
                self.point.set_filter(
                    filter='id = %s' % old.parent_id, limit=1)

            else:
                self.point.set_tablename(olds)
                self.point.set_filter(
                    filter='id = %s' % old.parent_id, limit=1)
        else:
            self.point.set_tablename(olds)
            self.point.set_filter(filter='id = %s' % old.parent_id, limit=1)

        old_data = self.point.query()
        if not old_data:
            return
        old_data = old_data[0]
        new.url = old_data.url

        analy = JudgmentProcesser()
        analy.fuzzy_analyse(new, old_data.content_all)
        insert_base(new, old.id)
        print __output__.getvalue()
        return


def web_port_id(num):
    """WEB API GET
        GET:
            http://192.168.1.118/api/v1.0/judgment/{ID}
        Returns:
                JSON(
                    {
                    "result": {
                        "People": {
                                "Plain": "",
                                "defen": ""
                            },
                        "danger": "",
                        "error": "Success",
                        "sign": "",
                        "status": 1
                        }
                    })
    """
    global __output__
    global __infomation__
    global __plai_people__
    global __defan_people__

    if __defan_people__.closed or __infomation__.closed:
        __output__ = StringIO()
        __infomation__ = StringIO()
        __plai_people__ = StringIO()
        __defan_people__ = StringIO()

    p = JudgmentAnalysis('AnalyzeTobase', filter='id = %s' % num)
    p.runing_works()
    result = {'sign': __infomation__.getvalue(), 'danger': __output__.getvalue(),
              'People': {'Plain': __plai_people__.getvalue(), 'defen': __defan_people__.getvalue()}}
    try:
        close_buff()
    except TypeError:
        pass
    return result


def web_port(case_number='', title='', depart='', datasource=None):
    """WEB API POST 
        POST:
            http://192.168.1.118/api/v1.0/judgment/
            case_number => case_number,
            title => title,
            depart => department,
            datasource => content
        Returns:
            JSON(
                {
                "result": {
                    "People": {
                            "Plain": "",
                            "defen": ""
                        },
                    "danger": "",
                    "error": "Success",
                    "sign": "",
                    "status": 1
                    }
                })
    """
    if datasource:
        new = test_old()
        analy = JudgmentProcesser()

        analy.fuzzy_analyse(new, datasource)

        try:
            new.clients_attr[u'原告'] = list(set(new.clients_attr[u'原告']))
            new.clients_attr[u'被告'] = list(set(new.clients_attr[u'被告']))
            new.lawyers_attr[u'原告'] = list(set(new.lawyers_attr[u'原告']))
            new.lawyers_attr[u'被告'] = list(set(new.lawyers_attr[u'被告']))
            plaintiff = ';'.join(
                u"%s:%s:%s" % client for client in new.clients_attr[u'原告'])
            defendant = ';'.join(
                u"%s:%s:%s" % client for client in new.clients_attr[u'被告'])
            plaintiff_lawyers = ';'.join(
                u"%s:%s" % lawyer for lawyer in new.lawyers_attr[u'原告'])
            defendant_lawyers = ';'.join(
                u"%s:%s" % lawyer for lawyer in new.lawyers_attr[u'被告'])
        except:
            return {'error': datasource}

        point = insert_database(
            'Sqlextend', tablename=test_old, editor=new)  # 设置添加数据
        try:
            point.insert()  # 添加数据
        except Exception, e:
            return {'error': e}

        print plaintiff
        print defendant
        print plaintiff_lawyers
        print defendant_lawyers

        return {'People': {u'原告': plaintiff, u'被告': defendant}, 'lawyers': {u'原告': plaintiff_lawyers, u'被告': defendant_lawyers},
                'case_number': new.case_number,
                'title': new.title,
                'sign': new.case_sign,
                'type': new.case_type,
                'error': 0}

    else:
        return {'error': u'没有传递数据过来噢'}


def run():
    """JudgmentAnalysis

    args <数据库名称>
    filter <条件>

    """

    p = JudgmentAnalysis('AnalyzeTobase', filter='id = 18')
    p.runing_works()

    # for i in range(43102, 104105, 10):
    #    p = JudgmentAnalysis('Judgment', filter='id >%s and id < %s' %(i, i+10))
    #    p.runing_works()
