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
   
   2015-09-06
   更新：
   1.去除BAMBOO分析原被告
   2.修改书记员识别方式
   
"""

# $Id$
__author__ = [
    'liuyu <showmove@qq.com>',
]
__version__ = '$Revision: 1.1 $'

import re
import codecs
from extend.Processer.utils import *
from extend.WYCrawler.utils import XPath
from analyse import Analyse
import datetime
from configure import Area_duct, Checking_area, \
    MECHANISM, PLAIN, DEFEN, SPLIT_KEY, P_D_SUB, WHITE, OFFICE, CASE_SIGN

from extend.exists import Dou_text


class DateException(Exception):

    "异常类"
    pass


class JudgmentProcesser(Analyse):

    "分析类"
    chinese_date = re.compile(ur'(.+)年(.+)月(.+)日')
    kk = codecs.open('test.log', 'w', encoding='utf8')
    street_name_stop_word = (
        u'国', u'省', u'市', u'县', u'州', u'郡', u'区', u'乡', u'镇', u'村',
        u'庄', u'洋',
        u'城', u'馆', u'寺', u'宫', u'府', u'山', u'政府', u'江', u'法院', u'道路')
    exinclude_street_name = (
        u'阿坝藏族羌族自治州', u'阿克苏地', u'阿克苏地区', u'阿拉尔', u'阿拉尔市', u'阿拉善盟',
        u'阿勒泰地',
        u'阿勒泰地区', u'阿里地', u'阿里地区', u'安徽', u'安徽省', u'安康', u'安康市', u'安庆',
        u'安庆市', u'安顺', u'安顺市', u'安阳', u'安阳市', u'鞍山', u'鞍山市', u'澳门',
        u'巴南', u'巴南区', u'巴彦淖尔', u'巴彦淖尔市', u'巴音郭楞蒙古自治州', u'巴中', u'巴中市',
        u'白城', u'白城市', u'白沙黎族自治县', u'白山', u'白山市', u'白银', u'白银市', u'百色',
        u'百色市', u'蚌埠', u'蚌埠市', u'包头', u'包头市', u'保定', u'保定市', u'保山',
        u'保山市', u'保亭黎族苗族自治县', u'宝坻', u'宝坻区', u'宝鸡', u'宝鸡市', u'宝山',
        u'宝山区', u'北碚', u'北碚区', u'北辰', u'北辰区', u'北海', u'北海市', u'北京市',
        u'北京',
        u'北区', u'本溪', u'本溪市', u'毕节地', u'毕节地区', u'璧山县', u'滨州', u'滨州市',
        u'亳州', u'亳州市', u'博尔塔拉蒙古自治州', u'沧州', u'沧州市', u'昌都地', u'昌都地区',
        u'昌吉回族自治州', u'昌江黎族自治县', u'昌平', u'昌平区', u'常德', u'常德市', u'常州',
        u'常州市', u'长春', u'长春市', u'长宁', u'长宁区', u'长沙', u'长沙市', u'长寿',
        u'长寿区', u'长治', u'长治市', u'巢湖', u'巢湖市', u'潮州', u'潮州市', u'郴州',
        u'郴州市', u'城口县', u'成都', u'成都市', u'承德', u'承德市', u'澄迈县', u'池州',
        u'池州市', u'赤峰', u'赤峰市', u'崇明县', u'崇文', u'崇文区', u'崇左', u'崇左市',
        u'滁州', u'滁州市', u'楚雄彝族自治州', u'达州', u'达州市', u'大埔区', u'大埔元朗',
        u'大渡口', u'大渡口区', u'大港', u'大港区', u'大理白族自治州', u'大连', u'大连市',
        u'大庆', u'大庆市', u'大同', u'大同市', u'大兴', u'大兴安岭地', u'大兴安岭地区',
        u'大兴区', u'大足县', u'丹东', u'丹东市', u'儋州', u'儋州市', u'德宏傣族景颇族自治州',
        u'德阳', u'德阳市', u'德州', u'德州市', u'迪庆藏族自治州', u'垫江县', u'定安县', u'定西',
        u'定西市', u'东城', u'东城区', u'东方', u'东方市', u'东莞', u'东莞市', u'东丽',
        u'东丽区', u'东区', u'东营', u'东营市', u'鄂尔多斯', u'鄂尔多斯市', u'鄂州', u'鄂州市',
        u'恩施土家族苗族自治州', u'房山', u'房山区', u'防城港', u'防城港市', u'丰都县', u'丰台',
        u'丰台区', u'奉节县', u'奉贤', u'奉贤区', u'佛山', u'佛山市', u'涪陵', u'涪陵区',
        u'福建', u'福建省', u'福州', u'福州市', u'抚顺', u'抚顺市', u'抚州', u'抚州市',
        u'莆田', u'莆田市', u'阜新', u'阜新市', u'阜阳', u'阜阳市', u'甘南藏族自治州', u'甘肃',
        u'甘肃省', u'甘孜藏族自治州', u'赣州', u'赣州市', u'高雄', u'高雄市', u'菏泽', u'菏泽市',
        u'固原', u'固原市', u'观塘', u'观塘区', u'广安', u'广安市', u'广东', u'广东省',
        u'广西', u'广西省', u'广元', u'广元市', u'广州', u'广州市', u'桂林', u'桂林市',
        u'贵港', u'贵港市', u'贵阳', u'贵阳市', u'贵州', u'贵州省', u'果洛藏族自治州', u'哈尔滨',
        u'哈尔滨市', u'哈密地', u'哈密地区', u'海北藏族自治州', u'海淀', u'海淀区', u'海东地',
        u'海东地区', u'海口', u'海口市', u'海南', u'海南藏族自治州', u'海南省',
        u'海西蒙古族藏族自治州', u'邯郸', u'邯郸市', u'汉沽', u'汉沽区', u'汉中', u'汉中市',
        u'杭州', u'杭州市', u'合川', u'合川区', u'合肥', u'合肥市', u'和平', u'和平区',
        u'和田地', u'和田地区', u'河北', u'河北区', u'河北省', u'河池', u'河池市', u'河东',
        u'河东区', u'河南', u'河南省', u'河西', u'河西区', u'河源', u'河源市', u'贺州',
        u'贺州市', u'鹤壁', u'鹤壁市', u'鹤岗', u'鹤岗市', u'黑河', u'黑河市', u'黑龙江',
        u'黑龙江省', u'衡水', u'衡水市', u'衡阳', u'衡阳市', u'红河哈尼族彝族自治州', u'红桥',
        u'红桥区', u'虹口', u'虹口区', u'呼和浩特', u'呼和浩特市', u'呼伦贝尔', u'呼伦贝尔市',
        u'湖北', u'湖北省', u'湖南', u'湖南省', u'湖州', u'湖州市', u'葫芦岛', u'葫芦岛市',
        u'怀化', u'怀化市', u'怀柔', u'怀柔区', u'淮安', u'淮安市', u'淮北', u'淮北市',
        u'淮南', u'淮南市', u'黄大仙', u'黄大仙区', u'黄冈', u'黄冈市', u'黄南藏族自治州',
        u'黄浦', u'黄浦区', u'黄山', u'黄山市', u'黄石', u'黄石市', u'惠州', u'惠州市',
        u'基隆', u'基隆市', u'鸡西', u'鸡西市', u'吉安', u'吉安市', u'吉林', u'吉林省',
        u'吉林市', u'济南', u'济南市', u'济宁', u'济宁市', u'济源', u'济源市', u'蓟县',
        u'佳木斯', u'佳木斯市', u'嘉定', u'嘉定区', u'嘉兴', u'嘉兴市', u'嘉义', u'嘉义市',
        u'嘉峪关', u'嘉峪关市', u'江北', u'江北区', u'江津', u'江津区', u'江门', u'江门市',
        u'江苏', u'江苏省', u'江西', u'江西省', u'焦作', u'焦作市', u'揭阳', u'揭阳市',
        u'津南', u'津南区', u'金昌', u'金昌市', u'金华', u'金华市', u'金山', u'金山区',
        u'锦州', u'锦州市', u'晋城', u'晋城市', u'晋中', u'晋中市', u'荆门', u'荆门市',
        u'荆州', u'荆州市', u'景德镇', u'景德镇市', u'静安', u'静安区', u'静海县', u'九江',
        u'九江市', u'九龙城', u'九龙城区', u'九龙坡', u'九龙坡区', u'酒泉', u'酒泉市', u'喀什地',
        u'喀什地区', u'开封', u'开封市', u'开县', u'克拉玛依', u'克拉玛依市',
        u'克孜勒苏柯尔克孜自治州', u'葵青', u'葵青区', u'昆明', u'昆明市', u'拉萨', u'拉萨市',
        u'来宾', u'来宾市', u'莱芜', u'莱芜市', u'兰州', u'兰州市', u'廊坊', u'廊坊市',
        u'乐东黎族自治县', u'乐山', u'乐山市', u'漯河', u'漯河市', u'离岛', u'离岛区', u'丽江',
        u'丽江市', u'丽水', u'丽水市', u'连云港', u'连云港市', u'凉山彝族自治州', u'梁平县',
        u'聊城', u'聊城市', u'辽宁', u'辽宁省', u'辽阳', u'辽阳市', u'辽源', u'辽源市',
        u'临沧', u'临沧市', u'临汾', u'临汾市', u'临高县', u'临夏回族自治州', u'临沂', u'临沂市',
        u'林芝地', u'林芝地区', u'陵水黎族自治县', u'柳州', u'柳州市', u'六安', u'六安市',
        u'六盘水', u'六盘水市', u'龙岩', u'龙岩市', u'陇南', u'陇南市', u'娄底', u'娄底市',
        u'卢湾', u'卢湾区', u'泸州', u'泸州市', u'洛阳', u'洛阳市', u'吕梁', u'吕梁市',
        u'马鞍山', u'马鞍山市', u'茂名', u'茂名市', u'梅州', u'梅州市', u'眉山', u'眉山市',
        u'门头沟', u'门头沟区', u'密云县', u'绵阳', u'绵阳市', u'闵行', u'闵行区', u'牡丹江',
        u'牡丹江市', u'那曲地', u'那曲地区', u'南岸', u'南岸区', u'南昌', u'南昌市', u'南充',
        u'南充市', u'南川', u'南川区', u'南汇', u'南汇区', u'南京', u'南京市', u'南开',
        u'南开区', u'南宁', u'南宁市', u'南平', u'南平市', u'南区', u'南通', u'南通市',
        u'南阳', u'南阳市', u'内江', u'内江市', u'内蒙古自治', u'内蒙古自治区', u'宁波',
        u'宁波市', u'宁德', u'宁德市', u'宁河县', u'宁夏回族自治', u'宁夏回族自治区',
        u'怒江傈僳族自治州', u'攀枝花', u'攀枝花市', u'盘锦', u'盘锦市', u'彭水苗族土家族自治县',
        u'平顶山', u'平顶山市', u'平谷', u'平谷区', u'平凉', u'平凉市', u'萍乡', u'萍乡市',
        u'濮阳', u'濮阳市', u'普陀', u'普陀区', u'浦东新', u'浦东新区', u'七台河', u'七台河市',
        u'綦江县', u'齐齐哈尔', u'齐齐哈尔市', u'潜江', u'潜江市', u'黔东南苗族侗族自治州', u'黔江',
        u'黔江区', u'黔南布依族苗族自治州', u'黔西南布依族苗族自治州', u'钦州', u'钦州市', u'秦皇岛',
        u'秦皇岛市', u'清远', u'清远市', u'青岛', u'青岛市', u'青海', u'青海省', u'青浦',
        u'青浦区', u'庆阳', u'庆阳市', u'琼海', u'琼海市', u'琼中黎族苗族自治县', u'衢州',
        u'衢州市', u'曲靖', u'曲靖市', u'泉州', u'泉州市', u'荃湾', u'荃湾区', u'日喀则地',
        u'日喀则地区', u'日照', u'日照市', u'荣昌县', u'三门峡', u'三门峡市', u'三明', u'三明市',
        u'三亚', u'三亚市', u'沙坪坝', u'沙坪坝区', u'沙田', u'沙田区', u'厦门', u'厦门市',
        u'山东', u'山东省', u'山南地', u'山南地区', u'山西', u'山西省', u'陕西', u'陕西省',
        u'汕头', u'汕头市', u'汕尾', u'汕尾市', u'商洛', u'商洛市', u'商丘', u'商丘市',
        u'上海', u'上海市', u'上饶', u'上饶市', u'韶关', u'韶关市', u'绍兴', u'绍兴市',
        u'邵阳', u'邵阳市', u'深水埗', u'深水埗区', u'深圳', u'深圳市', u'神农架林',
        u'神农架林区', u'沈阳', u'沈阳市', u'十堰', u'十堰市', u'石河子', u'石河子市', u'石家庄',
        u'石家庄市', u'石景山', u'石景山区', u'石柱土家族自治县', u'石嘴山', u'石嘴山市', u'双桥',
        u'双桥区', u'双鸭山', u'双鸭山市', u'顺义', u'顺义区', u'朔州', u'朔州市', u'思茅',
        u'思茅市', u'四川', u'四川省', u'四平', u'四平市', u'松江', u'松江区', u'松原',
        u'松原市', u'苏州', u'苏州市', u'宿迁', u'宿迁市', u'宿州', u'宿州市', u'绥化',
        u'绥化市', u'遂宁', u'遂宁市', u'随州', u'随州市', u'塔城地', u'塔城地区', u'台北',
        u'台北市', u'台南', u'台南市', u'台湾', u'台湾北京', u'台湾省', u'台中', u'台中市',
        u'台州', u'台州市', u'太原', u'太原市', u'泰安', u'泰安市', u'泰州', u'泰州市',
        u'唐山', u'唐山市', u'塘沽', u'塘沽区', u'天津', u'天津市', u'天门', u'天门市',
        u'天水', u'天水市', u'铁岭', u'铁岭市', u'通化', u'通化市', u'通辽', u'通辽市',
        u'通州', u'通州区', u'潼南县', u'铜川', u'铜川市', u'铜梁县', u'铜陵', u'铜陵市',
        u'铜仁地', u'铜仁地区', u'图木舒克', u'图木舒克市', u'吐鲁番地', u'吐鲁番地区', u'屯昌县',
        u'屯门', u'屯门区', u'湾仔', u'湾仔区', u'万盛', u'万盛区', u'万宁', u'万宁市',
        u'万州', u'万州区', u'威海', u'威海市', u'潍坊', u'潍坊市', u'渭南', u'渭南市',
        u'温州', u'温州市', u'文昌', u'文昌市', u'文山壮族苗族自治州', u'乌海', u'乌海市',
        u'乌兰察布', u'乌兰察布市', u'乌鲁木齐', u'乌鲁木齐市', u'巫山县', u'巫溪县', u'吴忠',
        u'吴忠市', u'无锡', u'无锡市', u'梧州', u'梧州市', u'芜湖', u'芜湖市', u'五家渠',
        u'五家渠市', u'五指山', u'五指山市', u'武汉', u'武汉市', u'武隆县', u'武清', u'武清区',
        u'武威', u'武威市', u'西安', u'西安市', u'西藏', u'西藏自治', u'西藏自治区', u'西城',
        u'西城区',
        u'西贡', u'西贡区', u'西宁', u'西宁市', u'西青', u'西青区', u'西双版纳傣族自治州',
        u'锡林郭勒盟', u'仙桃', u'仙桃市', u'咸宁', u'咸宁市', u'咸阳', u'咸阳市', u'湘潭',
        u'湘潭市', u'湘西土家族苗族自治州', u'襄樊', u'襄樊市', u'香港', u'孝感', u'孝感市',
        u'忻州', u'忻州市', u'新疆自治', u'新疆自治区', u'新乡', u'新乡市', u'新余', u'新余市',
        u'新竹', u'新竹市', u'信阳', u'信阳市', u'兴安盟', u'邢台', u'邢台市',
        u'秀山土家族苗族自治县', u'徐汇', u'徐汇区', u'徐州', u'徐州市', u'许昌', u'许昌市',
        u'宣城', u'宣城市', u'宣武', u'宣武区', u'雅安', u'雅安市', u'烟台', u'烟台市',
        u'延安', u'延安市', u'延边朝鲜族自治州', u'延庆县', u'盐城', u'盐城市', u'扬州',
        u'扬州市', u'杨浦', u'杨浦区', u'阳江', u'阳江市', u'阳泉', u'阳泉市', u'伊春',
        u'伊春市', u'伊犁哈萨克自治州', u'宜宾', u'宜宾市', u'宜昌', u'宜昌市', u'宜春',
        u'宜春市', u'益阳', u'益阳市', u'银川', u'银川市', u'鹰潭', u'鹰潭市', u'营口',
        u'营口市', u'永川', u'永川区', u'永州', u'永州市', u'油尖旺', u'油尖旺区',
        u'酉阳土家族苗族自治县', u'榆林', u'榆林市', u'渝北', u'渝北区', u'渝中', u'渝中区',
        u'玉林', u'玉林市', u'玉树藏族自治州', u'玉溪', u'玉溪市', u'元朗区', u'岳阳', u'岳阳市',
        u'云浮', u'云浮市', u'云南', u'云南省', u'云阳县', u'运城', u'运城市', u'枣庄',
        u'枣庄市', u'闸北', u'闸北区', u'湛江', u'湛江市', u'张家界', u'张家界市', u'张家口',
        u'张家口市', u'张掖', u'张掖市', u'漳州', u'漳州市', u'昭通', u'昭通市', u'朝阳',
        u'朝阳区', u'朝阳市', u'肇庆', u'肇庆市', u'浙江', u'浙江省', u'镇江', u'镇江市',
        u'郑州', u'郑州市', u'中山', u'中山市', u'中卫', u'中卫市', u'中西', u'中西区',
        u'忠县', u'重庆', u'重庆市', u'周口', u'周口市', u'舟山', u'舟山市', u'株洲',
        u'株洲市', u'珠海', u'珠海市', u'驻马店', u'驻马店市', u'淄博', u'淄博市', u'资阳',
        u'资阳市', u'自贡', u'自贡市', u'遵义', u'遵义市')
    _text = None
    text_in_lines = None
    bamboo = None

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
            #: line = re.sub(u'\(.+\)$|。$|\w+$|\d+.\d+$', '', normalize_parentheses(line))
            #: 去掉结尾字符并不能完全保证标题的正确性，就使用正则表示多种可能性
            if (line.endswith(u'书') or
                re.search('书\(.+\)$',  normalize_parentheses(line)) or
                re.search('\d+$',  normalize_parentheses(line)) or
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
            if len(line) < 15 and (re.match(u'^(%s)' % "|".join(CASE_SIGN), line)
                                   or re.match(u'.+年.+月.+日', line)):
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
                Splitn = filter(lambda x: x in line, SPLIT_KEY)
                if Splitn:
                    _second_part_end_index = index
                    second_part = thirt_part[:index]
                    thirt_part = thirt_part[index:]
                    break

        result = ['\n'.join(part) for part in (
            first_part, second_part, thirt_part, four_part)]

        # 处理署名
        result[3] = normalize_numeric(
            result[3].replace(u'员', u'员 ').replace(u'审判长', u'审判长 '))

        return result

    def guess_clients_lawyers(self, part):
        """根据内容分析出原告被告和其代理律师的信息

        :param content:
        :return: :rtype:
        """

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

        for line in part.split('\n'):
            #: 开始分析每一行了。

            Purs = Dou_text(line)
            #: 使用地区库来进行判断吧
            for areas in Purs:
                if not Checking_area(re.sub(u'\(|\)|（|）', '', areas).encode('utf8')):
                    #:创建白名单
                    if re.sub(u'\(|\)|（|）', '', areas) in WHITE:
                        continue
                    #:其他的数据都删除
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

                law_firm = ''
                if (u'律师事务所' in line) or (u'事务所律师' in line) or (u'援助中心' in line):

                    text = line.split(u'。')
                    text = text[0].split(u'，')
                    for item in text:
                        #: if item in u'事务所':
                        if (u'事务所' in item) or (u'援助中心' in item):
                            law_firm = item
                            break

                    if (law_firm.find(u'事务所') > 3 or law_firm.find(u'援助中心') > 3):

                        if u'援助中心' in law_firm:

                            law_firm = law_firm[
                                0: law_firm.find(u'援助中心')] + u'援助中心'
                            law_firm = law_firm.replace(
                                u'：', '').replace(u':', '')

                        elif u'事务所' in law_firm:

                            if re.search(u'事务所\W+分所', law_firm):
                                law_firm = law_firm[
                                    0: law_firm.find(u'分所')] + u'分所'
                            else:
                                law_firm = law_firm[
                                    0: law_firm.find(u'事务所')] + u'事务所'
                                law_firm = law_firm.replace(
                                    u'：', '').replace(u':', '')

                    else:
                        law_firm = re.split(
                            ur'[， ,]', line.split(u'律师事务所', 1)[0][::-1], 1)[0][::-1] + u'律师事务所'

                    #: 这里可以更简单的使用Rplace方法去修改
                    #: 例： law_firm.replace(u'系', '').replace(u'是', '')
                    #：当然！现在我还不想改他
                    if u'系' in law_firm or law_firm.startswith(u'是') or law_firm.startswith(u'均为'):
                        if u'系' in law_firm:
                            law_firm = law_firm.split(u'系', 1)[1]
                        elif law_firm.startswith(u'是'):
                            law_firm = law_firm.replace(u'是', '')
                        elif law_firm.startswith(u'均为'):
                            law_firm = law_firm.replace(u'均为', '')

                #: 最近总能发现找出了一些律师事务所，并没有什么数据的！我们需要去掉
                if law_firm == '' and (law_firm == u'律师事务所' or law_firm == u'援助中心'):
                    return []
                    #law_firm = self.bamboo.insitution_group(line)
                    #law_firm = law_firm and law_firm[0] or ''

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
                        result = re.findall(u'委托代表人(.+)', text)[0]
                    else:
                        return re.split(ur'[^\u4e00-\u9fa5、]',
                                        re.sub(ur'^指定辩护人|^委托代理人|^辩护人|^指定代理人|^代理人|^指定委托代理人|^委托代表人|^.+委托代理人([^\u4e00-\u9fa5]|有)*', '', line, 1))[0].split(u'、')[0]
                    if result != '':
                        result = result.replace(u'：', '').replace(u':', '')
                        return [result]
                    #: 避免返回None值
                    return []
                lawyers_name = _get_name(line)

                #: print law_firm,lawyers_name
                #：记录一下第一行
                try:
                    people = lawyers_name[0].split(u'、')
                except IndexError:
                    #: 如果是两个逗号！中间一个分割可能是律师
                    if len(text) > 2:
                        if re.search(u'代理人|代表人|辩护人', text[0]) and re.search(u'事务所|援助中心', text[2]):
                            lawyers_name = [text[1]]
                    if lawyers_name:
                        people = lawyers_name[0].split(u'、')
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
                        #: 大于4的就不是正常名字了，还需要bamboo来处理下
                        #lawyers_name = self.bamboo.people_name(line.replace(' ', ''))
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

    def guess_end_date(self, case_sign=''):
        "分析guess"

        def _check_line(line):
            "检查行"
            line = normalize_numeric(line).replace(u'元月', u'一月')
            date = self.chinese_date.match(line)
            if date:
                year, month, day = date.groups()
                year = chinese_to_digit(year)
                month = chinese_to_digit(month)
                day = chinese_to_digit(day)

                if year > 10000:
                    year = year % 100 + year / 100 * 10

                if year < 1990:
                    raise DateException('Error year.')
                return datetime.datetime(year, month, day)
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

    def guess_chief_judge(self):
        "获取审判长"
        for line in self.text_in_lines[::-1]:
            line = just_chinese(line)
            _line = line.replace(' ', '')
            if len(_line) > 15 or len(_line) < 3:
                continue
            if _line.startswith(u'审判长'):
                return _line.replace(u'审判长', ''). \
                    replace(u':', '').replace(u'：', '')

    def guess_judge(self):
        "获取审判员"
        judges = []
        for line in self.text_in_lines[::-1]:
            line = just_chinese(line)
            _line = line.replace(' ', '')
            if len(_line) > 15 or len(_line) < 3:
                continue
            if _line.startswith(u'审判员'):
                judges.append(
                    _line.replace(u'审判员', '').replace(u':', '').replace(u'：', ''))
            # if _line.startswith(u'人民陪审员'):
            #    judges.append(_line.replace(u'人民陪审员', '').replace(u':', '').replace(u'：', ''))
        if judges:
            return ','.join(judges)

    def guess_id_number(self):
        "获取身份证"
        return re.findall(u"身份证.{0,7}?(\d+)", self.text, re.M)

    def guess_acting_judges(self):
        "获取代理审判员"
        acting_judge = []
        for line in self.text_in_lines[::-1]:
            line = just_chinese(line)
            _line = line.replace(' ', '')
            if len(_line) > 15 or len(_line) < 3:
                continue
            if _line.startswith(u'代理审判员'):
                acting_judge.append(_line.replace(u'代理审判员', '').
                                    replace(u':', '').replace(u'：', '')
                                    )

        if acting_judge:
            return ','.join(acting_judge)

    def guess_clerk(self):
        "获取书记员"
        for line in self.text_in_lines[::-1]:
            line = just_chinese(line)
            _line = line.replace(' ', '')
            if len(_line) > 15 or len(_line) < 3:
                continue

            text = re.findall(u'^书记员|^代书记员|^代理书记员|^见习书记员', _line)
            if text:
                return _line.replace(text[0], '').\
                    replace(u':', '').replace(u'：', '')

            # if _line.startswith(u'书记员'):
            #    return _line.replace(u'书记员', ''). \
            #        replace(u':', '').replace(u'：', '')

    def guess_sentence(self):
        "获取数据"
        s = re.search(u'达成.*?协议.*?[：|:]\n', self.text, re.M)
        s1 = re.search(u'[判决|裁定]如下[：|:|；|。]\n', self.text, re.M)
        s2 = re.search(u'特发出此.*?令[：|:|；|。]\n', self.text, re.M)
        if s:
            text = self.text.split(s.group())[1]
        elif s1:
            text = self.text.split(s1.group())[1]
        elif s2:
            text = self.text.split(s2.group())[1]
        else:
            return

        if u'\n审判长' in text:
            return text.split(u'\n审判长')[0]
        elif u'\n审判员' in text:
            return text.split(u'\n审判员')[0]
        else:
            return text

    def guess_department(self):
        """从原文猜测审理机构。
        :return:
        """
        first_line = self.text[:self.text.find('\n')]
        if u'法院' in first_line:
            return first_line.strip()

    def guess_street_name(self):
        "分析信息"
        street_name = []
        for line in self.text_in_lines[::-1]:
            street_name.extend(self.bamboo.street_name(line))

            # street_name = self.bamboo.street_name(self.text)

        def _stop_word(name):
            "停止分析"
            for word in self.street_name_stop_word:
                if name.endswith(word):
                    return False
            return True

        street_name = filter(_stop_word, street_name)
        street_name = filter(lambda name:
                             name not in self.exinclude_street_name,
                             street_name)
        return street_name

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

        return u'其他'
    insitution_stop_word = (u'公司',)

    def guess_insitution_name(self):
        "分析数据"
        insitution_names = self.bamboo.insitution_group(self.text)

        def _filter_insitution(name):
            "filterinsitution .."
            for word in self.insitution_stop_word:
                if name.endswith(word):
                    return True
            return False

        return filter(_filter_insitution, insitution_names)

    def guess_area(self, text):
        "分析区域"

        # 分析地区
        area = self.area_parse.ident(text.encode('gbk'))
        #
        # area['name'] = area['name'].decode('gbk')
        # area['prov'] = area['prov'].decode('gbk')
        if area:
            return area['areano']

    def guess_lawyers_as_string(self):
        "返回字符串"
        lawyers = self.guess_lawyers()
        return ';'.join([','.join(lawyer) + ':' + firm for (lawyer, firm) in lawyers])

    def guess_money(self):
        """猜测判决书里面涉及的金额，取最大的一个金额。


        :return:
        """

        money = [float(item.replace(',', '')) for item in
                 re.findall(u"([\d|,]+)元", self.text)]
        if money:
            return max(money)

        "判断原告与被告信息"
        queue = []
        clients = {u'被告': [], u'原告': []}

        def _check_client_in_line(line):
            """判断这一行是否有当事人，有则分析其属性，并返回。"""

            names = self.bamboo.people_name(line)
            institutions = self.bamboo.insitution_group(line)

            # 如果这一行有多于一个名字出现，有可能是别名，又名
            # if len(names) > 1:
            # for name in names: print name,
            # print '####', line

            # 如果有机构名和人名同时存在，而且人名包含在机构名里，则判断为机构，因为很多公司名跟人名相似
            # 如果只有机构名，那当然判断为机构
            if (institutions and names and names[0] in institutions[0]) \
                    or \
                    (institutions and not names):

                return (institutions[0], u'机构', '')

            # 如果有名字出现，则判断为个人
            elif names:
                # 尝试分析性别
                result = re.search(u'[,|，]([男|女])[,|，|。]', line)
                sex = result and result.groups()[0] or ''

                return (names[0], u'个人', sex)

            # 同时没有机构名和人名，有可能是bamboo分析不出，我们返回未知
            else:
                return ('', u'未知', '')
            #: 避免返回一个None值
            return ('', u'未知', '')
        clients_names = set()
        for line in self.text_in_lines:
            queue.append(len(line))

            if len(queue) > 4:
                queue = queue[1:]

            if len(queue) > 2 and numpy.var(queue) > 1000:
                break

            # print numpy.var(queue), line

            if u'委托代理人' not in line:

                # TODO:本来是一句话里面出现多个名字就判断为正文，但忽略了有可能是几个原告之间的关系。
                # if True in map(
                # lambda name: name in line, clients_names):
                # break
                # 直接判断句子头几个字
                if line.startswith(u'被上诉人') or line.startswith(u'被告'):

                    client = _check_client_in_line(line)
                    clients_names.add(client[0])
                    clients[u'被告'].extend([client])

                elif line.startswith(u'上诉人') or line.startswith(
                        u'原告') or line.startswith(u'公诉机关'):
                    client = _check_client_in_line(line)
                    clients_names.add(client[0])
                    clients[u'原告'].extend([client])

        return clients

    def fuzzy_analyse(self, new, raw_html):
        "分析方法，开始对数据进行分析"

        # 先把html转为一行为一段的纯文本1
        # self.text = html_to_text(HTML_PARSER.unescape(raw_html))
        # new.content_all = self.text#re.sub(u'法院:|日期:|案号:','',self.text)

        new.content_all = raw_html

        self.text = raw_html

        _without_header = new.department and new.case_type and new.case_number and True

        _header, part, new.content, new.case_sign = self.split_to_four_parts()

        new.clients_attr, new.lawyers_attr = self.guess_clients_lawyers(part)

        if not _without_header:

            if _header:
                _header = _header.split('\n')

            for line in _header:
                # 专门对付 XXX法院民三庭这种
                if len(line.split(':')) > 1:
                    line = line.split(':')[1].strip()
                if not new.department and (line.endswith(u'法院') or re.match(u'.+(一|二|三|四|五)庭$', line)):
                    new.department = line.split(u'法庭')[0]

                if (not new.case_type) and line.endswith(u'书'):
                    new.case_type = line

                if (not new.case_number) and line.endswith(unicode('号', 'utf8')):
                    new.case_number = line

                if new.department and new.case_type and new.case_number:
                    break
        if new.case_type == '' or new.case_type is None:
            return

        new.end_date = new.end_date or self.guess_end_date(new.case_sign)

        new.procedure = new.procedure or self.guess_procedure(new.case_number)

        new.chief_judge = new.chief_judge or self.guess_chief_judge()
        new.acting_judges = new.acting_judges or self.guess_acting_judges()
        new.judge = new.judge or self.guess_judge()
        new.clerk = new.clerk or self.guess_clerk()

        # self.guess_clients_lawyers(part)

        lawyers_name = filter(None, [x[0] for x in new.lawyers_attr[
                              u'原告']] + [x[0] for x in new.lawyers_attr[u'被告']])
        lawyer_firms = filter(None, [x[1] for x in new.lawyers_attr[
                              u'原告']] + [x[1] for x in new.lawyers_attr[u'被告']])
        #: if new.lawyers_attr == '' or new.lawyers_attr
        #: print lawyers_name, lawyer_firms
        new.replace_data = self._replace_data(part)
        """暂时并不需要的功能， 敏感信息可作为单独更新使用.
        all_people_name = self.bamboo.people_name(new.content_all)
        
        possible_names = list(
            set(all_people_name) - set(lawyers_name) - set([new.chief_judge, new.acting_judges, new.judge, new.clerk]))

        new.replace_data = {}

        new.replace_data.update(dict((name, u"%s某" % name[0]) for name in possible_names))

        street_names = self.guess_street_name()

        new.possible_streets = ','.join(street_names)

        id_numbers = self.guess_id_number()

        new.replace_data.update(dict((number, u"%s****" % number[:-4]) for number in id_numbers))

        insitution_name = self.guess_insitution_name()
        insitution_name = list(set(insitution_name) - set(lawyer_firms))
        
        def _mask_insitution(name):
            "判断是否机构"
            end_words = (u'有限责任公司', u'股份有限公司', u'总公司', u'分公司',
                         u'开发有限公司', u'技术有限公司', u'服务有限公司', u'有限公司', u'公司')
            for word in end_words:
                if name.endswith(word):
                    # parts = self.bamboo.seg(name.replace(word, ''))
                    # parts[-1] = len(parts[-1]) * '*'
                    return name, '*' * (len(name) - len(word)) + word

        new.replace_data.update(dict(_mask_insitution(name) for name in insitution_name))
        """
        new.content = part + new.content
