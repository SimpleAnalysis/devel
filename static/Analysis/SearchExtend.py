#!/usr/bin/python
# -*- coding:utf-8 -*-

# Copyright (c) 2015 yu.liu <showmove@qq.com>
# All rights reserved


from extend.Processer.process import Process

from inspection.extend_analysis import JudgmentProcesser
from model.orm.SearchExtend import ot_judge_search_extend_old
from model.Loading import insert_database, query

from inspection.analyse import Analyse

#: 载入案由配置以及地区配置
from configure import anyou_replace, Area_duct, case_mode, OFFICE, case_type_list

from StringIO import StringIO
from hashlib import md5
import time
import json
import re
import arrow
import sys


reload(sys)
sys.setdefaultencoding('utf-8')
actions_id, actions, replace, anyou_alias = anyou_replace('Judgment')
area = Area_duct()
case_type_key = case_type_list('JudgmentCenter')

DICT_SEARCH_KEY = {}


class JudgmentAnalysis(Process):

    def Update_extend_old(self, old):
        new = ot_judge_search_extend_old()
        if case_type_key.has_key(old.case_type.decode('utf8')):
            new.case_type_id = str(case_type_key[old.case_type.decode('utf8')])
        else:
            new.case_type_id = '0'
        print 'Update id = %s, new.case_type_id = %s' % (old.id, new.case_type_id)

        return new

    def to_query_ot_judge_search_extend_old(self, old, todat):
        """查询方法

        """
        new = todat()
        print 'Search True, id = %s' % old.id
        # DICT_SEARCH_KEY[old.id] = {
        #    'content': old.content, 'titile': old.title, 'case_number': old.case_number}
        new.id = old.id
        point = insert_database(
            'SearchExtend', tablename=todat, editor=new)
        point.update()

    def to_update_ot_judge_search_extend_old(self, old, todat):
        """更新方法

        """
        new = self.Update_extend_old(old)
        new.id = old.id
        # self.point.set_value(new)
        # self.point.update()
        point = insert_database(
            'SearchExtend', tablename=ot_judge_search_extend_old, editor=new)
        point.update()
        return

    def to_edit_ot_judge_search_extend_old(self, old, todat):
        """修改方法

        """
        pass

    def to_ot_judge_search_extend_old(self, old, todat):
        """默认方法

        """
        #analy = JudgmentProcesser()

        #analy.fuzzy_analyse(old, old.content_all)

        #insert_base(old, Update_id = 0)

        # return

        new = ot_judge_search_extend_old()
        analy = Analyse()
        analy.text = old.content_all
        _header, part, content, case_sign = analy.split_to_four_parts()

        clients_attr, lawyers_attr = analy.guess_clients_lawyers(
            part.split('\n'))
        case_sign_key = analy.guess_case_sign(case_sign.split('\n'))
        head_key = analy.guess_header_types(_header.split('\n'))

        clients_attr[u'原告'] = list(set(clients_attr[u'原告']))
        clients_attr[u'被告'] = list(set(clients_attr[u'被告']))
        lawyers_attr[u'原告'] = list(set(lawyers_attr[u'原告']))
        lawyers_attr[u'被告'] = list(set(lawyers_attr[u'被告']))

        plaintiff = ''
        defendant = ''
        plaintiff_lawyers = ''
        defendant_lawyers = ''

        if clients_attr[u'原告']:
            plaintiff = ';'.join(
                u"%s:%s:%s" % client for client in clients_attr[u'原告'])
        if clients_attr[u'被告']:
            defendant = ';'.join(
                u"%s:%s:%s" % client for client in clients_attr[u'被告'])
        if lawyers_attr[u'原告']:
            plaintiff_lawyers = ';'.join(
                u"%s:%s" % lawyer for lawyer in lawyers_attr[u'原告'])
        if lawyers_attr[u'被告']:
            defendant_lawyers = ';'.join(
                u"%s:%s" % lawyer for lawyer in lawyers_attr[u'被告'])
        if not head_key['case_type']:
            return

        for attr in ('content', 'end_date'):
            if getattr(old, attr) is None:
                print u'content is None, id = %s ' % old.id
                return
        new.content = '<p>' + \
            '</p><p>'.join((part + content).split('\n')) + '</p>'
        new.content_md5 = md5(new.content.encode('utf8')).hexdigest()
        new.case_sign = '<p>' + '</p><p>'.join(case_sign) + '</p>'

        new.case_number = head_key['case_number']
        new.department = head_key['department']
        new.type = head_key['type']
        new.title = head_key['title']
        new.case_type = head_key['case_type']
        new.case_type_id = str(
            case_type_key.get(old.case_type.decode('utf8'))) or '0'

        new.plaintiff = plaintiff
        new.defendant = defendant
        new.plaintiff_lawyers = plaintiff_lawyers
        new.defendant_lawyers = defendant_lawyers

        Pules = {}
        #: 更新案由信息
        if new.type == u'行政':
            anyou = filter(lambda x: x in new.title, actions)
            if not anyou:
                anyou = filter(lambda x: x in content.split('\n')[0], actions)
                if anyou:
                    anyou = anyou[0]
            else:
                for item in anyou:
                    Pules[len(item)] = item
        else:
            anyou = filter(lambda x: x in content.split('\n')[0], actions)
            if not anyou:
                anyou = filter(lambda x: x in new.title, actions)
                for item in anyou:
                    Pules[len(item)] = item
            else:
                anyou = anyou[0]
        if Pules:
            anyou = Pules[max(Pules)]
        if not anyou:
            new.anyou_id = 0
            new.anyou = ''
        else:
            new.anyou_id = actions_id[anyou.strip()]
            new.anyou = anyou
        
        new.chief_judge = ",".join(case_sign_key[u'审判长'])
        new.acting_judges = ",".join(case_sign_key[u'代理审判员'])
        new.judge = ",".join(case_sign_key[u'审判员'])
        new.clerk = ",".join(list(set(case_sign_key[u'书记员'])))
        new.procedure = old.procedure

        new.end_date = arrow.get(old.end_date, 'Asia/Shanghai').timestamp

        # 分析地区
        area_item = area.ident(new.department.encode('gbk'))
        if area_item:
            new.areacode = area_item['areano']

        new.url = old.referer

        replace_data = analy._replace_data(part)
        # for k, v in old.replace_data.iteritems():
        #    if not re.match(ur".*(某|X|x|\*).*", k):
        #        dic.update({k: v})
        new.replace_data = json.dumps(replace_data)
        new.input_time = arrow.now().timestamp

        # if (not new.chief_judge and not new.judge and not new.acting_judges.strip()) or \
        #   (u'事务所' not in new.plaintiff_lawyers and u'事务所' not in new.defendant_lawyers):
        #    return
        if (not new.chief_judge and not new.judge and not new.acting_judges.strip()) or \
           (not filter(lambda x: x in new.plaintiff_lawyers, OFFICE) and
                not filter(lambda x: x in new.defendant_lawyers, OFFICE)):
            print "[Warning] Not Condition , id = %s , url = %s" % (old.id, old.url)
            return

        new.parent_id = old.id
        print 'Runing String <to_ot_judge_search_extend_old> parent_id = %s , url = %s' % (old.id, old.url)

        point = insert_database(
            'SearchExtend', tablename=ot_judge_search_extend_old, editor=new)
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
            'SearchExtend', filter='id >= %s and id <= %s' % (i, i + 50), UPDATE=True)

        p.runing_works()


