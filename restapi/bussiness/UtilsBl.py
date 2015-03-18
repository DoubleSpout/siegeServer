# -*- coding: utf-8 -*-
#coding=utf-8
from functools import wraps
import flask
import os
import uuid
import json
import calendar
from flask import render_template, request, redirect, url_for, sessions, Response, session, make_response, g
from restapi import app

import urlparse
import urllib
import types
from flask.ext.restful import reqparse, abort, Api, Resource
import datetime
from hashlib import md5
import time


from restapi.bussiness.LoggerBl import log


#define utils Class
class Utils(object):

     @staticmethod
     def checkAndGetExt(fileIns, isMd5Filename):
        if not isinstance(fileIns, object):
            return False, 'empty file', None

        ok, extName = Utils.allowed_file(fileIns.filename)
        #判断扩展名是否匹配
        if not ok:
            return False, 'invalid file type', None

        md5FileName = None
        if isMd5Filename:
            md5FileName = Utils.md5(fileIns.filename + str(Utils.now()))+'.'+extName

        return True, extName, md5FileName

     @staticmethod
     def md5(str):
        m = md5()
        m.update(str)
        return m.hexdigest().upper()


     @staticmethod
     def getFromBoolStr(boolStr):
         if boolStr.lower() == 'false':
             return False
         else:
             return True

     @staticmethod
     def setBoolToStr(boolVal):
         if isinstance(boolVal, bool):
             if boolVal is True:
                 return 'true'

         else:
             return boolVal


     @staticmethod
     def JsonParse(str):
        try:
           resultDict = json.loads(str)
           if isinstance(resultDict, list) or isinstance(resultDict, dict):
               return True,  resultDict
           return False, 'invalid json format'
        except Exception as err:

            return False, Exception

     @staticmethod
     def now():
        return int(time.time())

     @staticmethod
     def getTimestampFromDatetime(d=None):
        if d is None:
            d = datetime.datetime.now()
        return int(time.mktime(d.timetuple()))

     #获取uuid
     @staticmethod
     def getuuid():
        return unicode(uuid.uuid1(os.getpid()))

     @staticmethod
     def nowStr():
        return time.strftime('%Y-%m-%d %H:%M:%S',time.localtime(time.time()))

     @staticmethod
     def todayStr():
        return time.strftime('%Y-%m-%d',time.localtime(time.time()))

     @staticmethod
     def getDateStr(dateTimeObj):
         return dateTimeObj.strftime('%Y-%m-%d %H:%M:%S')

     @staticmethod
     def allowed_file(filename):

         if not '.' in filename:
             return False, None
         extName = filename.rsplit('.', 1)[1].lower()
         if extName in app.config.get("ALLOWED_EXTENSIONS"):
            return True, extName
         else:
            return False, None


     @staticmethod
     def genResponse(ok, obj):
         if ok:
             status = 1
         else:
             status = 0

         return {
            'status':status,
            'data':obj
         }

     @staticmethod
     def genResponseApi(ok, obj):
         if obj is None:
             obj = ''
         resp = {
             'result':obj
         }
         if ok is True:
             resp['status'] = 'ok'
             resp['code'] = 200
         else:
             resp['status'] = 'fail'
             resp['code'] = ok

         return resp

     @staticmethod
     def genResponseApiMaterial(ok, obj):
         if ok is not True:
             return Utils.genResponseApi(ok, obj)

         returnStr = u'{{"code":200,"status":"ok","result":{0}}}'.format(obj)
         return Response(returnStr, mimetype='application/json; charset=utf-8')

     #检查签名
     @staticmethod
     def checkSignIsValid():
         #如果是开发环境，不验证sign
         if app.config['ENV'] == 'Debug':
             return True

         reqKeys = request.values.keys()
         if 'timestamp' not in reqKeys:
             return Utils.genResponseApi(1204, 'need timestamp param')
         if not request.values['timestamp'].isdigit():
             return Utils.genResponseApi(1208, 'invalid format timestamp')
         if 'sign' not in reqKeys:
             return Utils.genResponseApi(1206, 'need sign param ')
         if len(request.values['sign']) != 32:
             return Utils.genResponseApi(1206, 'invalid format sign ')


         nowTs = Utils.getTimestampFromDatetime(datetime.datetime.utcnow())
         if abs(nowTs - int(request.values['timestamp'])) > 60*15:
             return Utils.genResponseApi(1207, 'timestamp expire')


         #排序key字典
         reqKeys = sorted(reqKeys)
         unSignStr = ''
         for key in reqKeys:
             #sign 和 img_data 不参与签名
             if key == 'sign' or key == 'img_data':
                 continue
             unSignStr += key + request.values[key]

         unSignStr += g.device.appSecret
         #进行md5签名
         md5Str = Utils.md5(unSignStr)

         if request.values['sign'].upper() != md5Str:
             return Utils.genResponseApi(1205, 'sign error')

         #验证成功
         return True


     #check sign is Correct
     @staticmethod
     def checkSign(f):
        @wraps(f)
        def decorated_function(*args, **kwargs):
            from restapi.models.apiDeviceModel import apiDevice

            #sign logic
            appId = kwargs.get('appid', 'None')
            if appId is None:
                return Utils.genResponseApi(1201, 'need appid')

            if len(appId) < 32 or len(appId) > 50:
                return Utils.genResponseApi(1202, 'invalid appid')
            #数据库查询appId
            appId = appId.upper()
            result = apiDevice.query.filter(apiDevice.appId == appId).first()
            if not result:
                return Utils.genResponseApi(1203, 'not found appId')

            #将查询到的密钥放入临时变量g中
            g.device = result
            #检查签名

            ok = Utils.checkSignIsValid()
            if ok is True:
                return f(*args, **kwargs)
            else:
                return ok

        return decorated_function

     #生成csrf跨站伪造码
     @staticmethod
     def createCsrf(f):
        @wraps(f)
        def decorated_function(*args, **kwargs):
            g.csrfSign = Utils.md5(str(Utils.getTimestampFromDatetime()) + app.config['CSRF_KEY'])
            session['_csrf'] = g.csrfSign
            return f(*args, **kwargs)

        return decorated_function

     #验证跨站伪造码
     @staticmethod
     def checkCsrf(f):
        @wraps(f)
        def decorated_function(*args, **kwargs):
            csrfVal = request.values.get('_csrf', None)
            if not csrfVal:
                resp = Response(json.dumps(Utils.genResponseApi(1195, 'not found _csrf')), mimetype='application/json')
                return resp
            if csrfVal != session['_csrf']:
                resp = Response(json.dumps(Utils.genResponseApi(1196, 'invalid _csrf')), mimetype='application/json')
                return resp
            return f(*args, **kwargs)

        return decorated_function

     #检查appename
     @staticmethod
     def checkAppEname(f):
        @wraps(f)
        def decorated_function(*args, **kwargs):
            from restapi.models.apiAppModel import apiApp
            appEname = kwargs.get('appename', 'None')
            if not appEname or appEname == '':
                resp = Response(json.dumps(Utils.genResponseApi(1197, 'invalid appEname')), mimetype='application/json')
                return resp

            #查询此app的英文短名
            result = apiApp.query.filter(apiApp.appEname == appEname).first()
            if not result:
                resp = Response(json.dumps(Utils.genResponseApi(1198, 'not found appEname')), mimetype='application/json')
                return resp
            g.apiApp = result

            return f(*args, **kwargs)

        return decorated_function

     @staticmethod
     def checkBackUrl(f):
        @wraps(f)
        def decorated_function(*args, **kwargs):

            #验证回调地址的有效性
            backUrl = request.values.get('back_url', None)
            #没有回调地址默认使用oob
            if not backUrl or backUrl == '':
                backUrl = request.host_url + 'page/oob/'
            else:
            #否则使用传上来的回调地址
                if len(backUrl) > 100:
                    return json.dumps(Utils.genResponseApi(1194, 'back url too long'))
                urlIns = urlparse.urlparse(backUrl)
                requestHost = request.host_url
                if backUrl.find(requestHost + 'page/oob') != 0:
                    if urlIns.hostname is not None and urlIns.hostname != g.apiApp.authHost:
                        return json.dumps(Utils.genResponseApi(1199, 'back_url not auth'))

            session['backUrl'] = backUrl

            return f(*args, **kwargs)

        return decorated_function

     @staticmethod
     def checkPlatName(f):
        @wraps(f)
        def decorated_function(*args, **kwargs):

            platName = kwargs.get('platname', 'None')
            if not platName or (platName not in app.config['PROVIDER']):
                resp = Response(json.dumps(Utils.genResponseApi(1189, 'invalid platname')), mimetype='application/json')
                return resp

            return f(*args, **kwargs)

        return decorated_function

     @staticmethod
     def getUserIdByLoginToken(loginToken):
         from restapi.models.apiLoginLogModel import apiLoginLog
         from restapi.models.apiAllUserModel import apiAllUsers
         if not loginToken or loginToken == '' or len(loginToken) < 32 or len(loginToken) > 50:
             return 1860, 'invalid logintoken'
         loginResult = apiLoginLog.query.filter(apiLoginLog.loginToken == loginToken).first()
         if not loginResult:
             return 1861, 'not found loginResult'
         userId = loginResult.userId
         return True, userId

     #check user token
     @staticmethod
     def checkToken(f):
        @wraps(f)
        def decorated_function(*args, **kwargs):
            #获取并检查logintoken是否有效
            from restapi.models.apiLoginLogModel import apiLoginLog
            from restapi.models.apiAllUserModel import apiAllUsers

            loginToken = request.values.get('logintoken', None)
            if not loginToken or len(loginToken) < 32 or len(loginToken) > 50:
                resp = Response(json.dumps(Utils.genResponseApi(1191, 'missing logintoken param')), mimetype='application/json')
                return resp
            loginResult = apiLoginLog.query.filter(apiLoginLog.loginToken == loginToken).first()
            if not loginResult:
                log.error('Utils.checkToken not found loginttoken, token:{0}, ip:{0}'.format(loginToken, request.remote_addr))
                resp = Response(json.dumps(Utils.genResponseApi(1192, 'not found logintoken')), mimetype='application/json')
                return resp

            #根据获取的用户Id查找用户对象
            userId = loginResult.userId
            userResult = apiAllUsers.query.filter(apiAllUsers.Id == userId, apiAllUsers.isEnable==True).first()
            if not userResult:
                log.error('Utils.checkToken not found userresult, userId:{0}, ip:{0}'.format(str(userId), request.remote_addr))
                resp = Response(json.dumps(Utils.genResponseApi(1193, 'not found user')), mimetype='application/json')
                return resp
            #将用户放置入g请求上下文变量
            g.user = userResult

            return f(*args, **kwargs)
        return decorated_function

     @staticmethod
     def getApiAppByAppId(appId):
         from restapi.models.apiDeviceModel import apiDevice
         result = apiDevice.query.filter(apiDevice.appId == appId).first()
         if not result:
             return False
         return result.api_app

     @staticmethod
     def checkOs(agentStr):
       if agentStr.find('Android') > 0 or agentStr.find('Linux') > 0:
           return 'android'
       elif agentStr.find('Mac OS') > 0 or agentStr.find('iPhone') > 0 or agentStr.find('iPad') > 0:
           return 'ios'
       else:
           return 'other'

     @staticmethod
     def addParam(url, key, val):
       if url.find('?') > 0:
           return '{0}&{1}={2}'.format(url, key, urllib.quote(val))
       else:
           return '{0}?{1}={2}'.format(url, key, urllib.quote(val))



