# -*- encoding: utf-8 -*-
"""
Copyright (c) 2019 - present AppSeed.us
"""

from flask import render_template, redirect, request, url_for
from flask_login import (
    current_user,
    login_user,
    logout_user
)
from apps import login_manager
from apps.authentication import blueprint
from apps.authentication.forms import LoginForm, CreateAccountForm
from apps.authentication.util import verify_pass, hash_pass
from apps.neomodel.model import User


@blueprint.route('/')
def route_default():
    return redirect(url_for('authentication_blueprint.login'))

# Login & Registration
@blueprint.route('/login', methods=['GET', 'POST'])
def login():
    login_form = LoginForm(request.form)
    if 'login' in request.form:

        # read form data
        username  = request.form['username'] # we can have here username OR email
        password = request.form['password']

        # Locate user
        user1 = User.nodes.get_or_none(username=username)
        user2 = User.nodes.get_or_none(email=username)

        # if user not found
        user = user1 if user1 else user2
        if not user:
            return render_template( 'accounts/login.html',
                                    msg='Unknown User',
                                    form=login_form)

        # check the password
        if verify_pass(password, bytes(user.password.encode("ascii"))):        

            # verify if user is enabled
            if user.enabled:
                login_user(user)
                return redirect(url_for('authentication_blueprint.route_default'))
            else:
                return render_template('accounts/login.html',
                        msg='User is disabled',
                        form=login_form)
    
        # password is not ok
        return render_template('accounts/login.html',
                               msg='Wrong password',
                               form=login_form)

    if not current_user.is_authenticated:
        return render_template('accounts/login.html',
                               form=login_form)
    return redirect(url_for('home_blueprint.index'))


@blueprint.route('/register', methods=['GET', 'POST'])
def register():
    create_account_form = CreateAccountForm(request.form)
    if 'register' in request.form:

        username = request.form['username']
        email = request.form['email']

        # Check username exists
        user = User.nodes.get_or_none(username=username)
        if user:
            return render_template('accounts/register.html',
                                   msg='Username already registered',
                                   success=False,
                                   form=create_account_form)
        
        # Check email exists
        user = User.nodes.get_or_none(email=email)
        if user:
            return render_template('accounts/register.html',
                                   msg='Email already registered',
                                   success=False,
                                   form=create_account_form)

        # else we can create the user
        password = hash_pass(request.form['password'])
        user = User(username=username, email=email, password=password.decode('ascii'), enabled=True).save()

        # Delete user from session
        logout_user()

        return render_template('accounts/register.html',
                               msg='User created successfully.',
                               success=True,
                               form=create_account_form)

    else:
        return render_template('accounts/register.html', form=create_account_form)


@blueprint.route('/logout')
def logout():
    logout_user()
    return redirect(url_for('authentication_blueprint.login')) 

# Errors

@login_manager.unauthorized_handler
def unauthorized_handler():
    return render_template('home/page-403.html'), 403


@blueprint.errorhandler(403)
def access_forbidden(error):
    return render_template('home/page-403.html'), 403


@blueprint.errorhandler(404)
def not_found_error(error):
    return render_template('home/page-404.html'), 404


@blueprint.errorhandler(500)
def internal_error(error):
    return render_template('home/page-500.html'), 500
