#!/usr/bin/python
# -*- coding:utf-8 -*-

# Copyright (c) 2015 yu.liu <showmove@qq.com>
# All rights reserved

"""对裁判文书进行检查. 

    一、大于4个字的当事人（律师），没有识别为机构的
    二、有原告，没被告的（或有被告，没原告的）
    三、有括号，在括号中是二个字，但不是地区的，括号中是全英文的，括号中的字，在名单外的。
    五、地区只识别到省份的
    六、行政案由没在标题中出现，民事案由没在抬头后第一段中出现的，案由不在案由库中出现的
    七、没找到抬头区，抬头区在100个字内出现，抬头区超过1000字才出现
"""

#: 载入一些基础配置变量
from configure import Area_duct, Checking_area, \
    MECHANISM, PLAIN, DEFEN, SPLIT_KEY, P_D_SUB, WHITE, CASE_SIGN, anyou_replace

#：载入分析模块
from ..inspection.analyse import Analyse

#: 载入正则模块
import re

#: 获取案由
ACTION_ID, ACTIONS, REPLACE, ANYOU_ALIAS = anyou_replace('Judgment')

#: 获取地区
AREA = Area_duct()


#: 定制错误 1-9 为基础错误 10 - 100为疑似错误 正常值0
#: 错误定制暂未使用
ERROR = {0: u'正常',
         #: 定制基本错误
         1: u'文书头部过长或者过短,请检查标题、字号、法院等信息是否正常？',
         2: u'文书台头不正确，这个错误会直接影响到对律师律所的分析,请检查律师分析是否出错',
         3: u'正文内容出错',
         4: u'署名区出错，存在不规格的署名区域',
         5: u'其他',
         #: 定制疑似错误
         10: u'原告、被告 数据可能存在问题.',
         11: u'案由可能存在问题',
         12: u'缺少审判人员信息',
         13: u'地区识别可能存在错误',
         14: u'原告律师或者被告律师存在问题',

         15: u'原告或者被告长度超过5个字符！并且不属于机构',
         16: u'原告或者被告长度低于5个字符，并且不属于个人',
         17: u'原告或者被告信息不存在于台头',
         18: u'原告律师或者被告律师不存在于台头',
         19: u'原告或者被告律师存在，不存在事务所',

         20: u'律师事务所存在问题，可能存在括号未识别的区域',
         21: u'原告或被告信息为空',
         22: u'署名信息存在多个',
         99: u'文本属性存在问题'
         }


