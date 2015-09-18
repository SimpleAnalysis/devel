#!/usr/bin/python
# -*- coding:utf-8 -*-

# Copyright (c) 2015 yu.liu <showmove@qq.com>
# All rights reserved

import time
import json
from lxml import html
from requests import get
from urllib import quote
try:
    from selenium import webdriver
except ImportError:
    pass
from model.orm.Sqlextend import ot_baidu_search_info
from model.Loading import insert_database
from model.Loading import returns_session


def Querst_request():
    """通过GET网页获取网页的URL,并且更新库内的url值

    """
    session = returns_session('Sqlextend')()
    to = ot_baidu_search_info
    data = session.query(to).filter('id > 694').all()
    if not data:
        return
    for item in data:
        new = ot_baidu_search_info()
        new.id = item.id

        while True:
            try:
                r_url = get(item.url)
                break
            except:
                time.sleep(1)
                print 'retry sleep 1'

        if r_url.ok:
            new.url = r_url.request.url

            print 'Update old_url = %s, New_url = %s' % (item.url, new.url)
            session.merge(new)
            try:
                session.commit()
            except:
                continue
        else:
            print item.id
    session.close()


class BD_Search_Request(object):

    """使用webdriver来打开百度网页！获取网页的源码


    """

    def __init__(self, keys):
        """构造函数
        args:
           keys = <list>
        returns:
           None
        """
        self.url = ''

        self.keys = keys
        self.firefox = webdriver.Firefox()

    def set_pn(self, text, index):
        """设置连接地址
        args:
            text  = <str>
            index = <int>

        """
        self.url = """http://www.baidu.com/s?wd={0}&rsv_spt=1&pn={1}&f=8&rsv_bp=0&rsv_idx=2&ie=utf-8
        &tn=baiduhome_pg&rn=50&rsv_enter=1&rsv_sug3=12&rsv_sug1=6&rsv_sug2=0&inputT=1798&rsv_sug4=2332""".format(quote(text.encode('utf8')), index * 50)

    def reset_firefox(self):
        """重置firefox，当浏览器崩溃时可以调用
        调用前请使用self.firefox.quit()来关闭浏览器


        """
        self.firefox = webdriver.Firefox()

    def Querst_request(self):
        """搜索实例

        """

        point = insert_database('Sqlextend', tablename=ot_baidu_search_info)
        for key in self.keys:
            # self.firefox.get(self.url)
            for i in range(0, 20):
                self.set_pn(key, i)
                while True:
                    try:
                        self.firefox.get(self.url)
                        break
                    except:
                        # self.firefox.quit()
                        self.reset_firefox()
                        continue

                data = self.firefox.page_source

                if data:
                    xhtml = html.document_fromstring(data)
                    content = zip(xhtml.xpath('//div[@id="content_left"]//div[@class="f13"]//div[@class="c-tools"]'),
                                  xhtml.xpath('//div[@id="content_left"]//div[@class="f13"]//span[@class="g"]'))
                    for title, url in content:
                        db = ot_baidu_search_info()
                        try:
                            db.title = json.loads(
                                title.get('data-tools'))['title'].encode('utf8')
                        except:
                            try:
                                db.title = title.get(
                                    'data-tools').split(':')[1].split(',')[0].replace('"', '').encode('utf8')
                            except IndexError:
                                pass

                        db.url = url.text_content().encode('utf8')
                        db.key = key
                        insert_database(
                            'Sqlextend', tablename=ot_baidu_search_info, editor=db)
                        point.set_value(db)
                        point.insert()
                    """
                    for item in xhtml.xpath('//div[@id="content_left"]//div[@class="f13"]'):
                        #print item.get('href'), item.text_content().encode('utf8')
                        db = ot_baidu_search_info()
                        import pdb
                        pdb.set_trace()
                        db.title = item.xpath('//h3//a')[0].title
                        db.url = item.xpath('//span[@class="g"]')[0].text_content
                        
                        #db.url = item.get('href')
                        db.key = key
                        insert_database('Sqlextend', tablename = ot_baidu_search_info, editor = db)
                        point.set_value(db)
                        point.insert()
                    """
                time.sleep(2)

        self.firefox.close()


if __name__ == '__main__':

    keys = []
    plus = u"""上海律师网 上海律师事务所 上海律师咨询 
                 上海婚姻律师 上海离婚律师 上海离婚纠纷律师  
                上海劳动纠纷律师 上海劳动仲裁律师   
                上海刑事辩护律师 上海刑事律师   
                上海公司律师 上海公司纠纷律师 上海股权纠纷律师  
                上海合同律师 上海合同纠纷律师   
                上海房产律师 上海房产纠纷律师 上海房地产律师  
                上海交通事故律师    
                上海债权债务律师 上海债务律师 上海债务纠纷律师  上海债权律师 
                上海损害赔偿律师    
                上海知识产权律师 上海商标律师 上海专利律师  
                上海医疗纠纷律师 上海医疗损害律师 上海医疗事故律师 
                """.split()
    keys.extend(plus)
    for item in plus:
        keys.append(item.replace(u'上海', u'北京'))
    session = returns_session('Sqlextend')()
    to = ot_baidu_search_info
    diff = session.query(to.key).group_by(to.key).all()

    #keys = keys - dif
    if not diff:
        pass
    else:
        for item in diff:
            keys.remove(item[0])
        #keys = [u'北京律师', u'上海律师']
        # Querst_request()
        Search = BD_Search_Request(keys)
        # Search.Format_url_to_domain()

        Search.Querst_request()
