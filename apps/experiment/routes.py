# -*- encoding: utf-8 -*-
"""
Copyright (c) 2019 - present AppSeed.us
"""

from time import sleep

from apps.experiment import blueprint

from flask import render_template, request, flash, redirect, url_for
from flask_login import login_required
from jinja2 import TemplateNotFound
from apps.neomodel.model import Experiment
from apps.experiment.forms import PlotExperimentForm, ImportExperimentForm
from apps.experiment.util import get_experiment_info, process_experiment_files
from plotly.utils import PlotlyJSONEncoder
import plotly.express as px
import json


@blueprint.route('/experiment', methods=['GET', 'POST'])
@login_required
def get_experiments():
    experiments = Experiment.nodes.all()

    data = []
    for e in experiments:

        data.append({
            "name": e.name,
            "description": e.description,   
            "date": e.start_time.strftime("%Y-%m-%d"),
        })

    return render_template('experiment/list.html', segment="experiment", experiments=data)



@blueprint.route('/experiment/info/<exp_name>', methods=['GET'])
@login_required
def experiment_info(exp_name=None):
    if not exp_name:
        return render_template('home/page-404.html'), 404


    graphJSON = []
    titles = []

    # # get experiments to fill the select input
    # experiments = Experiment.nodes.all()
    # form.experiment_select.choices = [('', '')] + [(e.name, e.name) for e in experiments]

    # # case experiment selected (POST)
    # if form.validate_on_submit():
    graphs = []
    titles = []

    try:

        exp_data = Experiment.nodes.get_or_none(name=exp_name)
        exp_info = get_experiment_info(exp_name)

        # create a graph for each measurement type
        for m_type in exp_info["mt.name"].unique().tolist():                        
            fig = px.line(
                exp_info[exp_info["mt.name"] == m_type],
                x="m.time",
                y="m.value",
                color='br.name',
                labels={
                    "m.time": f"<b>Time [{exp_info['m.time_unit'].unique()[0]}]</b>",
                    "m.value": f"<b>{m_type}</b>",
                    "br.name": "<b>Bioreactor</b>"
                }
            )

            # Add chart type options: line - marker (dots)
            fig.update_traces(mode="lines")
            fig.update_layout(
                margin=dict(t=80, l=40, r=20, b=40),
                updatemenus=[
                    dict(
                        type="buttons",
                        direction="left",
                        buttons=[
                            dict(label="Line", method="update",
                                args=[{"mode": ["lines"] * len(fig.data)}]),
                            dict(label="Markers", method="update",
                                args=[{"mode": ["markers"] * len(fig.data)}]),
                            dict(label="Both", method="update",
                                args=[{"mode": ["lines+markers"] * len(fig.data)}]),
                        ],
                        showactive=True,
                        x=0,
                        y=1.15,              # 👈 arriba del plot
                        xanchor="left",
                        yanchor="top"
                    )
                ]
            )

            graphs.append(fig)
            titles.append(m_type)

        graphJSON = json.dumps(graphs, cls=PlotlyJSONEncoder)
    
    except Exception as e:
        print(f"Error processing graph: {e}")
        flash("Error loading experiment data", "danger")


    return render_template('experiment/info.html', segment='experiment', graphJSON=graphJSON, titles=titles, exp_data=exp_data)


@blueprint.route('/experiment/import', methods=['GET', 'POST'])
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

    return render_template('experiment/import.html', segment="import", form=form)


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
        return render_template("experiment/" + template, segment=segment)

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
