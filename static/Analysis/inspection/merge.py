#!/usr/bin/python
# -*- coding:utf-8 -*-

# Copyright (c) 2015 yu.liu <showmove@qq.com>
# All rights reserved

# pylint:disable-all


""" 把各分析库汇总到ot_judge_base """

# $Id$
__author__ = [
    'Tanggu <luckytanggu@163.com>',
]
__version__ = '$Revision: 0.1 $'


from . import *
from hashlib import md5
import arrow
from urlparse import urlparse
from wytool.utils.area import IdentArea
from wytool import dbtool

from flcrawl.warehouses.judgment.court_gov_cn import *
from flcrawl.warehouses.judgment.merge import *
from . import JudgmentProcesser

from pybamboo import Bamboo

import json
from flcrawl.config import DB_URL

from flcrawl.processers.judgment.lawyer import id_or_name,  local_lawyers, lawyers


bamboo = Bamboo()
LAWYER_TYPE = (u"委托代理人", u"代理人", u"指定代理人", u"指定委托代理人", u"指定辩护人", u"辩护人")
MODLE = sys.argv[2].split(".")[-1]

#import pdb
# pdb.set_trace()
DATAS = lawyers(mode=MODLE)
OLD_ID = id_or_name(fname="./keyword/oldid.json", mode="read")
OLD_ID = set(OLD_ID["id"])


def check_case_type_id():
    """ 216库中查找案件类型的id """

    dbarg = {"sql_host": "192.168.1.216", "sql_user": "dep_judge",
             "sql_db": "judge_center", "sql_pass": "LiALSwccQ89iScMqZt", "sql_port": 33669}

    sql = "select name, value from ot_judge_dict"
    res, desc = dbtool.exec_sql(dbarg, sql)
    if desc and desc[0]:
        return desc

TYPE_ID = check_case_type_id()


