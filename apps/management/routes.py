# -*- encoding: utf-8 -*-
"""
Copyright (c) 2019 - present AppSeed.us
"""

from apps.management import blueprint
from flask import render_template, request
from flask_login import login_required
from apps.neomodel.model import User, Objective, Strain, Plasmid, ProtocolTask, Model, Device, db
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


    return render_template('home/management.html', segment="users", properties=properties, items=item_list)

@blueprint.route('/objectives')
@login_required
def get_objectives():
    properties = ["name", "description"]
    item_list = Objective.nodes.all()
    return render_template('home/management.html', segment="objectives", properties=properties, items=item_list)

@blueprint.route('/strains')
@login_required
def get_strains():
    properties = ["name", "supplier", "acquisition_date", "doi"]
    item_list = Strain.nodes.all()
    return render_template('home/management.html', segment="strains", properties=properties, items=item_list)

@blueprint.route('/plasmids')
@login_required
def get_plasmids():
    properties = ["name", "supplier", "acquisition_date", "doi"]
    item_list = Plasmid.nodes.all()
    return render_template('home/management.html', segment="plasmids", properties=properties, items=item_list)

@blueprint.route('/devices')
@login_required
def get_devices():
    properties = ["name", "model", "type", "manufacturer", "driver"]
    item_list = Device.nodes.all()
    return render_template('home/management.html', segment="devices", properties=properties, items=item_list)

@blueprint.route('/protocols')
@login_required
def get_protocols():
    properties = ["name", "description", "doi", "steps"]
    item_list = ProtocolTask.nodes.all()
    return render_template('home/management.html', segment="Protocols", properties=properties, items=item_list)

@blueprint.route('/models')
@login_required
def get_models():
    properties = ["name", "description", "doi"]
    item_list = Model.nodes.all()
    return render_template('home/management.html', segment="Models", properties=properties, items=item_list)

@blueprint.route('/queries', methods=['GET', 'POST'])
@login_required
def get_experiment():
    run_id = request.form.get('InputRunID')

    # if run_id is set, return all experimental data
    if run_id:

        # TODO check exp_id in labels: list()
        exp_id = 19419

        df = to_dataframe(db.cypher_query("""
                    MATCH (exp: Experiment{run_id:$run_id})-->
                            (br:Bioreactor)<--
                            (m:Measurement) 
                                          WHERE br.exp_id IN [19419, 19423, 19427, 19428, 19435, 19436]
                    RETURN br.exp_id AS exp_id, m.type AS type, m.time AS time, m.value AS value
                    ORDER BY m.type, m.time ASC """,
                    {'run_id': int(run_id)}))
        
        df_grouped = df.groupby(['exp_id', 'type'])
        exp_ids = {e_id: True for e_id in df['exp_id'].unique()}
        measurements = df['type'].unique()

        exp = {}
        for measurement in measurements:

            exp[measurement] = {
                "data": {
                    "labels": (df_grouped.get_group((exp_id, measurement))['time'].to_numpy() / 3600).tolist(),
                    "datasets": [
                        {
                            "label": int(exp_id),
                            "data": df_grouped.get_group((exp_id, measurement))['value'].to_list()
                        }
                        for exp_id in exp_ids
                    ]
                },
                "xlabel": "'Time [h]'",
                "ylabel": "'Concentration [g/l]'" if measurement in ['Glucose', 'Acetate'] else ("'Percentage [%]'" if measurement == 'DOT' else "''")
            }
            if measurement == "DOT":
                print((df_grouped.get_group((exp_id, measurement))['time'].to_numpy() / 3600).tolist())

        return render_template('home/queries.html', segment="queries", form=request.form, exp=exp, exp_ids=exp_ids)
    else:
        return render_template('home/queries.html', segment="queries", form=request.form)

