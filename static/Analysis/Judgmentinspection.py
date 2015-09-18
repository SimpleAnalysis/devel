#!/usr/bin/python
# -*- coding:utf-8 -*-

# Copyright (c) 2015 yu.liu <showmove@qq.com>
# All rights reserved

# pylint:disable-all

"""裁判文书更新

   主要作用于发现文书错误后直接更新裁判文书。
   
   目前支持API调用:
   
   GET:
   
       http://192.168.1.118/api/v1.0/JudgmentUpdate/112448
   
   POST:

       暂无


"""


#: 载入程序运行模块
try:
    from extend.Processer.process import Process
except ImportError:
    from NewProject.extend.Processer.process import Process

#: 载入分析模块
from inspection.analyse import Analyse

#: 载入ORM模块
from model.orm.Judgment import ot_judgment_diffed, ot_judge_base, ot_rawdata_judgement_court_gov_cn_old as Otraw, \
    ot_rawdata_judgment_openlaw_old as Open

#: 载入检查文书正确性模块
from CheckData import JudgmentCheck

#: 载入数据连接模块插入模块
from model.Loading import insert_database

#: 载入配置模块
from configure import anyou_replace, Area_duct

#: 载入BANBOO模块
#: from pybamboo import Bamboo

#: 载入基础模块
import time
import json
import sys
import arrow
import re

reload(sys)
sys.setdefaultencoding('utf-8')


#: 定制全局变量
AREA = Area_duct()
ACTION_ID, ACTIONS, REPLACE, ANYOU_ALIAS = anyou_replace('Judgment')


