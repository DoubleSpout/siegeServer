# -*- coding: utf-8 -*-
import sys,os
from urllib import quote_plus as urlquote
import platform

def cur_file_dir(fileDirPath='logs'):
    #获取脚本路径
    path = os.sep.join(sys.path[0].split('/'))

    #判断为脚本文件还是py2exe编译后的文件，如果是脚本文件，则返回的是脚本的目录，如果是py2exe编译后的文件，则返回的是编译后的文件路径
    if os.path.isdir(path):
        pass
    elif os.path.isfile(path):
        path = os.path.dirname(path)
    return path+os.sep+fileDirPath

    
class Config(object):
    DEBUG = False
    TESTING = False
    SQLALCHEMY_DATABASE_URI = 'mysql://root:@127.0.0.1/tc_report'
    SQLALCHEMY_POOL_SIZE = 5
    SQLALCHEMY_POOL_RECYCLE = 499
    SQLALCHEMY_POOL_TIMEOUT = 60

    HOST = "0.0.0.0"
    PORT = 8000
    MANAGER_PORT = 8124

    REDIS_HOST = '127.0.0.1'
    REDIS_PORT = 6379
    REDIS_DB = 0

    LOG_PATH = cur_file_dir()

    LOGGER_NAME = 'mylog'
    SESSION_KEY = '05599c095f5900cc288bcadd9f9b4c34'
    CSRF_KEY = '6e7b631112254ac79b2423a83f98800b'
    P3P_HEADER = 'CURa ADMa DEVa PSAo PSDo OUR BUS UNI PUR INT DEM STA PRE COM NAV OTC NOI DSP COR'


    #manager config
    MAX_CONTENT_LENGTH = 16 * 1024 * 1024
    UPLOAD_FOLDER = cur_file_dir('restapi') + os.sep + 'static' + os.sep + 'upload'
    ALLOWED_EXTENSIONS = set(['txt', 'pdf', 'png', 'jpg', 'jpeg', 'gif','jmx'])
    USER_INIT_PASSWORD = '123456'

    JMETER_START_CMD = u'/usr/local/apache-jmeter/bin/jmeter.sh'


    #windows下和非win下分别解压到不同目录
    if platform.system() == 'Windows':
        TEMP_SOURCE_FOLDER = 'C:\\temp_source\\'
    else:
        TEMP_SOURCE_FOLDER = cur_file_dir('temp_source')

    STATIC_SOURCE_PATH = os.path.join(cur_file_dir('restapi'), 'static')

class Production(Config):
    ENV = 'Production'

    PORT = 5000
    DEBUG = False
    TESTING = False


class Debug(Config):
    ENV = 'Debug'
    DEBUG = True
    SQLALCHEMY_ECHO = True


staticPath = cur_file_dir('restapi') + os.sep + 'static'
if not os.path.isdir(staticPath):
    os.mkdir(staticPath)