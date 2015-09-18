#!/usr/bin/python
# -*- coding:utf-8 -*-

# Copyright (c) 2015 yu.liu <showmove@qq.com>
# All rights reserved

"""Analysis of data


"""


try:
    from extend.Processer.process import Process
except ImportError:
    from NewProject.extend.Processer.process import Process

from model.orm.Judgment import ot_judgment_inspection, ot_judge_inspection
from model.Loading import insert_database

import time
import json
import re
########################################################################


class JudgmentAnalysis(Process):

    #bamboo = Bamboo()
    def _check_lawyer_in_line(self, line):

        law_firm = ''
        if (u'律师事务所' in line) or (u'事务所律师' in line) or (u'援助中心' in line):

            text = line.split(u'。')
            text = text[0].split(u'，')
            for item in text:
                # if item in u'事务所':
                if (u'事务所' in item) or (u'援助中心' in item):
                    law_firm = item
                    break

            if (law_firm.find(u'事务所') > 3 or law_firm.find(u'援助中心') > 3):

                if u'援助中心' in law_firm:

                    law_firm = law_firm[0: law_firm.find(u'援助中心')] + u'援助中心'
                    law_firm = law_firm.replace(u'：', '').replace(u':', '')

                elif u'事务所' in law_firm:

                    law_firm = law_firm[0: law_firm.find(u'事务所')] + u'事务所'
                    law_firm = law_firm.replace(u'：', '').replace(u':', '')

            else:
                law_firm = re.split(
                    ur'[， ,]', line.split(u'律师事务所', 1)[0][::-1], 1)[0][::-1] + u'律师事务所'

            if u'系' in law_firm or law_firm.startswith(u'是'):
                if u'系' in law_firm:
                    law_firm = law_firm.split(u'系', 1)[1]

                elif law_firm.startswith(u'是'):
                    law_firm = law_firm.replace(u'是', '')

        if law_firm == '' and (law_firm == u'律师事务所' or law_firm == u'援助中心'):
            law_firm = self.bamboo.insitution_group(line)
            law_firm = law_firm and law_firm[0] or ''

        def _get_name(line):
            "获取委托代理人"
            text = line.split(u'。')
            text = text[0].split(u'，')[0]
            result = ''
            if re.search(u'代理人(.+)', text):
                result = re.findall(u'代理人(.+)', text)[0]
            elif re.search(u'辩护人(.+)', text):
                result = re.findall(u'辩护人(.+)', text)[0]
            else:
                return re.split(ur'[^\u4e00-\u9fa5、]',
                                re.sub(ur'^指定辩护人|^委托代理人|^辩护人|^指定代理人|^代理人|^指定委托代理人([^\u4e00-\u9fa5]|有)*', '', line, 1))[0].split(u'、')[0]
            if result.strip() != '':
                result = result.replace(u'：', '').replace(u':', '')

                return [result]

        lawyers_name = _get_name(line)

        people = lawyers_name[0].split(u'、')

        lawyers_double_name = []
        if len(people) > 1:
            lawyers_double_name = people
        # 大于4的就不是正常名字了，还需要bamboo来处理下
        else:
            if not lawyers_name or len(lawyers_name[0]) < 2 or len(lawyers_name[0]) > 4:
                lawyers_name = self.bamboo.people_name(line.replace(' ', ''))
        results_lawyers = []
        if lawyers_name:
            if lawyers_double_name:
                for item in lawyers_double_name:
                    #results_lawyers.append((item[0], lawyers_name[0]))
                    if item != '':
                        if type(item) is list and type(lawyers_name) is list:
                            results_lawyers.append((item[0], lawyers_name[0]))
                        else:
                            if type(lawyers_name) is list:
                                results_lawyers.append((item.replace(u'：', '').replace(
                                    u':', ''), lawyers_name[0].replace(u'：', '').replace(u':', '')))
                            elif type(item) is list:
                                results_lawyers.append((item[0].replace(u'：', '').replace(
                                    u':', ''), lawyers_name.replace(u'：', '').replace(u':', '')))
                            else:
                                results_lawyers.append((item.replace(u'：', '').replace(
                                    u':', ''), lawyers_name.replace(u'：', '').replace(u':', '')))

                return results_lawyers
            else:
                return [(lawyers_name[0], law_firm)]

        else:
            return []

    def _check_client_in_line(self, line):
        """判断这一行是否有当事人，有则分析其属性，并返回。"""

        line = re.sub(u'（[^\w ^）]{3,100}）', '', line)
        re_com = re.compile(u'''^原告|^上诉人|^申诉人|^起诉人|^公诉机关|^申请再审人|^再审申请人|^被上诉人
        |^被申诉人|^被起诉人|^被告|^申请人|^被申请人|^原公诉机关|^原告人|^附带民事诉讼原告人|^第.原告|^第.被告|^被告.：|^原告.：|^附带民事诉讼原告人''')
        if re.match(re_com, line):
            text = line.split(u'。')
            text = re.split(u'，|,', text[0])
            text = re.sub(re_com, '', text[0])
            # 去掉各种可能的字符
            #text = re.sub(u'。|：|:|；|;', '', text)
            text = text.replace(u'：', '').replace(u':', '')

            if self.bamboo.insitution_group(text):
                return (text, u'机构', '')

            elif self.bamboo.people_name(text):

                if u'公司' in text or u'医院' in text or u'事务所' in text or u'集团' in text or u'学院' in text:
                        # bamboo可能分析出一些机构带有人名的情况，所以只能做一些肯能的判断
                    return (text, u'机构', '')

                # return (text[1], u'个人', '')

                if len(text.split(u'、')) > 1:
                    text = text.split(u'、')
                    people = []
                    for im in text:
                        people.append((im, '个人', ''))
                    # return [(text[0], u'个人', ''),(text[1], u'个人', '')]

                result = re.search(u'[,|，]([男|女])[,|，|。]', line)
                sex = result and result.groups()[0] or ''
                if len(text) > 1:
                    return (text, u'个人', sex)
                else:
                    return (text, u'个人', sex)
            else:
                if (len(text) > 10 and len(text) < 25) or u'医院' in line or \
                   u'公司' in line or u'机关' in line or u'律所' in line or u'商贸中心' in line or u'学院' in line:
                    return (text, u'机构', '')
                elif len(text) > 1 and len(text) <= 10:
                    result = re.search(u'[,|，]([男|女])[,|，|。]', line)
                    sex = result and result.groups()[0] or ''
                    return (text, u'个人', sex)
                else:
                    if text != '':
                        result = re.search(u'[,|，]([男|女])[,|，|。]', line)
                        sex = result and result.groups()[0] or ''
                        if sex != '':
                            return (text, u'个人', sex)
                        elif u'公司' in line or u'机关' in line or u'律所' in line or u'医院' in line:
                            return (result, u'机构', '')
                        else:
                            return (text, u'个人', sex)
                    # else:
                    #    return []
        names = self.bamboo.people_name(line)
        institutions = self.bamboo.insitution_group(line)

        if (institutions and names and names[0] in institutions[0]) \
                or \
                (institutions and not names):

            return (institutions[0], u'机构', '')

        # 如果有名字出现，则判断为个人 返回机构列表
        elif names:
            # 尝试分析性别
            result = re.search(u'[,|，]([男|女])[,|，|。]', line)
            sex = result and result.groups()[0] or ''
            if len(names) > 1:
                return (names[0], u'个人', sex)
            else:
                return (names[0], u'个人', sex)
        # 同时没有机构名和人名，有可能是bamboo分析不出，我们返回未知 返回人名列表
        else:
            return []

    def to_ot_judge_inspection(self, old, todat):

        new = ot_judge_inspection()

        new.judgmentid = old.id

        people = [u'原告', u'被告', u'原告律师', u'被告律师',
                  u'委托代理人', u'', u'上诉人', u'被上诉人']
        content = []
        for item in old.content.replace("<p>", '').split("</p>"):
            if (item.endswith(u'书') or
                    item.endswith(u'法院') or
                    item.startswith(u'提交时间') or
                    item.endswith(u'号') or
                    re.match(u'.+(一|二|三|四|五)庭$', item)):
                continue
            else:
                content.append(item)

            if (u'一案' in item) or (u'诉状' in item) or (u'提起公诉' in item) or \
                    (u'检察院指控' in item) or (u'立案执行' in item) or (u'提起诉讼' in item) or (u'提起上诉' in item) \
                    or (u'诉至本院' in item) or (u'本院受理' in item):
                break
        lawyer = {u'plai': [], u'defen': []}
        lawyer_per = {u'plai': [], u'defen': []}
        frims = []
        checking = {u'原告': 0, u'被告': 0}

        for item in content:
            # if re.match(u'代理人|辩护人|律师|律所|顾问', item):
            if u'代理人' in item or u'辩护人' in item or u'律师' in item:
                frim = self._check_lawyer_in_line(item)

                if checking[u'原告'] == 1:
                    for firm in frim:
                        try:
                            lawyer['plai'].append(firm[0] + ':' + firm[1])
                        except TypeError:
                            return
                        frims.append(firm[1])

                    checking[u'原告'] = 0
                elif checking[u'被告'] == 1:
                    for firm in frim:
                        lawyer['defen'].append(firm[0] + ':' + firm[1])
                        frims.append(firm[1])
                    checking[u'被告'] = 0

            elif re.search(u'^原告|^上诉人|^申诉人|起诉人|^公诉机关|申请再审人|再审申请人|^申请人|^第.原告|^原告.：|^附带民事诉讼原告人', item):
                checking[u'原告'] = 1
                law = self._check_client_in_line(item)
                if type(law) is list:
                    for pl in law:
                        lawyer_per['plai'].append(pl[0])
                else:
                    lawyer_per['plai'].append(law[0])
                if law[1] == u'机构':
                    frims.append(law[0])
            elif re.search(u'被上诉人|被申诉人|被起诉人|^被告|被申请人|^原公诉机关|^第.被告|^被告.：|^附带民事诉讼被告人', item):
                checking[u'被告'] = 1
                law = self._check_client_in_line(item)
                if type(law) is list:
                    for pl in law:
                        lawyer_per['defen'].append(pl[0])
                else:
                    lawyer_per['defen'].append(law[0])

                if law[1] == u'机构':
                    frims.append(law[0])
        try:
            lawyer_per['plai'] = list(set(lawyer_per['plai']))
        except TypeError:
            return
        lawyer_per['defen'] = list(set(lawyer_per['defen']))
        lawyer['plai'] = list(set(lawyer['plai']))
        lawyer['defen'] = list(set(lawyer['defen']))
        frims = list(set(frims))
        # if type(frims) is list:
        try:
            frims.remove('')
        except ValueError:
            pass
        new.people = json.dumps(lawyer_per)
        new.lawyers = json.dumps(lawyer)
        new.firms = json.dumps(frims)

        # 分析署名
        #new.case_sign = old.case_sign
        sp_people = [u'审判员', u'审判长', u'人民陪审员', u'书记员',
                     u'代理审判员', u'代书记员', u'见习书记员', u'代理书记员']
        #people_key = dict(zip(sp_people, ['', '', '', '', '', '', '']))
        sp_all = []
        case_sign = old.case_sign.replace('<p>', '').split('</p>')
        for item in case_sign:
            for pl in sp_people:
                if item.startswith(pl):
                    #people_key[pl] = item.decode('utf8').replace(pl,'')
                    sp_all.append(item.replace(pl, '').replace(u'人民陪审员', ''))
        new.case_sign = ",".join(sp_all)

        point = insert_database(
            'Judgment', tablename=todat, editor=new)  # 设置添加数据
        point.insert()  # 添加数据
        return

    def to_ot_judgment_inspection(self, old, todat):
        new = ot_judge_inspection()

        new.judgmentid = old.id

        people = [u'原告', u'被告', u'原告律师', u'被告律师',
                  u'委托代理人', u'', u'上诉人', u'被上诉人']
        content = []
        for item in old.content.replace("<p>", '').split("</p>"):
            content.append(item)
            if (u'一案' in item) or (u'诉状' in item) or (u'提起公诉' in item) or \
                    (u'检察院指控' in item) or (u'立案执行' in item) or (u'提起诉讼' in item) or (u'提起上诉' in item) \
                    or (u'诉至本院' in item) or (u'本院受理' in item):
                break
        lawyer = {u'plai': [], u'defen': []}
        lawyer_per = {u'plai': [], u'defen': []}
        frims = []
        checking = {u'原告': 0, u'被告': 0}

        for item in content:
            # if re.match(u'代理人|辩护人|律师|律所|顾问', item):
            if u'代理人' in item or u'辩护人' in item or u'律师' in item:
                frim = self._check_lawyer_in_line(item)
                if checking[u'原告'] == 1:
                    for firm in frim:
                        lawyer['plai'].append(firm[0] + ':' + firm[1])
                        frims.append(firm[1])

                    checking[u'原告'] = 0
                elif checking[u'被告'] == 1:
                    for firm in frim:
                        lawyer['defen'].append(firm[0] + ':' + firm[1])
                        frims.append(firm[1])
                    checking[u'被告'] = 0

            elif re.search(u'^原告|^上诉人|^申诉人|起诉人|^公诉机关|申请再审人|再审申请人|^申请人|^第.原告|^原告.：', item):
                checking[u'原告'] = 1
                law = self._check_client_in_line(item)
                if type(law) is list:
                    for pl in law:
                        lawyer_per['plai'].append(pl[0])
                else:
                    lawyer_per['plai'].append(law[0])
                if law[1] == u'机构':
                    frims.append(law[0])
            elif re.search(u'被上诉人|被申诉人|被起诉人|^被告|被申请人|^原公诉机关|^第.被告|^被告.：', item):
                checking[u'被告'] = 1
                law = self._check_client_in_line(item)
                if type(law) is list:
                    for pl in law:
                        lawyer_per['defen'].append(pl[0])
                else:
                    lawyer_per['defen'].append(law[0])

                if law[1] == u'机构':
                    frims.append(law[0])

        lawyer_per['plai'] = list(set(lawyer_per['plai']))
        lawyer_per['defen'] = list(set(lawyer_per['defen']))
        lawyer['plai'] = list(set(lawyer['plai']))
        lawyer['defen'] = list(set(lawyer['defen']))
        frims = list(set(frims))
        new.people = json.dumps(lawyer_per)
        new.lawyers = json.dumps(lawyer)
        new.frims = json.dumps(frims)

        # 分析署名
        #new.case_sign = old.case_sign
        sp_people = [u'审判员', u'审判长', u'人民陪审员', u'书记员',
                     u'代理审判员', u'代书记员', u'见习书记员', u'代理书记员']
        #people_key = dict(zip(sp_people, ['', '', '', '', '', '', '']))
        sp_all = []
        case_sign = old.case_sign.replace('<p>', '').split('</p>')
        for item in case_sign:
            for pl in sp_people:
                if item.startswith(pl):
                    #people_key[pl] = item.decode('utf8').replace(pl,'')
                    sp_all.append(item.replace(pl, ''))
        new.case_sign = ",".join(sp_all)
        new.firm = ",".join(frims)
        point = insert_database(
            'Judgment', tablename=todat, editor=new)  # 设置添加数据
        point.insert()  # 添加数据
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
    p = JudgmentAnalysis('Judgment', filter='id = 96183')
    p.runing_works()
    # for i in range(13038, 104105, 20):
    #    p = JudgmentAnalysis('Judgment', filter = '%d <= id and  id <= %d ' % (i, i + 20))
    #    p.runing_works()