class ResponseMsg(object):
    OK = 'ok'
    FAIL = 'fail'
    ERROR = 'error'
    NOT_FOUND = 'not found'


class CrossOrigin(Resource):
    def options(self):
        resIns = Response()
        resIns.headers.add('Access-Control-Allow-Origin', u'*')
        resIns.headers.add('Access-Control-Allow-Credentials', u'true')
        resIns.headers.add('Access-Control-Allow-Methods', u'*')
        resIns.status_code = 200
        return resIns



class DumpToDict(object):
    def __init__(self):
        self.sqlData = None #dump key
        pass
    def dumpToList(self, result=None):
        if not result:
            result = self.sqlData

        #获取model的所遇key
        keyList = self.__mapper__.c.keys()
        #定义数组

        if isinstance(result, list):
            resultLength = len(result)
            tempList = range(resultLength)
            i = 0

            for sqlObj in result:
                tempList[i] = {}
                for key in keyList:
                    tempList[i][key] = getattr(sqlObj, key)
                    if isinstance(tempList[i][key], datetime.date):
                        tempList[i][key] = tempList[i][key].strftime("%Y-%m-%d %H:%M:%S")
                i += 1
        else:
            tempList = {}
            for key in keyList:
                    tempList[key] = getattr(result, key)
                    if isinstance(tempList[key], datetime.date):
                        tempList[key] = tempList[key].strftime("%Y-%m-%d %H:%M:%S")

        return tempList