def Search_runing():
    """尝试一个搜索方法
       测试1：
       CASE_NUMBER = 皖民四终字
       5分钟左右 200万数据,并能显示结果

       测试2：
       plaintiff_lawyers LIKE '%赵爱红%'
       or
       defendant_lawyers LIKE '%赵爱红%'
       使用OR时需要使用括号括起来
       10分钟左右

       注意事项：
       请填写好你的搜索条件！
       在数据返回结果多的情况：
       请将for i in xrange(start,end, number = 设置一个适合的数字)
       (plaintiff_lawyers = "{2}%" or defendant_lawyers like "{2}%")
    """
    point = query(
        'SearchExtend', tablename=ot_judge_search_extend_old)

    start, end = point.Size()
    #start = 0
    #end = 20
    print start, end
    data = u'赵爱红'
    for i in xrange(start, end, 10000):
        p = JudgmentAnalysis(
            'SearchExtend',
            filter='md5_identity IS NULL and id >= {0} and id <= {1}'.format(
                i, i + 10000, data),
            QUERY=True)
        # print i, i + 10000
        result = p.runing_works()

    for item in DICT_SEARCH_KEY:
        print DICT_SEARCH_KEY[item]['case_number'].decode('utf8'), item


def run():
    """JudgmentAnalysis

    args <数据库名称>
    filter <条件>

    """
    ##########################################################################
    #: 新增扩展调用说明
    #: Update => ot_update_tablename
    #: p = JudgmentAnalysis('Judgment', filter='id >%s and id < %s' % (1,100), UPDATE = True)
    #: p.runing_works()
    #: Edit => ot_edit_tablename
    #: p = JudgmentAnalysis('Judgment', filter='id >%s and id < %s' % (1, 100), EDIT = True)
    #: p.runing_works()
    ##########################################################################
    for i in xrange(5924419, 8000000, 100):
        p = JudgmentAnalysis(
            'SearchExtend',
            filter='id >= %s and id <= %s and id NOT IN (SELECT parent_id FROM `ot_judge_search_extend_old` WHERE parent_id !="")' % (i, i + 100))

        p.runing_works()