class Judgment_checking(object):

    """检测裁判文书内容是否存在疑似错误

    """

    def __init__(self, header, part, body, footer):
        """构造函数，传递文书的4块区域进入
        args: 
            header, part , body , footer

        """
        self.header = header
        self.part = part
        self.body = body
        self.footer = footer

        #: 在构造函数中做一些最基本的判定
        #: self.errors = [] 数组存储模式
        self.errors = {}
        # if len(self.header) > 10000 or len(self.header)< 10:
        # if len(self.header.split('\n')) > 5 or len(self.header.split('\n')) < 2:
        # : 头部不可能大于5行 且不可能小于两行
        #    self.errors['title'] = u'文书头部出现问题'
        header = filter(lambda x: x.strip() != '', self.header.split('\n'))

        if len(header) > 6 or len(header) < 2:
            self.errors['title'] = u'文书头部出现问题'

        if (not self.part) or filter(lambda x: x in self.part, SPLIT_KEY):
            #: 判断抬头是否为空并且是否存在正文的内容
            self.errors['content'] = u'台头出现问题'

        if not self.body:
            #: 内容不能为空
            self.errors['content'] = u'内容出现问题'

        if (not self.footer) or len(self.footer.split('\n')) < 2:
            #: 署名不能为空,且不能小于2行
            self.errors['case_sign'] = u'文书署名问题'

        #： 调用分析人名算法
        analy = Analyse()

        #: 原、被告和律师
        clients_attr, lawyers_attr = analy.guess_clients_lawyers(
            part.split('\n'))
        self.attr = {}

        #: 获取原被告与律师信息
        try:
            clients_attr[u'原告'] = list(set(clients_attr[u'原告']))
            clients_attr[u'被告'] = list(set(clients_attr[u'被告']))
            lawyers_attr[u'原告'] = list(set(lawyers_attr[u'原告']))
            lawyers_attr[u'被告'] = list(set(lawyers_attr[u'被告']))
        except:
            pass

        self.attr['plaintiff'] = ''
        self.attr['defendant'] = ''
        self.attr['plaintiff_lawyers'] = ''
        self.attr['defendant_lawyers'] = ''

        if clients_attr[u'原告']:
            self.attr['plaintiff'] = ';'.join(
                u"%s:%s:%s" % client for client in clients_attr[u'原告'])
        if clients_attr[u'被告']:
            self.attr['defendant'] = ';'.join(
                u"%s:%s:%s" % client for client in clients_attr[u'被告'])
        if lawyers_attr[u'原告']:
            self.attr['plaintiff_lawyers'] = ';'.join(
                u"%s:%s" % lawyer for lawyer in lawyers_attr[u'原告'])
        if lawyers_attr[u'被告']:
            self.attr['defendant_lawyers'] = ';'.join(
                u"%s:%s" % lawyer for lawyer in lawyers_attr[u'被告'])

    def Checking_anyou(self, anyou, Types=''):
        """检查案由是否存在错误
        args:
            anyou = 文书案由

        returns: 

            None
        [ERROR]
        #1: 案由不存在头部与首行
        #2: 案由属于行政，但不存在于标题
        #3: 案由不属于行政，不存在于正文
        #4: 案由不属于行政，案由存在正文，却与标题不等
        #5: 案由不属于行政, 标题或正文中出现多个案由

        ##############

        #6：案由不属于行政, 标题没有案由，案由不等于台头案由
        #7: 案由不属于行政，台头没有案由。
        """

        text = "".join(self.body.split('\n')[0:2])
        #Plush = re.findall("|".join(SPLIT_KEY), text)

        # if Plush:
        Checking_data = self.body.split('\n')[0]
        # else:
        #    Checking_data = text.split('\n')[0]

        if (anyou not in Checking_data) and (anyou not in self.header):
            self.errors['anyou'] = u'案由疑似错误 #1'
            return

        if Types == u'行政':
            if anyou not in self.header:
                self.errors['anyou'] = u'案由疑似错误 #2'
                return
        else:
            Pulas1 = {}
            Pulas2 = {}
            if anyou not in Checking_data:
                self.errors['anyou'] = u'案由疑似错误 #3'
                return
            else:
                ay_1 = filter(
                    lambda x: x in "".join(self.header.split('\n')), ACTIONS)
                ay_2 = filter(lambda x: x in Checking_data, ACTIONS)

                if ay_1 and ay_2:
                    # for item in ay_1:
                    #    Pulas1[len(item)] = item
                    for item in ay_2:
                        Pulas2[len(item)] = item
                    #: 设置一个变量来对案由进行判断
                    check_anyou = Pulas2[max(Pulas2.keys())]
                    #: 检查别名
                    if ANYOU_ALIAS.has_key(check_anyou):
                        check_anyou = ANYOU_ALIAS[check_anyou]

                    if anyou != check_anyou:
                        print anyou, check_anyou
                        self.errors['anyou'] = u'案由疑似错误 #4'
                        return
                    #: if ay_1[0] != ay_2[0]:
                    # :     self.errors['anyou'] = u'案由疑似错误 #4'
                    #:     return

    def Checking_lawyer(self, plai, defen):
        """检查律师

        args:
            plai = 原告律师
            defen = 被告律师

        returns: 
             None

        """
        def _context_plai_defen(text, value, attr):
            #: 作为一个传递的方法

            for item in text.split(';'):

                if item.strip() == '' or item.strip() == u'无':
                    if self.attr[attr].strip() != '':
                        self.errors[attr] = u'遗漏律师'
                        return
                    continue

                item = item.split(':')
                Peo = item[0]
                try:
                    types = re.sub(u':|：|\s+', '', item[1])
                    if not types:
                        self.errors[attr] = u'遗漏律所'
                        return

                except IndexError:
                    self.errors[attr] = u'遗漏律所'
                    return
                #: 检查姓名是否存在于台头
                if Peo not in self.part:
                    self.errors[attr] = u'律师疑似存在问题'
                    return
                if types not in self.part:
                    self.errors[attr] = u'律所疑似存在问题'
                    return
                for keys in self.attr:
                    if attr != keys:
                        if Peo in self.attr[keys] and (re.search('lawyers$', keys)):
                            self.errors[attr] = u'原被告律师信息存在调转问题'

                            return
                if Peo not in self.attr[attr]:
                    self.errors[attr] = u'律师存在错误信息'
                    return
                elif types not in self.attr[attr]:
                    self.errors[attr] = u'律所存在错误信息'
                    return

            if len(text.split(';')) < len(self.attr[attr].split(';')):
                self.errors[attr] = u'信息不全'
                return

        #: 判断原告被告
        for value in [[plai, u'原告律师', 'plaintiff_lawyers'], [defen, u'被告律师', 'defendant_lawyers']]:
            _context_plai_defen(value[0], value[1], value[2])

    def Checking_people(self, plai, defen):
        """检查原告被告

        args:
            plai = 原告
            defen = 被告
        returns: 
            None
        """
        def _context_plai_defen(text, value, attr):
            #: 作为一个传递的方法
            if text.strip() == '' and text.strip() == u'无':
                if self.attr[attr].strip() != '':
                    self.errors[attr] = u'人名遗漏'
                return
            for item in text.split(';'):
                if item == '':
                    continue
                item = item.split(':')
                Peo = item[0]
                try:
                    types = re.sub(u':|：|\s+', '', item[1])
                except IndexError:
                    #: self.errors.append(ERROR[99])
                    self.errors[attr] = u'属性存在问题'
                    return
                #: 检查姓名是否存在于台头
                if Peo not in self.part:
                    self.errors[attr] = u'人名不存在于台头'
                    return

                #: 检查长度是否满足需求
                if len(Peo) > 5 and types != u'机构':
                    self.errors[attr] = u'名称大于5个字，不属于机构'
                    return
                elif len(Peo) < 5 and types != u'个人':
                    self.errors[attr] = u'名称小于5个字, 不属于个人'
                    return
                for keys in self.attr:
                    #: 判断原被告是否存在调转
                    if attr != keys:
                        if Peo in self.attr[keys] and (not re.search('lawyers$', keys)):
                            self.errors[attr] = u'原被告信息存在调转问题'
                            return
                if Peo not in self.attr[attr]:
                    #: 判断人名是否存在
                    self.errors[attr] = u'人物存在错误信息'
                    return

            if len(text.split(';')) < len(self.attr[attr].split(';')):
                #: 判断长度是否相同
                #: 使用小于号是为了防止一些意外错误
                self.errors[attr] = u'信息不全'
                return
        #: 判断原告被告
        for value in [[plai, u'原告', 'plaintiff'], [defen, u'被告', 'defendant']]:
            _context_plai_defen(value[0], value[1], value[2])

    def Checking_area(self, area_code, department):
        """检查地区
        args:
            area_code  = <int areacode>
            department = <str department>
        returns:
            None

        [ERROR]
        #1： 分割的最后一个地区与识别的最后一个地区不符合
        #2： 没检查到地区存在县， 没有传递area_code
        #3： 没检查到地区存在县， 传递过来的area_code与识别的不同
        #4： 效验程序检测到存在地区，但传递值的却不存在
        #5:  标题存在地区，但是传递的是0
        """
        code = ''
        #department = department.repalce(u'自治区', '')
        area_index = filter(
            lambda x: department[x - 1] in [u'省', u'市', u'区', u'县'], range(len(department)))
        if area_index:
            if not area_code:
                self.errors[u'areacode'] = u'地区疑似错误 #4'

        area_item = filter(
            lambda x: AREA.area[x][0] == area_code, AREA.area.keys())
        if area_item:
            area_item = AREA.area[area_item[0]][1].decode('gbk')
        if area_index:
            #: 只判断他们结尾是否属于同一个地区！不属于就报错
            if len(area_index) > 1:
                addr = department[area_index[-2]: area_index[-1]]
            else:
                addr = department[0: area_index[-1]]
            addr = re.sub(u'省$|市$|县$|区$', '', addr)
            if addr not in area_item:
                self.errors['areacode'] = u'地区疑似错误 #1'
                return

    def Checking_sign(self, argv={}):
        """检查署名

        argv:
             argv = case_sign 署名人员信息

        """
        #： 用于计算复数个相同职位的人名个数
        case_key = {}
        for case in CASE_SIGN:
            case_key[case] = 0

        for item in self.footer.split('\n'):
            for case in CASE_SIGN:
                if case in item:
                    case_key[case] += 1

        sign_name = [u'审判长', u'审判员', u'代理审判员', u'书记员', u'代书记员', u'见习书记员']
        case_sign_name = []
        for item in self.footer.split('\n'):
            #： 获取署名区除人名陪审员以外所有人名列表以及日期
            if re.search('|'.join(sign_name), item):
                name = re.split('|'.join(sign_name), item)
                if name:
                    case_sign_name.append("".join(name))

        #: 判断人名是否存在
        for item in argv:
            if argv[item] == '':
                self.errors[item] = u'不存在值'
                # continue
                return
            if argv[item] == u'无':
                continue
            text = argv[item].split(u'，')
            for t in text:
                if t not in self.footer:
                    self.errors[item] = u'疑似错误'
                    return
        case_sign = []
        if argv and case_sign_name:
            old_case = filter(lambda x: x != u'无' or x != '', argv.values())
            for item in old_case:
                case_sign.extend(item.split(','))
            #： 判断人名是否存在遗漏.
            for item in case_sign_name:
                if item not in case_sign:
                    self.errors['clerk'] = u'人名遗漏'
                    return

    def Checking_department(self, department):
        """检查审理机构

        """
        if u'省' not in department and u'自治区' not in department:
            if not re.match(u'北京|上海|天津|重庆', department):
                self.errors['department'] = u'审理机构少了省'
