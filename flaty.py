from PySide2.QtQml import *
from PySide2.QtCore import *
from flask import Flask , request, render_template
from werkzeug.utils import secure_filename
import subprocess, os
import json  
import os
import copy 
import random
import shutil
import flask_login
from datetime import date

from peewee import *

from .core.modules import *


application = QCoreApplication([])

class Flaty:
	def __init__(self, filename):
		self.filename = filename

		self.engine = QJSEngine()
		
		self.app = Flask(__name__, static_url_path='')

		self.engine.installExtensions(QJSEngine.TranslationExtension | QJSEngine.ConsoleExtension);

		self.load("Python", Py(self.app, self.engine))
		self.load("Template", Template(self.app, self.engine))
		self.load("Routers", Router(self.app, self.engine))
		self.load("Model", JSModel(self.app, self.engine))

		db.connect()

	def load(self, name, object):

		object.setParent(QCoreApplication.instance())
		self.engine.globalObject().setProperty(name, self.engine.newQObject(object))

	def add_routes(self, route_filename):
		self.engine.evaluate(open(route_filename).read()).call()
	def add_models(self, model_filename):
		self.engine.evaluate(open("models.js").read()).call([])

	def run(self, auto_reload=False):
		self.app.jinja_env.auto_reload = auto_reload
		self.app.config['TEMPLATES_AUTO_RELOAD'] = auto_reload
		self.app.run()
