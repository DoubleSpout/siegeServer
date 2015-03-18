# -*- coding: utf-8 -*-

from flask import Flask, request
from flask.ext.restful import Resource, Api
from restapi.controllers.WelcomeController import Welcome, jmeterTest
from restapi.controllers.CommandController import Command
from restapi.controllers.ZabbixController import Zabbix
from restapi.controllers.MultiUploadController import save, delete
from restapi import app

api = Api(app)
api.add_resource(Welcome, '/')
#发送和获取压测命令接口
api.add_resource(Command, '/v1/command/')
#拉去zabbix性能监控接口
api.add_resource(Zabbix, '/v1/zabbix')

#附件上传
app.add_url_rule('/upload/save', 'multiUploadSave', save, methods=['POST'])
app.add_url_rule('/upload/delete', 'multiUploadRemove', delete, methods=['POST'])
#jmeter测试页面
app.add_url_rule('/jmeter', 'JMeter', jmeterTest, methods=['GET'])
