# -*- coding: utf-8 -*-
#coding=utf-8
from functools import wraps
import flask
from flask import render_template, request, redirect, url_for, sessions, Response, session
import urllib
import types
from sqlalchemy import Text, desc, text
from datetime import datetime
import time
from hashlib import md5

from restapi import app
from restapi.models.dbModel import *


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
     def now():
        return int(time.time())

     @staticmethod
     def allowed_file(filename):
         if not '.' in filename:
             return False, None
         extName = filename.rsplit('.', 1)[1].lower()
         if extName in app.config.get("ALLOWED_EXTENSIONS"):
            return True, extName.lower()
         else:
            return False, None

     @staticmethod
     def getFromBoolStr(boolStr):
         if boolStr.lower() == 'false':
             return False
         elif boolStr.lower() == 'true':
             return True
         else:
             return boolStr

     @staticmethod
     def setBoolToStr(boolVal):
         if isinstance(boolVal, bool):
             if boolVal is True:
                return 'true'
             else:
                return 'false'
         else:
             return boolVal

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

     #check sign is Correct
     @staticmethod
     def checkSign(f):
        @wraps(f)
        def decorated_function(*args, **kwargs):
            #sign logic
            print('in check sign func')
            return f(*args, **kwargs)
        return decorated_function

     #check user token
     @staticmethod
     def checkToken(f):
        @wraps(f)
        def decorated_function(*args, **kwargs):
            #sign logic
            print('in check token func')
            return f(*args, **kwargs)
        return decorated_function






class DumpToDictKendo(object):
    def __init__(self):
        pass
    def dumpToListKendo(self, result=None):
        if not result:
            result = getattr(self, 'sqlData', None)
        #如果没有sqlData
        if not getattr(self, 'sqlData', None):
            result = self

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
                    #如果是None,则为空
                    if tempList[i][key] is None:
                        tempList[i][key] = ''
                    elif isinstance(tempList[i][key], datetime):
                        tempList[i][key] = tempList[i][key].strftime("%Y-%m-%d %H:%M:%S")
                    elif isinstance(tempList[i][key], bool):
                        tempList[i][key] = Utils.setBoolToStr(tempList[i][key])
                i += 1
        else:
            tempList = {}
            for key in keyList:
                    tempList[key] = getattr(result, key)
                    #如果是None,则为空
                    if tempList[key] is None:
                        tempList[key] = ''
                    elif isinstance(tempList[key], datetime):
                        tempList[key] = tempList[key].strftime("%Y-%m-%d %H:%M:%S")
                    elif isinstance(tempList[key], bool):
                        tempList[key] = Utils.setBoolToStr(tempList[key])

        return tempList

