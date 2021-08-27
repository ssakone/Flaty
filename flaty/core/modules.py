from PySide2.QtQml import *
from PySide2.QtCore import *
from flask import Flask , request, render_template
from werkzeug.utils import secure_filename
import subprocess, os
import json  
from settings import *
import os
import copy 
import random
import shutil
import flask_login
from datetime import date

from peewee import *
from .template import *

dataURi = {}
modelList = {}

db = SqliteDatabase('people.db')

def loadJs():
	if "onCall" in dataURi[request.path].toVariant():
		cal = dataURi[request.path].property('onCall')
	else:
		fname = dataURi[request.path].property('path').toString()
		cal = QJSEngine().evaluate(open("views/js/{}".format(fname)).read());
	datas = {}
	if request.method=="POST":
		datas = request.form.to_dict()
		if 'file' in request.files:
			file = request.files['file']
			filename = secure_filename(file.filename)
			tempName = str(random.randrange(999999,9999999))
			tempName = tempName+"."+filename.split(".")[1]
			file.save(os.path.join(app.config['UPLOAD_TEMPS_FOLDER'], tempName))
			datas['fileName'] = filename
			datas['tempFileName'] = tempName 
	else:
		datas = request.args.to_dict()

	return cal.call([json.dumps(datas)]).toString()

def add_url(rule, endpoint, methods, app):
	app.add_url_rule(rule, str(endpoint), loadJs ,methods=methods)


class Router(QObject):

	def __init__(self, app = None, engine = None):
		QObject.__init__(self)
		self.app = app
		self.engine = engine

	@Slot(QJSValue)
	def route(self, route):
		dataURi[route.property('route').toString()] = route
		route = route.toVariant()
		try:
			method = route['methods']
		except:
			method = ["GET"]
		add_url(route["route"], route["name"], method, self.app)
	@Slot(QJSValue)
	def load(self, route):
		dataURi[route.property('route').toString()] = route
		route = route.toVariant()
		try:
			method = route['methods']
		except:
			method = ["GET"]
		add_url(route["route"], route["name"], method)

class Py(QObject):

	def __init__(self, app = None, engine = None):
		QObject.__init__(self)
		self.app = app
		self.engine = engine

	@Slot(str)
	def print(self, info):
		print(info)
	@Slot(str, str, result=bool)
	def move(self, start, end):
		shutil.move(os.path.join(app.config['UPLOAD_TEMPS_FOLDER'], start), os.path.join("", end))
		return True

		add_url(route["route"], route["name"], method)

class Template(QObject):
	def __init__(self, app = None, engine = None):
		QObject.__init__(self)
		self.app = app
		self.engine = engine
	@Slot(str, list, result=str)
	def render(self, fname, datas):
		return render_template(fname+".html", datas=datas[0])

class ModelObject(QObject):
	def __init__(self, app = None, engine = None):
		QObject.__init__(self)
		self.app = app
		self.engine = engine
	current_id = -1
	mode = None
	@Slot(QJSValue, QJSValue, result=int)
	def create(self, table, data):
		data = data.toVariant()
		model = modelList[table.toString()]
		c = model.create(**data)
		return c.id
	@Slot(QJSValue, int, result=int)
	def delete(self, table, ids):
		model = modelList[table.toString()]
		c = model.select().where(model.id == ids).get()
		c.delete_instance()
		return c

class JSModel(QObject):
	def __init__(self, app = None, engine = None):
		QObject.__init__(self)
		self.app = app
		self.engine = engine
	@Slot(QJSValue)
	def new(self, data): 
		cols = data.property('columns').toVariant()
		name = data.property('name').toString()
		col_list = []
		for col in cols:
			argList = []
			if "default" in col and col['type']=="CharField":
				argList.append("default='{}'".format(col['default']))
			if "default" in col and col['type']=="IntField":
				argList.append("default={}".format(col['default']))
			if "null" in col:
				argList.append("null={}".format(str(col['null'])))
			if "auto_now" in col:
				if col['auto_now']:
					argList.append("default=datetime.datetime.now")
			if "backref" in col:
				argList.append("backref='{}'".format(col['backref']))
			if "constraints" in col:
				argList.append("constraints=[{}]".format(col['constraints']))
			if "max_length" in col:
				argList.append("max_length={}".format(col['max_length']))
			if "model" in col:
				argList.append("model={}".format(modelList[col['model']]))
			col_list.append("{} = {}({})".format(col['name'],col['type'],",".join(argList)))
		new_model = CLASS_TEMPLATE.format(name,"\n\t".join(col_list),name, name)
		c = exec(new_model)
		db.create_tables([modelList[name]])
	@Slot(QJSValue, QJSValue, result=QJSValue)
	def create(self, table, data):
		data = data.toVariant()
		model = modelList[table.toString()]
		c = model.create(**data)
		obj = ModelObject()
		obj.mode = "item"
		obj.model = c
		ob = self.engine.newQObject(obj)
		return ob
	@Slot(QJSValue, int, result=int)
	def delete(self, table, ids):
		model = modelList[table.toString()]
		c = model.select().where(model.id == ids).get()
		c.delete_instance()
		return c
		
	@Slot(QJSValue, result=QJSValue)
	def charField(self, data):
		data.setProperty('type', 'CharField')
		return data
	@Slot(QJSValue, result=QJSValue)
	def intField(self, data):
		data.setProperty('type', 'IntegerField')
		return data
	@Slot(QJSValue, result=QJSValue)
	def dateField(self, data):
		data.setProperty('type', 'DateTimeField')
		return data
	@Slot(QJSValue, result=QJSValue)
	def foreignField(self, data):
		data.setProperty('type', 'ForeignKeyField')
		return data
	@Slot(QJSValue, result=QJSValue)
	def textField(self, data):
		data.setProperty('type', 'TextField')
		return data
