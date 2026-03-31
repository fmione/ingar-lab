# -*- encoding: utf-8 -*-
"""
Copyright (c) 2019 - present AppSeed.us
"""

import os

from flask import Flask
from flask_login import LoginManager
from importlib import import_module
from neomodel import install_all_labels


login_manager = LoginManager()

def register_extensions(app):
    login_manager.init_app(app)


def register_blueprints(app):
    for module_name in ('authentication', 'home', 'management', 'queries'):
        module = import_module('apps.{}.routes'.format(module_name))
        app.register_blueprint(module.blueprint)


def create_app(config):
    app = Flask(__name__)
    app.config.from_object(config)
    register_extensions(app)
    register_blueprints(app)
    install_all_labels()
    return app
