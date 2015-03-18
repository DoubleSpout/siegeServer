# -*- coding: utf-8 -*-
from datetime import datetime
from flask import Flask
from flask.ext.sqlalchemy import SQLAlchemy
from restapi import app
import redis

#db = SQLAlchemy(app)


_pool = redis.ConnectionPool(host=app.config['REDIS_HOST'], port=app.config['REDIS_PORT'], db=app.config['REDIS_DB'])
r = redis.Redis(connection_pool=_pool)