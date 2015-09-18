#!/usr/bin/python
# -*- coding:utf-8 -*-

# Copyright (c) 2015 yu.liu <showmove@qq.com>
# All rights reserved

"""最新的分析类 
   针对裁判文书的规格进行分析，并且去掉了以前使用bamboo识别人名不准确的可能性，
   让识别度更高更可用。  
   主要更新：
   1.将文书分为4块. (标题、台头、内容、署名)
   2.识别律师、律所、原告、被告，字节识别文本。
   3.识别机构会使用只针对出现的机构逐个增加
   09-15:
   1.新增裁判时间.
   2.新增敏感信息
   3.新增身份证搜索
"""

# $Id$
__author__ = [
    'liuyu <showmove@qq.com>',
]
__version__ = '$Revision: 0.3 $'

#: 载入DATE模块
import datetime

#: 载入正则模块
import re

#: 载入扩展模块
from extend.Processer.utils import *
from extend.WYCrawler.utils import XPath

#: 载入配置
from configure import Area_duct, Checking_area, \
    MECHANISM, PLAIN, DEFEN, SPLIT_KEY, P_D_SUB, WHITE, OFFICE, CASE_SIGN, case_mode

#：扩展的括号分割模块
from extend.exists import Dou_text


class DateException(Exception):

    "异常类"
    pass


