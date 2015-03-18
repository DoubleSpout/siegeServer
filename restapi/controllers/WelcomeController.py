# -*- coding: utf-8 -*-
#coding=utf-8

#import package
import os
import flask
import json
from flask import render_template, request, redirect, url_for, sessions, Response, session, make_response
import httplib
import urllib
from xml.dom.minidom import parse, parseString
from datetime import datetime
from flask.ext.restful import reqparse, abort, Api, Resource


#import custom
from restapi.bussiness.UtilsBl import Utils, CrossOrigin




class Welcome(CrossOrigin):
    def get(self):
        return Utils.genResponse(True, 'welcome siege server')



def jmeterTest():
    return render_template('jmeterTest.html')