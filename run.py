#!/usr/bin/env python
# -*- coding:utf-8 -*-

# Copyright (c) 2015 yu.liu <showmove@qq.com>
# All rights reserved

"""runing options using docopt.

Usage:
  run.py   query <dbname> | run view 
  run.py   syncdb | syncdb <dbname>
  run.py   analysis <ProcessFile>
  run.py   get <jobs> | get <jobs> <update>

Arguments:
  options dbname  
  syncdb

Options:
  -h --help            show this help message and exit
  --version            show version and exit
"""
from docopt import docopt


if __name__ == '__main__':

    arguments = docopt(__doc__, version='1.0.0rc2')

    if isinstance(arguments, dict):
        from model import *
        name = filter(lambda x: arguments[x] != False, [
                      'syncdb', 'query', 'get', 'run', 'analysis'])[0]

        if name == 'get':
            # Download Web pages or insert source data
            exec("from static.GetWebData import %s as runing" %
                 arguments['<jobs>'])

            if arguments.has_key('<update>') and (arguments['<update>'] != None):
                if arguments['<update>'] in ('Up', 'up', 'update', 'Update', 'UP'):
                    run = runing.Get_Html_Up()
                else:
                    raise Exception, 'Error'
            else:
                run = runing.Get_Html()
            run.run()
            run.network.join()

        elif name == 'syncdb':
            # Syncdb database
            if arguments.has_key('<dbname>'):
                database = arguments['<dbname>']
                Loading.init_db(database)
            else:
                Loading.init_db()

        elif name == 'query':
            # Search table
            exec('from static.Analysis.' +
                 arguments['<dbname>'] + ' import Search_runing')
            Search_runing()

        elif name == 'run':
            from WebView.flaskr import app
            app.run()

        elif name == 'analysis':
            exec('from static.Analysis.' +
                 arguments['<ProcessFile>'] + ' import run')
            run()

    else:

        print arguments
