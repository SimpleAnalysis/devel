#!/usr/bin/env python
# -*- coding:utf-8 -*-

# Copyright (c) 2015 yu.liu <showmove@qq.com>
# All rights reserved

import re
from requests import get
from lxml import html


def main():
    header = {
        'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8',
        'Accept-Encoding': 'gzip, deflate, sdch',
        'User-Agent': 'Mozilla/5.0 (Macintosh; U; Intel Mac OS X 10_6_3; en-us; Silk/1.0.141.16-Gen4_11004310) AppleWebkit/533.16 (KHTML, like Gecko) Version/5.0 Safari/533.16 Silk-Accelerated=true'
    }
    people = []
    error_url = []
    for i in range(5, 3643):
        try:
            data = get(
                'http://www.lawbang.com/index.php/wap-index-home-siteid-{0}.shtml'.format(str(i)), headers=header)
        except:
            print 'ERROR, error = %s' % 'http://www.lawbang.com/index.php/wap-index-home-siteid-{0}.shtml'.format(str(i))

            error_url.append(
                'http://www.lawbang.com/index.php/wap-index-home-siteid-{0}.shtml'.format(str(i)))
            continue

        if data.ok:
            xhtml = html.document_fromstring(data.text)
            try:
                title = xhtml.xpath('//title')[0].text
                try:
                    phone = xhtml.xpath(
                        '//li[@class="fr"]//a[@class="a1"]//p')[0].text
                except IndexError:
                    if re.search('tel:(\d+)', data.text):
                        phone = re.search(
                            'tel:(\d+)|tel:(\d+-\d+)', data.text).groups()[0]
                    else:
                        phone = ''
                if re.search('\W|[a-zA-Z]', phone):
                    if re.search('tel:(\d+)', data.text):
                        phone = re.search(
                            'tel:(\d+)|tel:(\d+-\d+)', data.text).groups()[0]
                    else:
                        phone = ''

                print title, phone
            except TypeError:
                print 're error'
                continue
            except UnicodeEncodeError:
                print 'Unicode Error'
                continue
            people.append((title, phone))

    with open('new_phone.csv', 'w') as new_file:
        new_file.write(
            "\n".join(['%s, %s' % (i[0], i[1]) for i in people]).encode('utf8'))
    with open('error_url', 'w') as err:
        err.write("\n".join(error_url).encode('utf8'))


if __name__ == '__main__':
    main()
