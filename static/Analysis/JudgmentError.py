#!/usr/bin/python
# -*- coding:utf-8 -*-

# Copyright (c) 2015 yu.liu <showmove@qq.com>
# All rights reserved


"""效验裁判文书类
   提供API核心方法：

   POST:
      ARGS
   GET：
      ID
    

"""
from extend.Processer.process import Process
from inspection.analyse import Analyse
from model.orm.Judgment import ot_judgment_diffed, ot_judge_base, \
    ot_rawdata_judgement_court_gov_cn_old as Otraw, \
    ot_rawdata_judgment_openlaw_old as Open
from model.orm.inspection import ot_process_error
from CheckData.JudgmentCheck import Judgment_checking

from model.Loading import insert_database
from model.Loading import returns_session

from configure import anyou_replace, Area_duct
import time
import json
import re

AREA = Area_duct()
ACTION_ID, ACTIONS, REPLACE, ANYOU_ALIAS = anyou_replace('Judgment')


class JudgmentAnalysis(Process):

    """生成错误库，有需要时可以使用

    """

    def to_ot_process_error(self, old, todat):
        """此方法用于写库，如有需求写入新库可以调用此方法。

        """

        print old.id, old.url
        olds = Otraw
        print "[Analysis to %s] time: %s " % (todat, time.strftime('%y-%m-%d %H-%M-%S'))
        if ('openlaw' in old.url):
            self.point.set_tablename(Open)
            self.point.set_filter(filter='id = %s' % old.parent_id, limit=1)

            old_data = self.point.query()

        else:
            self.point.set_tablename(olds)
            self.point.set_filter(filter='id = %s' % old.parent_id, limit=1)

            old_data = self.point.query()
        if not old_data:
            return

        old_data = old_data[0]

        analy = Analyse()
        analy.text = old_data.content_all

        _header, part, content, case_sign = analy.split_to_four_parts()

        #: 开始检测数据错误
        ero = Judgment_checking(_header, part, content, case_sign)

        #: 检查案由
        ero.Checking_anyou(old.anyou)

        #: 检查原告被告
        ero.Checking_people(old.plaintiff, old.defendant)

        #: 检查原告被告律师
        ero.Checking_lawyer(old.plaintiff_lawyers, old.defendant_lawyers)

        #: 检查署名信息
        ero.Checking_sign()

        if ero.errors:
            # return list(set(ero.errors))
            for item in ero.errors:
                new = ot_process_error()
                new.judge_id = old.id
                new.action = item[0]
                new.error = item[1]
                new.user_name = 'System'
                new.addtime = str(int(time.time()))
                point = insert_database(
                    'inspection', tablename=todat, editor=new)
                point.update()
        return


def Web_Api_Error(Judgmentid):
    """提供WEB API接口使用 GET方法

    """
    Session_to = returns_session('Judgment')
    session = Session_to()
    result = ot_judge_base

    result_data = session.query(result).filter('id = %s' % Judgmentid).first()
    if not result_data:
        return {'Error': u'没有找到文书ID的相应记录', 'status': -3}

    if 'openlaw' in result_data.url:
        to = Open
    else:
        to = Otraw
    try:
        data = session.query(to).filter(
            'id = %s' % result_data.parent_id).first()
    except SQLAlchemyError:
        return {'Error': u'相关的详细数据', 'status': -4}
    finally:
        session.close()
    if data:
        analy = Analyse()
        analy.text = data.content_all
        _header, part, content, case_sign = analy.split_to_four_parts()
        ero = Judgment_checking(_header, part, content, case_sign)

        #: 检查案由
        ero.Checking_anyou(result_data.anyou.decode('utf8'),
                           result_data.type.decode('utf8'))

        #: 检查原告被告
        ero.Checking_people(result_data.plaintiff.decode('utf8'),
                            result_data.defendant.decode('utf8'))

        #: 检查原告被告律师
        ero.Checking_lawyer(result_data.plaintiff_lawyers.decode('utf8'),
                            result_data.defendant_lawyers.decode('utf8'))

        #: 检查署名信息
        ero.Checking_sign()

        #: 检查地区信息
        ero.Checking_area(result_data.areacode,
                          result_data.department.decode('utf8'))

        #: 审理机构检查
        ero.Checking_department(result_data.department.decode('utf8'))

        ero.errors['status'] = 0
        if ero.errors:
            return ero.errors
        else:
            return {'Error': u'没有错误信息', 'status': 0}
    else:
        return {'Error': u'没有找到相关的记录', 'status': -4}


def Web_Api_On_Check(**keyword):
    """提供POST方法， 可供分析字段

    """

    Session_to = returns_session('Judgment')
    session = Session_to()
    result = ot_judge_base

    result_data = session.query(result).filter(
        'id = %s' % keyword['pid']).first()
    if not result_data:
        return {'Error': u'没有找到文书ID的相应记录', 'status': -3}
    if 'openlaw' in result_data.url:
        to = Open
    else:
        to = Otraw
    try:
        data = session.query(to).filter(
            'id = %s' % result_data.parent_id).first()
    except SQLAlchemyError:
        return {'Error': u'相关的详细数据', 'status': -4}
    finally:
        session.close()
    if data:

        #: 载入分析方法
        analy = Analyse()
        analy.text = data.content_all

        #: 将文本分为4个段落
        _header, part, content, case_sign = analy.split_to_four_parts()
        ero = Judgment_checking(_header, part, content, case_sign)

        #: 检查案由
        ero.Checking_anyou(keyword['anyou'], result_data.type)

        #: 检查原告被告
        ero.Checking_people(keyword['plaintiff'], keyword['defendant'])

        #: 检查原告被告律师
        ero.Checking_lawyer(
            keyword['plaintiff_lawyers'], keyword['defendant_lawyers'])

        #： 载入发过来的署名信息买，存入一个字典当中
        keys = {}
        keys['chief_judge'] = keyword['chief_judge']
        keys['judge'] = keyword['judge']
        keys['acting_judges'] = keyword['acting_judges']
        keys['clerk'] = keyword['clerk']
        #: 检查署名信息
        #: ero.Checking_sign(keys) 可不传递keys传递时会给出更加精确的判断
        ero.Checking_sign(keys)

        #: 检查地区信息
        ero.Checking_area(
            keyword['areacode'], result_data.department.decode('utf8'))

        if ero.errors:
            # status=0 必须放在这里！不然其他程序调用时就不是那么好判断了
            ero.errors['status'] = 0
            return ero.errors
        else:
            return {'Error': u'没有错误信息', 'status': 0}
    else:
        return {'Error': u'没有找到相关的记录', 'status': -4}


def run():
    """JudgmentAnalysis

    args <数据库名称>
    filter <条件>

    """
    for i in range(13038, 108222, 50):
        p = JudgmentAnalysis(
            'inspection', filter='id >= %s and id <= %s ' % (i, i + 50))
        p.runing_works()
