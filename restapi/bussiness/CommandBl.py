# -*- coding: utf-8 -*-
#import package
from functools import wraps
import flask
import hashlib
import uuid
import os
import platform
import subprocess
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

#import restapi
from restapi import app
from restapi import config
from restapi.models.dbModel import r
import time
import datetime

from restapi.bussiness.LoggerBl import log
from restapi.bussiness.UtilsBl import ResponseMsg, Utils
from restapi.lib.jmeteParseController import parseJMeterParam


#检测和生成文件夹
jmeterPath = os.path.join(app.config.get('STATIC_SOURCE_PATH'), 'jmeter')
if not os.path.isdir(jmeterPath):
    os.mkdir(jmeterPath)

outputPath = os.path.join(app.config.get('STATIC_SOURCE_PATH'), 'output')
if not os.path.isdir(outputPath):
    os.mkdir(outputPath)

class CommandBl(object):

    def __init__(self, sessionId=None):
        self.sessionId = sessionId

    #执行命令
    def runCommand(self, commandArray=[]):
        self.commandArray = commandArray
        ok, result  = self. __parseCommand()
        if not ok:
            return ok, result

        ok, result = self.saveToRedis()
        if not ok:
            return ok, result

        return True, self.sessionId

    #执行console命令
    def __runConsoleCommand(self, item):
        runCmd = self.genNoHupCommand(item['cmd'], item['stdout'])
        try:
            subprocess.call([runCmd], shell=True)
        except Exception as err:
            return False, err
        return True, 'ok'

    #执行Jmete命令
    def __runJmeteCommand(self, item):
        #开始编写jmete配置
        itemParam = item.get('param')
        #机器配置
        dctMachineParam = {}
        dctMachineParam["sJMeterConsole"] = itemParam.get("sJMeterConsole", '')
        dctMachineParam["lstJMeterServer"] = itemParam.get("lstJMeterServer", '')

        #脚本配置
        dctCaseScenario = {}
        dctCaseScenario["nTotalTestDuration"] = itemParam.get("nTotalTestDuration", '')
        dctCaseScenario["nCaseTimeOut"] = itemParam.get("nCaseTimeOut", '')
        #获取case脚本地址
        dctCaseScenario["sCaseScriptPath"] = itemParam.get("sCaseScriptPath", '')
        pathList = dctCaseScenario["sCaseScriptPath"].split('/')
        if len(pathList) == 0:
            return False, 'invalid param sCaseScriptPath'
        scriptPath = os.path.join(app.config.get('UPLOAD_FOLDER') ,pathList[len(pathList)-1])
        if not os.path.exists(scriptPath):
            return False, 'not found sCaseScriptPath'
        dctCaseScenario["sCaseScriptPath"] = scriptPath
        dctCaseScenario["nCaseRunType"] = itemParam.get("nCaseRunType", '')
        dctCaseScenario["nWaitTimeBeforeReport"] = itemParam.get("nWaitTimeBeforeReport", '')

        #字典参数
        dctJMeterParam= {}
        dctJMeterParam["nThreadNum"] = itemParam.get("nThreadNum", '')
        dctJMeterParam["nRampUpTime"] = itemParam.get("nRampUpTime", '')        #Sec as as unit.

        #工具配置
        dctToolParam = {}
        dctToolParam["sToolPath"] = app.config.get('JMETER_START_CMD')
        dctToolParam["bNeedToolLog"] = True
        dctToolParam["sToolLogPath"] = os.path.join(jmeterPath, '{0}_{1}.jtl'.format(self.sessionId, item['i']))
        dctToolParam["bSetAggregateLogPath"] = True
        dctToolParam["sAggregatePath"]= os.path.join(jmeterPath, '{0}_{1}.csv'.format(self.sessionId, item['i']))

        #定义jmeter字典
        jmeterDict = {
            'dctMachineParam':dctMachineParam,
            'dctCaseScenario':dctCaseScenario,
            'dctJMeterParam':dctJMeterParam,
            'dctToolParam':dctToolParam,
        }
        #获取jmeter启动命令
        runCmd = parseJMeterParam(jmeterDict)
        runCmd = self.genNoHupCommand(runCmd)
        try:
            subprocess.call([runCmd], shell=True)
        except Exception as err:
            return False, str(err)
        return True, 'ok'


    #解析命令
    def __parseCommand(self):
        self.sessionId = Utils.md5(Utils.getuuid())
        self.cmdList = []
        i = 0
        for item in self.commandArray:
            if not item.get('host'):
                return False, 'Invalid json format, not found host'
            tempItem = {
                'i':i,                   #记录当前数组位置
                'host': item.get('host'),#记录目标host地址
                'cmd':item.get('cmd', ''),#执行的命令
                'stdout':os.path.join(outputPath, '{0}_{1}.txt'.format(self.sessionId, i)),#stdout文件存放url地址
                'param':item.get('param', {}),#命令执行参数
                'type':item.get('type', ''),#类型，目前仅支持jmete
            }

            #如果任务是jmete的，则执行jmete命令
            if item.get('type') == 'jmeter':
                ok, result = self.__runJmeteCommand(tempItem)
            #其他的暂时不支持,直接执行命令行
            else:
                ok, result = self.__runConsoleCommand(tempItem)
            #如果运行出错
            if ok is not True:
                return ok, result
            self.cmdList.append(tempItem)
            i += 1

        return True, 'ok'


    #保存控制台输出，生成
    def genNoHupCommand(self, cmd, stdOutPath='/dev/null'):
        if platform.system() == 'Windows':
            return cmd
        else:
            cmd = 'nohup {0} > {0} 2>&1 &'.format(cmd, stdOutPath)
            print cmd
            return cmd

    #生成SessionId用来
    def saveToRedis(self):
        try:
            jsonStr = json.dumps(self.cmdList)
        except Exception as err:
            return False, 'json dumps error'

        r.set(self.sessionId, jsonStr)
        r.expire(self.sessionId, 3600*24)#过期时间设置为1天
        return True, self.sessionId

    #根据sessionId获取输出信息
    def getInfo(self):
        result = r.get(self.sessionId)
        if result is None:
            return False, 'not found data'
        try:
            resultDict = json.loads(result)
        except Exception as err:
            return False, 'parse json str error'

        return True, resultDict