class Analyse(object):

    """分析方法，主要更新，去除Bamboo并且纯文本分析


    """
    area = Area_duct()
    _text = None
    text_in_lines = None
    chinese_date = re.compile(ur'(.+)年(.+)月(.+)日')

    @property
    def text(self):
        "返回文本"
        return self._text

    @text.setter
    def text(self, value):
        """把全文内容放进来。

        :param value:
        """

        value = just_readable(value)

        # 去掉所有的千奇百怪的空格
        value = strip_whitespaces(value)

        # 把多个换行都整理成一个
        value = re.sub(r'\n+', '\n', value)

        self.text_in_lines = value.split('\n')

        # 每行必须大于2个字，否则这行就会被抛弃
        self.text_in_lines = filter(
            lambda line: len(line) > 2, self.text_in_lines)
        self._text = '\n'.join(self.text_in_lines)

    def split_to_four_parts(self):
        """把self.text当做是一篇完整的文章。
        尝试把判决书分成四部分，(法院/判决书类型/文书字号)（抬头） (正文内容) (署名)

        """

        _first_part_end_index = None
        first_part, second_part, thirt_part, four_part = [], [], [], []

        for index, line in enumerate(self.text_in_lines[:6]):
            #: 去掉结尾字符存在的括号！
            line = re.sub(u'。$', '', normalize_parentheses(line))

            #: 去掉结尾字符并不能完全保证标题的正确性，就使用正则表示多种可能性
            if (line.endswith(u'书') or
                re.search(u'书\(.+\)$',  normalize_parentheses(line)) or
                re.search(u'书.+\d+$',  normalize_parentheses(line)) or
                line.endswith(u'判决') or
                    line.endswith(u'民事裁定') or
                    line.endswith(u'法院') or
                    line.startswith(u'提交时间') or
                    line.startswith(u'日期') or
                    re.search(u'第.+号$', line) or
                    re.match(u'.+(一|二|三|四|五)庭$', line)):

                _first_part_end_index = index
            else:
                break

        if _first_part_end_index is not None:
            _first_part_end_index = _first_part_end_index + 1
            first_part = self.text_in_lines[:_first_part_end_index]
        else:
            _first_part_end_index = 0

        _four_part_start_index = None
        _four_part_end_index = None

        for index, line in enumerate(self.text_in_lines[::-1]):

            if len(line) < 20 and (re.search(u'(%s|^记录)' % "|".join(CASE_SIGN), line)
                                   or re.search(u'.+年.+月.+日', line)):
                if not _four_part_end_index:
                    _four_part_end_index = len(self.text_in_lines) - index

            elif _four_part_end_index is not None:
                _four_part_start_index = len(self.text_in_lines) - index
                break
        if _four_part_start_index is not None and _four_part_end_index is not None:
            four_part = self.text_in_lines[
                _four_part_start_index:_four_part_end_index]
            thirt_part = self.text_in_lines[
                _first_part_end_index:_four_part_start_index]

        else:
            thirt_part = self.text_in_lines[_first_part_end_index:]

        for index, line in enumerate(thirt_part):
            if index > 1:
                #： 直接获取分割列表！然后进行检查
                Splitn = filter(lambda x: x in line, SPLIT_KEY)
                if Splitn or re.search(u'^原告.+诉.+', line):
                    _second_part_end_index = index
                    second_part = thirt_part[:index]
                    thirt_part = thirt_part[index:]
                    break

        result = ['\n'.join(part) for part in (
            first_part, second_part, thirt_part, four_part)]

        # 处理署名
        result[3] = normalize_numeric(
            result[3].replace(u'员', u'员 ').replace(u'审判长', u'审判长 '))
        result[3] = result[3].replace(u'本案判决所依据的相关法律', '')
        return result

    def guess_clients_lawyers(self, part):
        """根据内容分析出原告被告和其代理律师的信息

        :param content:
        :return: :rtype:
        """
        if isinstance(part, str):
            part = part.split('\n')
        clients = {u'被告': [], u'原告': []}
        lawyers = {u'被告': [], u'原告': []}

        def _check_client_in_line(line):
            """判断这一行是否有当事人，有则分析其属性，并返回。"""

            #: 先定义一个正则表达式，把所有被告原告可能的形式都写出来
            re_com = P_D_SUB
            if re.match(re_com, line):
                text = line.split(u'。')
                text = re.split(u'，|,', text[0])
                text = re.sub(re_com, '', text[0])
                #: 去掉各种可能的字符
                #: text = re.sub(u'。|：|:|；|;', '', text)
                #: 貌似使用Replace会出人意料的快和准确
                text = text.replace(u'：', '').replace(u':', '')
                if filter(lambda x: x in text, MECHANISM):
                    return (text, u'机构', '')
                else:
                    #: 写完之后居然发现这样的重复使用了代码！
                    #: 可在下个版本修订吧
                    #：主要还是去掉一些重复和代码简介吧
                    if len(text.split(u'、')) > 1:
                        text = text.split(u'、')
                        Plural = []
                        for item in text:
                            Plural.append((item, u'个人', ''))
                        return Plural
                    result = re.search(u'[,|，]([男|女])[,|，|。]', line)
                    if result:
                        sex = result and result.groups()[0] or ''
                        return (text, u'个人', sex)
                    else:
                        #: 感觉判断text的长度非常不靠谱，但是加上了后面的机构的话！过多的重复代码，这样真的好吗？
                        if (len(text) > 10 and len(text) < 25) or filter(lambda x: x in text, MECHANISM):
                            return (text, u'机构', '')
                        #: 反正不管你是阿拉伯人还是非洲人！如果你长过了10个字符的名称我就不记录你了。
                        elif len(text) > 1 and len(text) <= 10:
                            return (text, u'个人', '')

                        else:
                            return (text, u'未知', '')
            else:
                # return (text, u'未知', '')
                return None

        expect_whose_lawyers = None
        #: 定义删除括号内的内容
        #: 扩展， \(被告\)可增加任意 例如： \(原审原告\)
        #: 排除， \([^可能需要的东西]\)
        #: 增加,  \([可能删除的东西]\)
        #: sub_line_text = re.compile(u'''\([^\w ^\)]{3,100}\)|\(被告\)|\(原告\)|（[^\w ^）]{3,100}）
        #:                               |\([^\w ^\)]{3,100}\d+\)|（[^\w ^）]{3,100}\d+）
        #:                               |\([0-9a-zA-Z]+[\W ^\)]{3,100}[0-9a-zA-Z]+\)|（[0-9]+[\W ^）]{3,100}[0-9a-zA-Z]+）
        #:                               |\([a-zA-Z，\,]+\)|（[a-zA-Z，\,]+）
        #:                               |\([\W ^\)]+[a-zA-Z0-9]+-[a-zA-Z0-9]+\)|（[\W ^）]+[a-zA-Z0-9]+-[a-zA-Z0-9]+\）
        #:                               |\(\d+[\W ^\)]+、[a-zA-Z0-9]+[\W ^\)]+\)|（\d+[\W ^\)]+[\W ^）]+、[a-zA-Z0-9]+[\W ^）]+）
        #:                               |\([\W ^\)]+[a-zA-Z0-9]+-[a-zA-Z0-9]+，[\W ^）]+\)|（[\W ^）]+[a-zA-Z0-9]+-[a-zA-Z0-9]+，[\W ^）]+\）''')
        #: 需要修正的正则表达式
        #: sub_line_text = re.compile(u'\(.+[^\(]\)|（.+[^（]）')
        #: 思考如何删除5个以上的呢？
        for line in part:
            #: 开始分析每一行了。
            #: line = re.sub(sub_line_text, '', normalize_parentheses(line))
            #: 这里就不能使用删除了
            #: Purs = re.findall(sub_line_text, line)
            #: 正则还是不理想，只能用一个方法来区分括号内容了
            #: line = line.replace('(','（').replace(')','）')
            Purs = Dou_text(line)
            #: 使用地区库来进行判断吧
            for areas in Purs:
                if not Checking_area(re.sub(u'\(|\)|（|）', '', areas).encode('utf8')):
                    #: 白名单就在这里判断吧
                    if re.sub(u'\(|\)|（|）', '', areas) in WHITE:
                        continue
                    line = line.replace(areas, '')

            if (u'代理人' not in line) and (u'辩护人' not in line) and (u'委托代表人' not in line):
                #: 分析原告被告.
                #: 总觉得这种正则就应该写成compile直接往配置文件里面写,这回让代码更美观把
                #: re.compile()
                #: 需要的时候总能调用，并且加上注释。
                if re.search(DEFEN, line):
                    client = _check_client_in_line(line)
                    if isinstance(client, list):
                        clients[u'被告'].extend(client)
                    else:
                        if client != None:
                            clients[u'被告'].extend([client])

                    expect_whose_lawyers = 'defendant'

                elif re.search(PLAIN, line):
                    client = _check_client_in_line(line)
                    if isinstance(client, list):
                        clients[u'原告'].extend(client)
                    else:
                        if client != None:
                            clients[u'原告'].extend([client])

                    expect_whose_lawyers = 'plaintiff'

            # or u'律所' in line #or u'顾问' in line)):
            elif (re.search(u'辩护人|代理人|委托代表人', line) and (u'律师' in line)):

                #: 分析律师数据
                #: 如果需要去掉每行的括号！又要保证地区存在呢？
                #: line = re.sub(u'\([^\w ^\)]{3,100}\)', '', normalize_parentheses(line))
                #: 以上是个方法，但是并不完美！

                #: 获取机构特性
                office = filter(lambda x: x in line, OFFICE)
                law_firm = ''
                if office:
                    text = line.split(u'。')
                    text = text[0].split(u'，')
                    #： 存储机构特性
                    office = office[0]
                    for item in text:
                        if office in item:
                            #: 获取律所全名
                            law_firm = item
                            break
                    if law_firm:
                        if law_firm.find(office) > 3:
                            #: 此处开始分割机构名称, 主要是去除一些多余的字。
                            if office == u'事务所':
                                #: 事务所可能存在分所的情况
                                if re.search(u'事务所\W+分所', law_firm):
                                    law_firm = law_firm[
                                        0: law_firm.find(u'分所')] + u'分所'
                                else:
                                    law_firm = law_firm[
                                        0: law_firm.find(u'事务所')] + u'事务所'
                            else:
                                law_firm = law_firm[
                                    0: law_firm.find(office)] + office
                        else:
                            law_firm = re.split(
                                ur'[， ,]', line.split(u'律师事务所', 1)[0][::-1], 1)[0][::-1] + u'律师事务所'

                        #: 去掉一些不必要的特殊字符吧
                        law_firm = law_firm.replace(u'：', '').replace(u':', '')
                        #: 本来下面的语句能够满足！但是避免律所文中可能存在这些字就改使用正则吧
                        #: law_firm = law_firm.replace(u'系', '').replace(u'是', '').replace('均为','')
                        law_firm = re.sub(u'^是|^系|^均为|^均系', '', law_firm)

                #: 最近总能发现找出了一些律师事务所，并没有什么数据的！我们需要去掉
                if law_firm == '' and (law_firm == u'律师事务所' or law_firm == u'援助中心'):
                    #law_firm = self.bamboo.insitution_group(line)
                    #law_firm = law_firm and law_firm[0] or ''
                    return []

                def _get_name(line):
                    "获取委托代理人"

                    text = line.split(u'。')
                    text = text[0].split(u'，')[0]
                    result = ''
                    if re.search(u'代理人(.+)', text):
                        result = re.findall(u'代理人(.+)', text)[0]
                    elif re.search(u'辩护人(.+)', text):
                        result = re.findall(u'辩护人(.+)', text)[0]
                    elif re.search(u'委托代表人(.+)', text):
                        result = re.findall(u'代表人(.+)', text)[0]
                    else:
                        return re.split(ur'[^\u4e00-\u9fa5、]',
                                        re.sub(ur'^指定辩护人|^委托代理人|^辩护人|^指定代理人|^代理人|^指定委托代理人|^委托代表人|^.+委托代理人([^\u4e00-\u9fa5]|有)*', '', line, 1))[0].split(u'、')[0]
                    if result != '':
                        result = result.replace(u'：', '').replace(u':', '')
                        return [result]

                    return []
                lawyers_name = _get_name(line)

                #：记录一下第一行
                try:
                    people = lawyers_name[0].split(u'、')
                except IndexError:
                    #: 如果是两个逗号！中间一个分割可能是律师

                    if len(text) > 2:
                        if re.search(u'代理人|代表人|辩护人', text[0]) and re.search(u'事务所|援助中心', text[2]):
                            lawyers_name = [text[1]]
                    if lawyers_name and isinstance(lawyers_name, list):
                        try:
                            people = lawyers_name[0].split(u'、')
                        except IndexError:
                            #: 还有可能是其他情况，就废弃掉吧
                            people = []
                    else:
                        #: 也有可能会没有律师出现只有事务所！这种我就不记录了。
                        people = []

                #：创建一个数组，来预备接下来可能出现的多个律师
                lawyers_double_name = []
                if len(people) > 1:
                    #: 如果存在多个律师就放到我们预定好的变量里面去吧
                    lawyers_double_name = people

                else:
                    if not lawyers_name or len(lawyers_name[0]) < 2 or len(lawyers_name[0]) > 4:
                        #： 如果文字大于四个！可能存在一些特殊字符.或者空格
                        lawyers_name = lawyers_name[0].strip().replace(
                            ':', '').replace(u'：', '')

                #: 最后存入我们的律师变量里面去吧！并且需要判断上一个分析出来的是原告还是被告噢！
                if lawyers_name:
                    if lawyers_double_name:
                        for item in lawyers_double_name:
                            if expect_whose_lawyers == 'defendant':
                                lawyers[u'被告'].append((item, law_firm))
                            elif expect_whose_lawyers == 'plaintiff':
                                lawyers[u'原告'].append((item, law_firm))
                    else:
                        if expect_whose_lawyers == 'defendant':
                            lawyers[u'被告'].append((lawyers_name[0], law_firm))
                        elif expect_whose_lawyers == 'plaintiff':
                            lawyers[u'原告'].append((lawyers_name[0], law_firm))

        return clients, lawyers

    def guess_case_sign(self, floot):
        """分析署名区
        args: 
             floot = <list or str> 
        returns:
             signs = <dict>

        """
        signs = {}
        if isinstance(floot, str):
            #： 先检查值
            floot = floot.split('\n')

        for item in CASE_SIGN:
            signs[item] = []

        for item in floot:
            Purs = Dou_text(item)
            for of in Purs:
                item = item.replace(of, '')

            for sign in CASE_SIGN:
                if re.search('%s' % sign, item):
                    # signs[sign].append(item.replace(sign, '')
                    #                   .replace(u'：', '')
                    #                   .replace(':', '').strip())
                    try:
                        name = re.search('^%s(.+)' % sign, item).groups()[0]
                        signs[sign].append(name.replace(u'：', '')
                                           .replace(':', '').strip())
                    except AttributeError:
                        #: 审判员和代理审判员的情况不能直接使用re.search('%s(.+)' % sign, item)
                        name = re.search('%s(.+)' % sign, item).groups()
                        if name:
                            signs[sign].append(name[0].replace(u'：', '')
                                               .replace(':', '').strip())

        for keys in signs.keys():
            if u'书记员' in keys or u'记录人' in keys or u'速录员' in keys:
                signs[u'书记员'].extend(signs[keys])

            if u'代审判员' in keys:
                signs[u'代理审判员'].extend(signs[keys])
        if not signs[u'书记员']:

            for item in floot:
                if re.match(u'^记录', item):
                    signs[u'书记员'].append(item.replace(u'记录', ''))
                    break

        return signs

    def guess_header_types(self, header):
        """分析头部信息
            args:
                header = <str or list>
            returns:
                signs  = <dict>
        """
        head_key = {'department': '', 'case_number': '',
                    'case_type': '', 'title': '', 'type': ''}
        title = {}
        if isinstance(header, str):
            header = header.split('\n')

        for item in header:
            if (u'法院' in item) or (re.match(u'.+(一|二|三|四|五)庭$', item)):
                head_key['department'] = item

            elif re.search(u'第.+号$', item):
                head_key['case_number'] = item

            else:
                head_key['case_type'] = "".join(
                    filter(lambda x: x in item, case_mode))
                if head_key['case_type']:
                    title[len(item)] = item

        if title:
            head_key['title'] = title[max(title.keys())]
            if not head_key['case_type']:
                head_key['case_type'] = "".join(
                    filter(lambda x: x in head_key['title'], case_mode))
        if head_key['case_type']:
            head_key['type'] = head_key['case_type'][:-3]

        return head_key

    def guess_end_date(self, case_sign=''):
        "分析guess"

        def _check_line(line):
            "检查行"
            line = normalize_numeric(line).replace(u'元月', u'一月')
            date = self.chinese_date.match(line)
            if date:
                year, month, day = date.groups()
                year = chinese_to_digit(year)
                if len(str(year)) > 4:
                    year = int(str(year)[len(str(year)[:-4]):])

                month = chinese_to_digit(month)
                day = chinese_to_digit(day)

                if year > 10000:
                    year = year % 100 + year / 100 * 10

                if year < 1990:
                    raise DateException('Error year.')
                month = month if (month != 0 and month < 12) else 1
                day = day if (day != 0 and day < 30) else 1

                try:
                    return datetime.datetime(year, month, day)
                except ValueError:
                    pass
            else:
                raise DateException('Not found.')

        # 如果有署名的，先用署名来分析
        if case_sign:
            for line in case_sign.split('\n'):
                try:
                    return _check_line(line)
                except DateException:
                    pass

        # 署名分析不出，我们唯有一行行来分析了
        for line in self.text_in_lines[::-1]:
            if 5 <= len(line) <= 15:
                try:
                    return _check_line(line)
                except DateException:
                    pass

    def _Identity_analysis(self):
        """对身份证进行分析

        """
        return re.findall(u"身份证.{0,7}?(\d+)", self.text, re.M)

    def _People_Information(self):
        """人物信息进行分析

        """
        pass

    def _replace_data(self, part):
        """敏感信息存储

        """
        if not isinstance(part, list):
            part = part.split('\n')
        replace_data = {}
        for line in part:
            Purs = Dou_text(line)
            #: 使用地区库来进行判断吧
            for areas in Purs:
                if not Checking_area(re.sub(u'\(|\)|（|）', '', areas).encode('utf8')):
                    #: 白名单就在这里判断吧
                    if re.sub(u'\(|\)|（|）', '', areas) in WHITE:
                        continue
                    for item in WHITE:
                        if item in areas and len(areas) > 5 and len(areas) < 20:
                            #: 如果括号里面是某某机构的话就作为敏感数据
                            replace_data[areas] = areas.replace(
                                areas[:areas.index(item)], '*****')
                    line = line.replace(areas, '')
            content = line.split(u'。')
            text = content[0].split(u'，')
            if u'律师' not in line and (not re.search(P_D_SUB, line)):
                for item in [u'代表人', u'代理人', u'辩护人', u'负责人']:
                    #: 一些代表人和代理人的去掉吧
                    if item in text[0]:
                        name = re.sub(u'.+{0}|{0}'.format(item), '', text[0])
                        if name.strip():
                            replace_data[name] = name[0] + '***'

                for item in MECHANISM:
                    #: 一些机构去掉吧
                    for insitu in text:
                        if item in insitu:
                            isus = insitu[:insitu.index(item)]
                            if len(isus) > 3 and len(isus) < 20:
                                replace_data[isus + item] = '****' + item

        return replace_data

    def guess_procedure(self, case_number):
        "判断审理"
        if not case_number:
            return u'其他'
        procedures = {u'一审': [u'初第', u'初字', u'初字第', u'初'],
                      u'二审': [u'重第', u'重字', u'重字第'],
                      u'再审': [u'再第', u'再字', u'再字第', u'再'],
                      u'终审': [u'终第', u'终字', u'终字第', u'终'],
                      u'申诉': [u'申第', u'申字', u'申字第'],
                      u'破产': [u'破第', u'破字', u'破字第', u'清（算）字', u'清（预）字'],
                      }
        for (key, values) in procedures.items():
            for value in values:
                if value in case_number:
                    return key

    def fuzzy_analyse(self, text):
        """调试时，可调用此方法调试

        """

        self.text = text

        _header, part, content, case_sign = self.split_to_four_parts()

        print _header, part, content, case_sign

        clients_attr, lawyers_attr = self.guess_clients_lawyers(
            part.split('\n'))

        for key, val in clients_attr.items():
            print key

            for item in val:
                print u' '.join(item)

        for key, val in lawyers_attr.items():
            print key

            for item in val:
                print u' '.join(item)

if __name__ == '__main__':
    import sys
    fuzzy = Analyse()
    fuzzy.fuzzy_analyse(file(sys.argv[1]).read().decode('utf8'))
