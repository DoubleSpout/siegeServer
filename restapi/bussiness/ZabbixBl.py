# -*- coding: utf-8 -*-
#import package
from functools import wraps
import flask
import hashlib
import time
import httplib
import urllib
import json
import calendar
from datetime import datetime
from flask import render_template, request, redirect, url_for, sessions, Response, session
from sqlalchemy import *
from flask.ext.sqlalchemy import SQLAlchemy
from sqlalchemy.orm import load_only, joinedload, dynamic_loader, lazyload, defer, undefer
from sqlalchemy.ext.serializer import loads, dumps
import requests
import random

from hashlib import md5

#import restapi
from restapi import app
from restapi import config
import time
import datetime

from restapi.bussiness.LoggerBl import log
from restapi.bussiness.UtilsBl import ResponseMsg, Utils



class Zabbix(object):

    def __init__(self, sessionId):
        self.sessionId = sessionId

    #根据sessionId获取zabbix的监控数据
    def getInfo(self):
        pass