#解析kendoui参数的类
class kendouiData(object):

    #将时间字符串转为字符串
    def parseTimeStr(self, timeStr):

        try:
            timeStr = timeStr.split('(')[0].strip()
            timeString = datetime.strptime(timeStr, "%a %b %d %Y %H:%M:%S %Z 0800").strftime("%Y-%m-%d %H:%M:%S")
        except Exception as err:
            return False, err

        return True, timeString

    #将数组拼接成条件字符串
    def joinCoditionList(self, conditionList=None, curLogic = None):
        if not conditionList:
            conditionList = self.ormFilterList
        if not curLogic:
            curLogic = 'and'

        tempList = []
        for item in conditionList:
            tempList.append('({0})'.format(item))

        return True, curLogic.join(tempList)



    def genConditionStr(self, filters=None, curFilterList=None):
        if not filters:
            return False, None

        if not curFilterList:
            curFilterList = self.ormFilterList

        self.valueCount += 1

        key = filters.get('field', '')
        keyIsDate = None
        dateOk = True
        operator = filters.get('operator', '')
        value = filters.get('value', '')
        genStr = None

        #布尔值转换
        value = Utils.getFromBoolStr(value)

        #如果是日期字段
        if key.lower().find('time') > 0 or key.lower().find('date') > 0:
            keyIsDate = True

        #如果是等于操作符
        if operator == 'eq':
            genStr = '({0} = :v{1})'.format(key, self.valueCount)
            if keyIsDate:
                dateOk, value = self.parseTimeStr(value)

        #如果是不等于操作
        elif operator == 'neq':
            genStr = '({0} <> :v{1})'.format(key, self.valueCount)
            if keyIsDate:
                dateOk, value = self.parseTimeStr(value)

        #如果是起始于操作
        elif operator == 'startswith':
            genStr = '({0} like :v{1})'.format(key, self.valueCount)
            value = value+'%'

        #如果包含操作
        elif operator == 'contains':
            genStr = '({0} like :v{1})'.format(key, self.valueCount)
            value = '%'+value+'%'

        #如果是结束于操作
        elif operator == 'endswith':
            genStr = '({0} like :v{1})'.format(key, self.valueCount)
            value = '%'+value

        #如果是不包含操作
        elif operator == 'doesnotcontain':
            genStr = '({0} not like :v{1})'.format(key, self.valueCount)
            value = '%'+value+'%'

        #如果是大于等于操作
        elif operator == 'gte':
            genStr = '({0} >= :v{1})'.format(key, self.valueCount)
            if keyIsDate:
                dateOk, value = self.parseTimeStr(value)

        #如果是大于操作
        elif operator == 'gt':
            genStr = '({0} > :v{1})'.format(key, self.valueCount)
            if keyIsDate:
                dateOk, value = self.parseTimeStr(value)

        #如果是小于等于操作
        elif operator == 'lte':
            genStr = '({0} < :v{1})'.format(key, self.valueCount)
            if keyIsDate:
                dateOk, value = self.parseTimeStr(value)


        #如果是小于操作
        elif operator == 'lt':
            genStr = '({0} <= :v{1})'.format(key, self.valueCount)
            if keyIsDate:
                dateOk, value = self.parseTimeStr(value)

        #如果日期出错
        if not dateOk:
            return False, None

        #如果匹配了操作符
        if genStr:
            curFilterList.append(genStr)
            self.ormFilterValue['v{0}'.format(self.valueCount)] = value
            return True, genStr
        else:
            return False



    def parseKendoData(self, paramObj=None):
        if not paramObj:
            paramObj = parse(self.kendoParam)

        self.ormSkip = paramObj.get('skip', 0)
        self.ormLimit = paramObj.get('pageSize', 20)
        self.orderBy = paramObj.get('orderBy', 'Id ')
        self.ormFilterList = []
        self.ormFilterValue = {}
        self.ormFilterStr = ''

        filter = paramObj.get('filter', {})
        filterList = filter.get('filters', {})
        filterGolbalLogic = filter.get('logic', 'and')

        #循环条件
        self.valueCount = 0
        for key in filterList:
            item = filterList[key]
            if not item:
                continue

            subFilters = item.get('filters', None)
            #如果是单条件
            if not subFilters:
                ok, genStr = self.genConditionStr(item)
                if not ok:
                    return False
            #如果是多条件
            elif isinstance(subFilters, dict):
                subLogic = item.get('logic', 'and')
                #对子条件进行循环
                curFilterList = []
                for key2 in subFilters:
                    subItem = subFilters[key2]
                    ok = self.genConditionStr(subItem, curFilterList)
                #将子条件拼接
                ok, joinedStr = self.joinCoditionList(curFilterList, subLogic)
                if not ok:
                    return False
                #将子条件做好拼接，放入数组中
                self.ormFilterList.append(joinedStr)

        ok, self.ormFilterStr = self.joinCoditionList(self.ormFilterList, filterGolbalLogic)

        return ok

    def getData(self):
        #将kendoui的参数解析为orm的参数
        self.parseKendoData()
        #实例化admin类
        objIns = self.modelClass()
        #查询数据
        objQuery = self.modelClass.query
        #如果有filter条件
        if self.ormFilterStr != '':
            objQuery = objQuery.filter(text(self.ormFilterStr))\
                                   .params(**self.ormFilterValue)
        #查询总数
        total = objQuery.count()

        objQuery = objQuery\
            .order_by(desc(self.modelClass.Id))\
            .offset(self.ormSkip)\
            .limit(self.ormLimit)

        dataQueryList = objQuery.all()
        #将查询的数据转为dict
        self.sqlData = objIns.sqlData = dataQueryList

        #如果总数为0，则显示空数组
        if total == 0:
            dataList = []
        else:
            dataList = objIns.dumpToListKendo()

        return True, {
            'Total': total,
            'AggregateResults':None,
            'Errors':None,
            'Data': dataList
        }


    #获取并保存数据
    def saveData(self):

        self.saveModel = parse(self.saveModel)

        if self.saveModel.get('models') and isinstance(self.saveModel, dict):
            self.saveModel = self.saveModel['models'].get('0', None)

        if not self.saveModel:
            return False, u'更新对象参数有误'

        keyList = self.modelClass.__mapper__.c.keys()

        #将key和字段对应起来
        insObj = {}
        for key in keyList:
            if self.saveModel.get(key, None):
                value = self.saveModel.get(key, None)
                if value is None:
                    continue
                elif value == 'true':
                    value = True
                elif value == 'false':
                    value = False
                elif key.lower().find('time') > 0 or key.lower().find('date') > 0:
                    ok, tmpValue = self.parseTimeStr(value)
                    if not ok:
                        continue
                    value = tmpValue

                insObj[key] = value


        #进行数据库操作
        if insObj.get('Id', None) is None or int(insObj['Id']) == 0:
            #实例化model类
            modelIns = self.modelClass(insObj)
            db.session.add(modelIns)
        else:
            #查询记录
            result = self.modelClass.query.filter(self.modelClass.Id==insObj['Id']).first()
            #更新记录
            for key in insObj:
                setattr(result, key, insObj[key])

        db.session.commit()

        return True, insObj

    def delData(self):
        self.delModel = parse(self.delModel)

        if self.delModel.get('models') and isinstance(self.delModel, dict):
            self.delModel = self.delModel['models'].get('0', None)

        if not self.delModel:
            return False, u'删除对象参数有误'

        delId = self.delModel.get('Id', None)
        if not delId:
            return False, u'Id参数有误'

        #实例化model类
        #insObj = self.modelClass({'Id':int(delId)})
        #进行数据库操作
        self.modelClass.query.filter(self.modelClass.Id == delId).delete()
        #db.session.delete(insObj)
        db.session.commit()

        return True, {}


class SimpleBl(kendouiData):
    def __init__(self):
        pass
    #获取列表页
    def getList(self):
        return self.getData()

    #添加或者更新一条记录
    def saveOne(self):

        return self.saveData()

    #删除一条记录
    def delOne(self):
        return self.delData()

    def getAndCheckSaveModel(self):
       self.saveModel = parse(self.saveModel)
       if isinstance(self.saveModel, dict):
            self.saveModel = self.saveModel['models'].get('0', None)
            return True, self.saveModel
       else:
            return False, u'更新对象参数有误'

    def getAndCheckDelModel(self):
       self.delModel = parse(self.delModel)
       if isinstance(self.delModel, dict):
            self.delModel = self.delModel['models'].get('0', None)
            return True, self.delModel
       else:
            return False, u'更新对象参数有误'

    def isCreate(self):
         if self.saveModel['Id'] is None or int(self.saveModel['Id']) == 0:
            del self.saveModel['Id']
            return True
         return False