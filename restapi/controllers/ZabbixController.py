# -*- coding: utf-8 -*-
#coding=utf-8

#import package
import os
import flask
import json
from flask import render_template, request, redirect, url_for, sessions, Response, session, make_response
import httplib
import urllib
import re
from xml.dom.minidom import parse, parseString
from datetime import datetime
from flask.ext.restful import reqparse, abort, Api, Resource

#import custom
from restapi.bussiness.UtilsBl import Utils, CrossOrigin
from restapi.bussiness import LoggerBl, ZabbixBl
from restapi import config
from restapi import app

#save device get appid and secret
zabbixParser = reqparse.RequestParser()
zabbixParser.add_argument('sid', type=str, dest='sessionId', location='args')

#错误码使用10xx
class Zabbix(CrossOrigin):
    #根据sessionId获取Zabbix的输出
    def get(self):
        args = zabbixParser.parse_args()
        sessionId = args.get('sessionId')
        zabbixIns = ZabbixBl(sessionId)
        return Utils.genResponseApi(*zabbixIns.getInfo())
