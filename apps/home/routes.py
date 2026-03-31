# -*- encoding: utf-8 -*-
"""
Copyright (c) 2019 - present AppSeed.us
"""

from apps.home import blueprint
from apps.home.util import process_experiment_files
from flask import render_template, request, flash, redirect, url_for
from flask_login import login_required
from jinja2 import TemplateNotFound
from apps.home.forms import ImportExperimentForm


@blueprint.route('/index')
@login_required
def index():
    return render_template('home/index.html', segment='index')


@blueprint.route('/import', methods=['GET', 'POST'])
@login_required
def import_experiment():
    form = ImportExperimentForm()
    
    if form.validate_on_submit():
        status, message = process_experiment_files(form.exp_name.data, form.init_time.data, form.bioreactor_type.data, form.exp_files.data)

        if status:
            flash(message, "success")
            return redirect(url_for('home_blueprint.import_experiment'))
        else:
            flash(message, "danger")

    elif form.is_submitted():
            errors = []
            for field, errs in form.errors.items():
                label = getattr(form, field).label.text
                errors.extend([f"{label}: {e}" for e in errs])

            if errors:
                flash(" | ".join(errors), "danger")

    return render_template('home/import.html', segment="import", form=form)


# generic route template
@blueprint.route('/<template>')
@login_required
def route_template(template):
    try:
        if not template.endswith('.html'):
            template += '.html'

        # Detect the current page
        segment = get_segment(request)

        # Serve the file (if exists) from app/templates/home/FILE.html
        return render_template("home/" + template, segment=segment)

    except TemplateNotFound:
        return render_template('home/page-404.html'), 404

    except:
        return render_template('home/page-500.html'), 500


# Helper - Extract current page name from request
def get_segment(request):

    try:
        segment = request.path.split('/')[-1]

        if segment == '':
            segment = 'index'

        return segment

    except:
        return None
