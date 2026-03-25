# -*- encoding: utf-8 -*-
"""
Copyright (c) 2019 - present AppSeed.us
"""

from apps.home import blueprint
from flask import render_template, request
from flask_login import login_required
from jinja2 import TemplateNotFound
from apps.home.forms import CreateExpConfigForm
from apps.neomodel.model import User, Objective, Strain, Plasmid, Model, ComputationalMethod
import yaml


yaml_template = {""}

@blueprint.route('/index')
@login_required
def index():
    return render_template('home/index.html', segment='index')


@blueprint.route('/exp_config', methods=['GET', 'POST'])
@login_required
def create_experiment_config():

    form = CreateExpConfigForm(request.form)

    # --- buttons actions
    # add responsible row
    if form.add_responsible.data:
        form.responsibles.append_entry(None)
    # delete responsible row
    form.resp_deleted.data = False
    for idx, resp in enumerate(form.responsibles.entries):
        if resp.resp_delete.data:      
            del form.responsibles.entries[idx]
            form.resp_deleted.data = True

    # add mbr group row
    if form.add_mbr_group.data:
        form.mbr_groups.append_entry(None)
    # delete responsible row
    form.mbr_group_deleted.data = False
    for idx, mbrg in enumerate(form.mbr_groups.entries):
        if mbrg.mbr_group_delete.data:      
            del form.mbr_groups.entries[idx]
            form.mbr_group_deleted.data = True
   

    # --- get data for select inputs
    # set input data for objective
    form.objective.choices = [obj.name for obj in Objective.nodes.all()]

    # set input data for responsibles
    user_list = User.nodes.all()
    for resp in form.responsibles.entries:
        resp.resp_name.choices = [user.username for user in user_list] 
        resp.resp_role.choices = ["laboratory_supervisor", "laboratory_experimentation", "experimental_planner", "computational_algorithms", "workflow_definition"]

    # set input data for strains, objectives, plasmids, comp methods
    strain_list = Strain.nodes.all()
    plasmid_list = Plasmid.nodes.all()
    model_list = Model.nodes.all()
    comp_method_list = ComputationalMethod.nodes.all()
    for mbrg in form.mbr_groups.entries:
        mbrg.comp_method.choices = [comp_method.name for comp_method in comp_method_list] 
        mbrg.strain.choices = [strain.name for strain in strain_list]
        mbrg.plasmid.choices = [plasmid.name for plasmid in plasmid_list]
        mbrg.model.choices = [model.name for model in model_list]   

    if form.validate_on_submit():
        print("estaaaa validadooooooooo")
        # TODO: create yaml y descargar

    return render_template('home/exp_config.html', segment="exp_config", form=form)


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
