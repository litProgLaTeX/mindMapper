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
        wiki = g._wiki = Wiki(current_app.config['CONTENT_DIR'])
    return wiki


current_wiki = LocalProxy(get_wiki)


def get_users():
    users = getattr(g, '_users', None)
    if users is None:
        users = g._users = UserManager(current_app.config['CONTENT_DIR'])
    return users


current_users = LocalProxy(get_users)


def create_app(directory, configPath):
    app = Flask(__name__)
    app.config['CONTENT_DIR'] = directory
    app.config['CONFIG_PATH'] = configPath
    app.config['TITLE'] = u'wiki'
    try:
        with open(configPath, "rb") as tomlFile :
            tomlData = tomllib.load(tomlFile)
            app.config.from_mapping(tomlData)
    except IOError:
        msg = "You need to provide a TOML configuration file."
        raise WikiError(msg)

    loginmanager.init_app(app)

    from mindMapper.web.routes import bp
    app.register_blueprint(bp)

    return app


loginmanager = LoginManager()
loginmanager.login_view = 'mindMapper.user_login'


@loginmanager.user_loader
def load_user(name):
    return current_users.get_user(name)
