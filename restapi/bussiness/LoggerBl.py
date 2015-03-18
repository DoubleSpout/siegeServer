# -*- coding: utf-8 -*-
import logging
import os
from logging.handlers import TimedRotatingFileHandler
from restapi import app
from restapi import config

#设置logger模块
log = logging.getLogger('mylogger')
log.setLevel(logging.DEBUG)
#fh = logging.FileHandler( os.path.join('logs','{0}.log'.format(config.Config.LOGGER_NAME)))
#fh.setLevel(logging.DEBUG)
formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')

fileTimeHandler = TimedRotatingFileHandler(os.path.join('logs','{0}.log'.format(config.Config.LOGGER_NAME)), "D", 1, 30)
logging.basicConfig(level = logging.INFO)
fileTimeHandler.setFormatter(formatter)

#fh.setFormatter(formatter)
log.addHandler(fileTimeHandler)
log.info('log start in {0}'.format(app.config['ENV']))