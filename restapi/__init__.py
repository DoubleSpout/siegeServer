#!/usr/bin/env python
from flask import Flask
import config


app = Flask(__name__,static_folder='static', static_url_path='/static')