class JudgmentAnalysis(Process):

    """继承程序运行模块，开始对任务进行分析


    """

    def fuzzy_analyse(self, old_data):
        "分析方法，开始对数据进行分析"
        analy = Analyse()
        analy.text = old_data.content_all

        _header, part, content, case_sign = analy.split_to_four_parts()
        if len(_header.split('\n')) < 4:
            _header = "\n".join(analy.text_in_lines[0:6])
        _header = re.sub(u'日期:|法院:|案号:', '', _header)
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
        end_time = analy.guess_end_date(case_sign)
        replace_data = analy._replace_data(part)

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

        return [(_header, part, content, case_sign),
                (plaintiff, plaintiff_lawyers),
                (defendant, defendant_lawyers),
                case_sign_key,
                head_key,
                replace_data,
                end_time]

    def to_ot_judgment_diffed(self, old, todat):
        """选择to库，此处可以是个任意库，但是必须对应配置文件中的库.

        此前该方法作为验证正确性使用，现在用于更新使用


        """

        # if old.status in ['-1', '3', '1'] or (not old.url):
        #    return

        print old.id, old.url
        olds = Otraw

        #diff = ot_judgment_diffed()

        print "[Analysis to %s] time: %s " % (todat, time.strftime('%y-%m-%d %H-%M-%S'))

        if ('openlaw' in old.url):
            self.point.set_tablename(Open)
            self.point.set_filter(filter='id = %s' % old.parent_id, limit=1)

        else:
            self.point.set_tablename(olds)
            self.point.set_filter(filter='id = %s' % old.parent_id, limit=1)

        old_data = self.point.query()
        if not old_data:
            return

        old_data = old_data[0]

        analysis_data = self.fuzzy_analyse(old_data)

        """将此处代码注释去掉，可对验证正确性库进行写入数据
        new_plain_lawyer = {'Success': old.plaintiff_lawyers,
                            'old': plaintiff_lawyers,
                            'new': analysis_data[1][1]
                            }
        new_defen_lawyer = {'Success': old.defendant_lawyers,
                    'old': defendant_lawyers,
                    'new': analysis_data[2][1]
                    }
        plaintiff = ';'.join(u"%s:%s:%s" % client for client in old_data.clients_attr[u'原告'])
        defendant = ';'.join(u"%s:%s:%s" % client for client in old_data.clients_attr[u'被告'])
        
        new_plain_people = {'Success': old.plaintiff, 
                            'old': plaintiff,
                            'new': analysis_data[1][0]
                            }
        new_defen_people = {'Success': old.defendant, 
                            'old': defendant,
                            'new': analysis_data[2][0]
                            }
        
        diff.case_sign = analysis_data[0][3]
        diff.header = analysis_data[0][0]
        diff.content = analysis_data[0][2]
        diff.firsthead = analysis_data[0][1]
        diff.defendant = json.dumps(new_defen_people)
        diff.defendant_lawyers = json.dumps(new_defen_lawyer)
        diff.plaintiff = json.dumps(new_plain_people)
        diff.plaintiff_lawyers = json.dumps(new_plain_lawyer)
        diff.judgmentid = old.id
        diff.url = old.url
        point = insert_database('Judgment', tablename = todat, editor = diff)  #设置添加数据
        point.insert()   #添加数据
        """

        Update = ot_judge_base()

        # if (not old.chief_judge and not old.judge and not old.acting_judges ) or \
        #   (u'事务所' not in analysis_data[1][1] and u'事务所' not in analysis_data[2][1]):
        # : 删除信息
        # print 'Delete new Analy %s' % old.id
        # point = insert_database('Judgment', tablename = ot_judge_base, filter = 'id = %s' % old.id)
        # point.delete()
        #    pass
        #: 更新CASE_SIGN
        case_sign = analysis_data[0][3].split('\n')
        Update.case_sign = '<p>' + '</p><p>'.join(case_sign) + '</p>'
        # else:
        Pules = {}
        #: 更新案由信息
        anyou = []
        if old.type == u'行政':
            #: 检查标题
            anyou.extend(filter(lambda x: x in analysis_data[0][0], ACTIONS))
            if not anyou:
                #: 检查第一行
                anyou.extend(filter(
                    lambda x: x in "".join(analysis_data[0][2].split('\n')[:1]), ACTIONS))

        else:
            anyou.extend(filter(
                lambda x: x in "".join(analysis_data[0][2].split('\n')[:1]), ACTIONS))
            # if not anyou:
            anyou.extend(filter(lambda x: x in analysis_data[0][0], ACTIONS))

        for item in anyou:
            Pules[len(item)] = item

        if Pules:
            anyou = Pules[max(Pules)]

        if anyou:
            Update.anyou_id = ACTION_ID[anyou.strip()]
            if ANYOU_ALIAS.has_key(anyou):
                Update.anyou = ANYOU_ALIAS[anyou]
            else:
                Update.anyou = anyou
        else:
            Update.anyou = ''
            Update.anyou_id = 0
        # print Update.anyou_id
        area_item = AREA.ident(old.department.replace(u'县', '').replace(u'自治区', '')
                               .replace(u'管城回族区', '管城回区').encode('gbk'))

        if area_item:
            Update.areacode = area_item['areano']
        else:
            area_item = AREA.ident(
                old.department.replace(u'市', '').replace(u'区', '').replace(u'省', '').encode('gbk'))
            if area_item:
                Update.areacode = area_item['areano']

        # print 'Update new Analysis'
        Update.defendant = analysis_data[2][0]
        Update.defendant_lawyers = analysis_data[2][1]
        Update.plaintiff = analysis_data[1][0]
        Update.plaintiff_lawyers = analysis_data[1][1]
        Update.id = old.id

        #: 更新审判人员信息
        case_sign_key = analysis_data[3]

        Update.chief_judge = ",".join(case_sign_key[u'审判长'])
        Update.acting_judges = ",".join(case_sign_key[u'代理审判员'])
        Update.judge = ",".join(case_sign_key[u'审判员'])
        Update.clerk = ",".join(list(set(case_sign_key[u'书记员'])))

        head_key = analysis_data[4]

        Update.department = head_key['department']
        Update.case_number = head_key['case_number']

        Update.type = head_key['type']
        Update.title = head_key['title']

        #: 分析裁判时间
        Update.end_date = arrow.get(
            analysis_data[6], 'Asia/Shanghai').timestamp
        #: 敏感信息
        Update.replace_data = analysis_data[5]

        #: 检查敏感信息
        #： for item in REPLACE:
        #：     if item in old_data.content_all:
        #:          Update.replace_data[item] = '****'

        Update.replace_data = json.dumps(Update.replace_data)
        #: 开始检查数据 正确性
        ero = JudgmentCheck.Judgment_checking(
            analysis_data[0][0], analysis_data[0][1], analysis_data[0][2], analysis_data[0][3])

        #: 验证案由
        ero.Checking_anyou(Update.anyou, old.type)

        #: 验证地区
        ero.Checking_area(Update.areacode, old.department)

        #: 验证原告被告
        ero.Checking_people(Update.plaintiff, Update.defendant)

        #: 验证原、被告律师
        ero.Checking_lawyer(Update.plaintiff_lawyers, Update.defendant_lawyers)

        #: 验证署名
        #: 署名可以添加详细署名
        #：如
        #: keys = {'judge': old.judge}
        #: ero.Checking_sign(keys)
        #: 这样就可以验证详细的署名信息
        ero.Checking_sign()

        #: 审理机构检查
        ero.Checking_department(old.department.decode('utf8'))

        if not ero.errors:
            for attr in old.__dict__.keys():
                if not getattr(old, attr) or str(getattr(old, attr)).strip() == u'无':
                    if (not getattr(Update, attr)) or str(getattr(Update, attr)).strip() == '':
                        setattr(Update, attr, u'无')
            Update.come_from = 'Update_Judgment_Checking_Success'
            Update.base_check = 1
            Update.status = 2

        else:

            Update.come_from = 'Update_Judgment_Checking_Faild'
            Update.status = 0
            Update.base_check = 0

        point = insert_database(
            'Judgment', tablename=ot_judge_base, editor=Update)
        code = point.update()
        if code == 1062:
            #: 存在重复数据
            print "Delte From id = %s, table = %s" % (Update.id, ot_judge_base.__name__)
            point.set_filter('id = %s' % old.id)
            point.delete()
        return


def run():
    """JudgmentAnalysis

    args <数据库名称>
    filter <条件>

    """

    #: 调用案例说明，
    ##########################################################################
    #: 指定多个ID段落
    #: for i in range(108479, 112984, 10):
    #:    p = JudgmentAnalysis('Judgment', filter='id >= %s and id <= %s ' %(i, i+10))
    #:    p.runing_works()
    #: 指定一个小范围
    #:
    #: p = JudgmentAnalysis('Judgment', filter='id >= %s and id <= %s and base_check = 1 and status = 2' %(100, 500))
    #: p.runing_works()
    #: 支持IN语句
    #: p = JudgmentAnalysis('Judgment', filter='id in %s and come_from="Update_Judgment_Checking_Faild" ' % repr((1,2,3,4,5,6,7,8,100)))
    #: p.runing_works()
    ##########################################################################
    for i in range(0, 130000, 100):
        clerk = u'无'
        p = JudgmentAnalysis(
            'Judgment', filter='id >= %s AND id <= %s AND update_datetime >= "15-09-18 16:00:52"' % (i, i + 100))
        p.runing_works()

    # p = JudgmentAnalysis(
    #    'Judgment', filter='id = 13136')
    # p.runing_works()
