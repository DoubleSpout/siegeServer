# -*- coding: utf-8 -*-
#coding=utf-8

#import package
import os
import flask
import json
from flask import flash, render_template, request, redirect, url_for, sessions, Response, session, make_response
import httplib
import urllib
import json
from xml.dom.minidom import parse, parseString
from datetime import datetime


from restapi import app
from restapi.bussiness.UtilsBl2 import Utils

#如果不存在上传文件目录，则创建
uploadPath = app.config.get('UPLOAD_FOLDER')
if not os.path.isdir(uploadPath):
    os.mkdir(uploadPath)

def save():
    file = request.files.get('upload_file', None)
    #检查格式
    ok, extName, saveFileName = Utils.checkAndGetExt(file, True)

    if not ok:
        return extName, 400
    #保存文件
    file.save(os.path.join(app.config.get('UPLOAD_FOLDER'), saveFileName))
    return Response(json.dumps({'result':'/static/upload/'+saveFileName}), mimetype='application/json; charset=utf-8')



def delete():
    return Response(json.dumps({}), mimetype='application/json; charset=utf-8')
