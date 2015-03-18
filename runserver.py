# -*- coding: utf-8 -*-
import os
import sys
import getopt
import flask
from restapi import app
from restapi import config
from flask.ext.sqlalchemy import SQLAlchemy
from werkzeug.contrib.fixers import ProxyFix

reload(sys)
sys.setdefaultencoding('utf-8')

#获取配置参数
try:
    __scritpEnv = ""
    __opts, _ = getopt.getopt(sys.argv[1:], "e:") #获取命令行参数
except Exception as err:
    __opts = {}

for name, value in __opts:
    if name == "-e": #获取命令行参数e
        __scritpEnv = value
if __scritpEnv.lower() == "debug":
    app.config.from_object(config.Debug())
else:
    app.config.from_object(config.Production())

print('running env: {0}'.format(app.config['ENV']))

#session支持
app.secret_key = app.config['SESSION_KEY']

def mkdirFn(path):
    # 引入模块
    
    # 去除首位空格
    path=path.strip()
    # 去除尾部 \ 符号
    path=path.rstrip("\\") 
 
    # 判断路径是否存在
    # 存在     True
    # 不存在   False
    isExists=os.path.exists(path)
 
    # 判断结果
    if not isExists:
        # 如果不存在则创建目录
        print path+' create success'
        # 创建目录操作函数
        os.makedirs(path)
        return True
    else:
        # 如果目录存在则不创建，并提示目录已存在
        print path+' is exist'
        return False

#计算路径，然后创建文件夹
curPath = os.path.split(os.path.realpath(__file__))[0]
logsPath = curPath + os.sep + 'logs'

mkdirFn(logsPath)


from restapi.controllers import *
from restapi.route import *

#优先创建 apiMeLocale 表，所以先加载

if __scritpEnv.lower() != "debug":
    import logging
    log = logging.getLogger('werkzeug')
    log.setLevel(logging.ERROR)

if __name__ == '__main__':
    if __scritpEnv.lower() == "debug" :
        app.run(host=app.config.get("HOST"),port=app.config.get("PORT"))
    else:
        app.wsgi_app = ProxyFix(app.wsgi_app)
        app.run()
elif __scritpEnv.lower() != "debug" :
    app.wsgi_app = ProxyFix(app.wsgi_app)

    
    

