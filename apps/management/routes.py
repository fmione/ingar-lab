# -*- encoding: utf-8 -*-
"""
Copyright (c) 2019 - present AppSeed.us
"""

from apps.management import blueprint
from flask import render_template, request
from flask_login import login_required
from apps.neomodel.model import User, Objective, Strain, ProtocolTask, Device, MeasurementType, BioreactorType, db
from neomodel.integration.pandas import to_dataframe
import numpy as np
import json


@blueprint.route('/users', methods=['GET', 'POST'])
@login_required
def get_users():
    properties = ["username", "email", "enabled"]
    item_list = User.nodes.all()

    if request.method == 'POST': 
        
        print(json.loads(request.form.get("data"))) # o agregar


    return render_template('management/management.html', segment="users", properties=properties, items=item_list)


@blueprint.route('/objectives')
@login_required
def get_objectives():
    properties = ["name", "description"]
    item_list = Objective.nodes.all()
    return render_template('management/management.html', segment="objectives", properties=properties, items=item_list)


@blueprint.route('/strains')
@login_required
def get_strains():
    properties = ["name", "supplier", "acquisition_date", "doi"]
    item_list = Strain.nodes.all()
    return render_template('management/management.html', segment="strains", properties=properties, items=item_list)


@blueprint.route('/devices')
@login_required
def get_devices():
    properties = ["name", "model", "type", "manufacturer", "driver"]
    item_list = Device.nodes.all()
    return render_template('management/management.html', segment="Devices - Sensors", properties=properties, items=item_list)


@blueprint.route('/protocols')
@login_required
def get_protocols():
    properties = ["name", "description", "sop", "steps"]
    item_list = ProtocolTask.nodes.all()
    return render_template('management/management.html', segment="Protocols", properties=properties, items=item_list)


@blueprint.route('/measurement-type')
@login_required
def get_measurement_types():
    properties = ["name"]
    item_list = MeasurementType.nodes.all()
    return render_template('management/management.html', segment="Measurement Types", properties=properties, items=item_list)


@blueprint.route('/bioreactor-type')
@login_required
def get_bioreactor_types():
    properties = ["name", "volume"]
    item_list = BioreactorType.nodes.all()
    return render_template('management/management.html', segment="Bioreactor Types", properties=properties, items=item_list)


@blueprint.route('/calibration')
@login_required
def get_calibrations():
    properties = ["device", "calibration_date", "file_path", "calibrated_by"]
    # item_list = DeviceCalibration.nodes.all()
    return render_template('management/management.html', segment="Calibrations", properties=properties, items={})