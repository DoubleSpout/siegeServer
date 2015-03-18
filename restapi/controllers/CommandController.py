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
from restapi.bussiness.CommandBl import CommandBl
from restapi import config
from restapi import app

#save device get appid and secret
commandGetParser = reqparse.RequestParser()
commandGetParser.add_argument('sid', type=str, dest='sessionId', location='args')

postCommandJsonParser = reqparse.RequestParser()
postCommandJsonParser.add_argument('cmd_json', type=str, dest='cmdJson', location='form')

#一个指令的示例
#[
#     {
#       "host":"192.168.1.1",  //用来标示去哪台zabbix上获取性能监控
#       "type" : "jmete",      //调用命令的类型，目前仅支持jmete
#       "cmd":"ls /etc"        //执行本机的命令行，打印ls输出
#       "param": {             //jmete可选参数配置等
#                   "nThreadNum": 20,
#                   "nRampUpTime":30,
#                    ...
#               }
# ]



class Command(CrossOrigin):
    #获取命令行执行情况输出
    def get(self):
        args = commandGetParser.parse_args()
        sessionId = args.get('sessionId')
        commandIns = CommandBl(sessionId)
        return Utils.genResponseApi(*commandIns.getInfo())

    #发送指令
    def post(self):
        args = postCommandJsonParser.parse_args()
        cmdJson = args.get('cmdJson')
        try:
            cmdJson = json.loads(cmdJson)
        except Exception as err:
            return Utils.genResponseApi(False, 'Invalid json str')

        if not isinstance(cmdJson, list):
            return Utils.genResponseApi(False, 'post json must be a list')

        commandIns = CommandBl()
        ok, sessionId = commandIns.runCommand(cmdJson)
        return Utils.genResponseApi(ok, sessionId)


