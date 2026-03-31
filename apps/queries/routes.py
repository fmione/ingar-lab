# -*- encoding: utf-8 -*-
"""
Copyright (c) 2019 - present AppSeed.us
"""

from time import sleep

from apps.queries import blueprint

from flask import render_template, request, flash, redirect, url_for
from flask_login import login_required
from jinja2 import TemplateNotFound
from apps.neomodel.model import Experiment
from apps.queries.forms import PlotExperimentForm
from apps.queries.util import get_experiment_info
from plotly.utils import PlotlyJSONEncoder
import plotly.express as px
import json


@blueprint.route('/plots', methods=['GET', 'POST'])
@login_required
def plots():

    form = PlotExperimentForm()

    graphJSON = []
    titles = []

    # get experiments to fill the select input
    experiments = Experiment.nodes.all()
    form.experiment_select.choices = [('', '')] + [(e.name, e.name) for e in experiments]

    # case experiment selected (POST)
    if form.validate_on_submit():
        graphs = []
        titles = []

        try:

            exp_info = get_experiment_info(form.experiment_select.data)

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

                graphs.append(fig)
                titles.append(m_type)

            graphJSON = json.dumps(graphs, cls=PlotlyJSONEncoder)
        
        except Exception as e:
            print(f"Error processing graph: {e}")
            flash("Error loading experiment data", "danger")


    return render_template('queries/plots.html', segment='plots', form=form, graphJSON=graphJSON, titles=titles)


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
