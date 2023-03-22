# -*- coding: utf-8 -*-

import os
import tomllib

from flask import current_app
from flask import Flask
from flask import g
from flask_login import LoginManager
from werkzeug.local import LocalProxy

from mindMapper.core import Wiki
from mindMapper.web.user import UserManager

class WikiError(Exception):
  pass


def get_wiki():
  wiki = getattr(g, '_wiki', None)
  if wiki is None:
    wiki = g._wiki = Wiki(
      current_app.config['CONTENT_DIR'],
      current_app.config['CONFIG_PATH'],
      current_app.config['CACHE_PATH']
    )
  return wiki

current_wiki = LocalProxy(get_wiki)

def get_users():
  users = getattr(g, '_users', None)
  if users is None:
    users = g._users = UserManager(current_app.config['CONTENT_DIR'])
  return users

current_users = LocalProxy(get_users)

def create_app(ctxMeta):
  app = Flask(__name__)

  app.config['CONTENT_DIR'] = ctxMeta['directory']
  app.config['CONFIG_PATH'] = ctxMeta['configPath']
  app.config['CACHE_PATH']  = ctxMeta['cachePath']
  app.config['TITLE'] = u'wiki'
  try:
    with open(app.config['CONFIG_PATH'], "rb") as tomlFile :
      tomlData = tomllib.load(tomlFile)
      nodeMapping = {}
      if 'nodeMapping' in tomlData : nodeMapping = tomlData['nodeMapping']
      linkMapping = {}
      if 'linkMapping' in tomlData : linkMapping = tomlData['linkMapping']
      with app.app_context() :
        if '_mappings' not in g : g._mappings = {
          'nodes' : nodeMapping,
          'links' : linkMapping
        }
        app.config.from_mapping(tomlData)
  except IOError:
    msg = "You need to provide a TOML configuration file."
    raise WikiError(msg)

  if 'SERVER_NAME' in app.config and app.config['SERVER_NAME'] :
    #print(f"using server name {app.config['SERVER_NAME']}")
    sHost, sPort = app.config['SERVER_NAME'].split(':')
    if sHost : app.config['HOST'] = sHost
    if sPort : app.config['PORT'] = sPort

  if ctxMeta['host'] :
    #print(f"using command line host {ctxMeta['host']}")
    app.config['HOST'] = ctxMeta['host']

  if ctxMeta['port'] :
    #print(f"using command line port {ctxMeta['port']}")
    app.config['PORT'] = ctxMeta['port']

  if 'HOST' not in app.config :
    #print(f"using default host")
    app.config['HOST'] = '127.0.0.1'

  if 'PORT' not in app.config :
    #print(f"using default port")
    app.config['PORT'] = 5000

  if 'SERVER_NAME' not in app.config or app.config['SERVER_NAME'] is None :
    app.config['SERVER_NAME'] = f"{app.config['HOST']}:{app.config['PORT']}"

  loginmanager.init_app(app)

  from mindMapper.web.routes import bp
  app.register_blueprint(bp)

  return app

loginmanager = LoginManager()
loginmanager.login_view = 'mindMapper.user_login'

@loginmanager.user_loader
def load_user(name):
  return current_users.get_user(name)