class CourtGovCnMergeProcesserLawyer(JudgmentProcesser):

    """ 按好律师表中的律师名单抽取到正式库 """

    from_warehouses = (ot_rawdata_judgement_court_gov_cn_old,)
    to_warehouses = (ot_judge_base,)

    sql_ml = 'select parent_id from ot_judge_base where come_from="CourtGovCnMergeProcesserLawyer" order by parent_id desc limit 1'

    startid = DATAS

    case_mode = (u'民事判决书', u'民事调解书', u'仲裁裁决书', u'仲裁调解书', u'刑事判决书', u'行政判决书',
                 u"民事裁定书", u"国家赔偿决定书",  u"刑事裁定书", u"刑事附带民事判决书", u"刑事附带民事裁定书",
                 u"刑事附带民事调解书", u"刑事再审判决书", u"强制医疗决定书", u"行政裁定书", u"行政附带民事判决书",
                 u"行政附带民事调解书", u"行政赔偿调解书")

    def on_init(self):
        """ 初始化
        """

        self.cause_of_action_id = {}
        self.cause_of_actions = []
        engine = create_engine(DB_URL, echo=False)

        with engine.connect() as conn:
            old_anyou = conn.execute(
                "select anyou_name,new_id,max(level) from ot_judge_anyou_old group by anyou_name").fetchall()

            new_anyou = conn.execute(
                "select anyou_name,id,max(level) from ot_judge_anyou group by anyou_name").fetchall()

            self.replace_keywords = dict(conn.execute(
                "select keyword,keyword_replace from ot_judge_keyword_filter").fetchall()
            )

        self.cause_of_action_id.update(dict((x[0], x[1]) for x in old_anyou))
        self.cause_of_action_id.update(dict((x[0], x[1]) for x in new_anyou))

        self.cause_of_actions.extend(
            sorted(set(x[0] for x in new_anyou), lambda x, y: len(y) - len(x)))
        self.cause_of_actions.extend(
            sorted(set(x[0] for x in old_anyou), lambda x, y: len(y) - len(x)))

        # 获取地区识别模块
        self.area_parse = IdentArea('192.168.3.234', 7779, 'area')

        dbarg = {"name": "uc_area", "sql_host": "192.168.1.216", "sql_user": "user_cloud",
                 "sql_db": "user_cloud_db", "sql_pass": "YgFD762EWSXijh65", "sql_port": 57789}

        sql = 'select id,  province, city,country, grade from uc_area'

        res, desc = dbtool.exec_sql(dbarg, sql)

        """
        self.area_parse.set_areas(
            [(result['id'], result['province'], result['city'],
            result['country'])
            for result in desc])
        """
        for result in desc:
            if result['grade'] == 2:
                self.area_parse.set_area(
                    result['country'], result['id'], 2, result['city'])
            if result['grade'] == 1:
                self.area_parse.set_area(
                    result['city'], result['id'], 1, result['province'])
            if result['grade'] == 0:
                self.area_parse.set_area(
                    result['province'], result['id'], 0, '')

    def check_lawyer(self,  old):
        """ 查找该裁判文书中的律师是否要匹配的 """

        #import pdb
        # pdb.set_trace()

        # 该裁判文书中的所有人姓名
        peoples = bamboo.people_name(old.content)

        pp = False
        name = ""
        for k in old.lawyers_attr.keys():
            # {原告:[(name, firm),(...)]， 被告: ...}
            if not old.lawyers_attr[k]:
                continue
            for v in old.lawyers_attr[k]:
                if v[0] in DATAS[0]:
                    print v[0].encode("utf8")
                    pp = True
                    name = v[0]
                    return (pp, name)
        if not pp:
            for lawyer in DATAS[0]:
                # 先全文模糊查找该律师名是否存在, 若存在则逐行查找, 不存在则退出此次循环, 换一律师
                if lawyer in peoples:
                    # 过滤不存在律师名的行
                    lines = filter(
                        lambda line: lawyer in line, old.content.split('\n'))
                    for line in lines:
                        num = line.index(lawyer)
                        # 律师xx  xx律师
                        if u"律师" in line[num - 2:num] or u"律师" in line[len(lawyer) + num:len(lawyer) + num + 2]:
                            print lawyer.encode("utf8")
                            pp = True
                            name = lawyer
                            return (pp, name)
                        for item in LAWYER_TYPE:
                            if (item in line) and (lawyer in line[line.index(item) + len(item):line.index(item) + len(item) + len(lawyer)]):
                                print lawyer.encode("utf8")
                                pp = True
                                name = lawyer
                                return (pp, name)
                else:
                    continue
        return (pp, name)

    def to_ot_judge_base(self, old):
        """ 抽取字段 """

        #import pdb
        # pdb.set_trace()

        print old.url

        # if self.p_type and old.id > self.pages:
        #    os._exit(0)

        if MODLE == "CourtGovCnMergeProcesserLawyer":
            data = {"max": old.id, "up": DATAS[2]}
            id_or_name(fname="./keyword/id.json", mode="write", indata=data)

        if MODLE == "CourtGovCnMergeProcesserLawyerUp":
            if DATAS[1] < old.id:
                print "更新模式父id已大于普通模式下的父id, 请使用非更新模式进行抽取!"
                os._exit(0)
            elif DATAS[1] >= old.id:
                data = {"max": DATAS[1], "up": old.id}
                id_or_name(
                    fname="./keyword/id.json", mode="write", indata=data)

        # 如果此id已抽取过, 则直接返回
        if old.id in OLD_ID:
            return

        for attr in ('content', 'case_sign', 'case_type', 'department', 'end_date'):
            if getattr(old, attr) is None:
                return

        # 只分析以下类型的裁判文书
        if old.case_type not in self.case_mode:
            return

        #import pdb
        # pdb.set_trace()
        # 如果没有匹配的律师, 则直接返回
        result = self.check_lawyer(old)
        if not result[0]:
            return
        else:
            OLD_ID.add(old.id)
            data = {"id": list(OLD_ID)}
            id_or_name(fname="./keyword/oldid.json", mode="write", indata=data)

        new = ot_judge_base()

        new.content = '<p>' + '</p><p>'.join(old.content.split('\n')) + '</p>'
        new.content_md5 = md5(new.content.encode('utf8')).hexdigest()
        new.case_sign = '<p>' + \
            '</p><p>'.join(old.case_sign.split('\n')) + '</p>'

        new.case_type = old.case_type

        for item in TYPE_ID:
            if item["name"] == new.case_type.encode("gbk"):
                new.case_type_id = item["value"]
                break

        new.type = new.case_type[:-3]

        # 如果是仲裁,那属于民事
        if new.type == u'仲裁':
            new.type = u'民事'

        new.case_number = old.case_number

        new.title = re.split("\n", old.content_all)[0].strip()

        ff = False
        title = new.title
        # 先把标题中裁判文书类型文字去掉
        for item in self.case_mode:
            if item in title:
                title = title.replace(item, "")
        for ca in self.cause_of_actions:
            if ca in title:
                new.anyou = ca
                ff = True
                break
        if not ff:
            for ca in self.cause_of_actions:
                if ca in old.content_all:
                    new.anyou = ca
                    break
                else:
                    return
        new.anyou_id = self.cause_of_action_id[new.anyou]

        new.department = old.department

        new.chief_judge = old.chief_judge

        new.judge = old.judge

        new.acting_judges = old.acting_judges

        new.clerk = old.clerk

        new.plaintiff = ';'.join(
            u"%s:%s:%s" % client for client in old.clients_attr[u'原告'])
        new.plaintiff_lawyers = ';'.join(
            u"%s:%s" % lawyer for lawyer in old.lawyers_attr[u'原告'])

        new.defendant = ';'.join(
            u"%s:%s:%s" % client for client in old.clients_attr[u'被告'])
        new.defendant_lawyers = ';'.join(
            u"%s:%s" % lawyer for lawyer in old.lawyers_attr[u'被告'])

        new.procedure = old.procedure

        new.end_date = arrow.get(old.end_date, 'Asia/Shanghai').timestamp

        # 分析地区
        area = self.area_parse.ident(new.department.encode('gbk'))
        if area:
            new.areacode = area['areano']

        new.url = old.referer

        #import pdb
        # pdb.set_trace()
        # 把某某都去掉
        # new.replace_data = json.dumps(
        #    {k: v for k, v in old.replace_data.iteritems() if not re.match(ur'.*(某|X|x|\*).*', k)}
        #)

        dic = {}
        for k, v in old.replace_data.iteritems():
            if not re.match(ur".*(某|X|x|\*).*", k):
                dic.update({k: v})
        new.replace_data = json.dumps(dic)

        new.input_time = arrow.now().timestamp
        new._MASK_SYNC_V2 = datetime.now()
        new.from_host = urlparse(old.referer).hostname

        print "OK"
        # 更新该律师的裁判文书数
        if MODLE <> "CourtGovCnMake":
            sql_up = "update user_lawyer_main set count=count+1, update_datetime=%d where name='%s'" \
                % (arrow.now().timestamp, result[1].encode("utf8"))
            local_lawyers("insert", sql_up)

        return new


class CourtGovCnMergeProcesserLawyerUp(CourtGovCnMergeProcesserLawyer):
    sql_lu = 'select parent_id from ot_judge_base where come_from="CourtGovCnMergeProcesserLawyerUp" order by parent_id desc limit 1'


class CourtGovCnMake(CourtGovCnMergeProcesserLawyer):

    """ 更正模式 """

    from_warehouses = (ot_judge_base,)
    to_warehouses = (ot_judge_base,)

    sql_mk = 'select max(id) from ot_judge_base where come_from="CourtGovCnMake" limit 1'

    def to_ot_judge_base(self, old):
        """ 更正方法 """

        new = ot_judge_base()

        new.id = old.id

        #import pdb
        # pdb.set_trace()
        # 更正案由字段
        new.anyou = old.anyou

        title = old.title
        for item in self.case_mode:
            if item in old.title:
                title = title.replace(item, "")
                break

        for ca in self.cause_of_actions:
            if ca in title:
                new.anyou = ca
                break

        if new.anyou <> old.anyou:
            new.anyou_id = self.cause_of_action_id[new.anyou]
            new.input_time = arrow.now().timestamp
            new._MASK_SYNC_V2 = datetime.now()

            new.come_from = "CourtGovCnMake"

            new.merge()
