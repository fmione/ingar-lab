# # -*- encoding: utf-8 -*-
"""
Copyright (c) 2019 - present AppSeed.us
"""

from flask_wtf import FlaskForm
from flask_wtf.file import FileAllowed, FileRequired
from wtforms import StringField, SubmitField, SelectField, MultipleFileField, DateTimeLocalField
from wtforms.validators import DataRequired


class PlotExperimentForm(FlaskForm):
    experiment_select = SelectField("Experiment name", choices=[], validators=[DataRequired()])

    submit = SubmitField('Submit')

