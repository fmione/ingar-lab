# # -*- encoding: utf-8 -*-
"""
Copyright (c) 2019 - present AppSeed.us
"""

from flask_wtf import FlaskForm
from flask_wtf.file import FileAllowed, FileRequired
from wtforms import StringField, SubmitField, SelectField, MultipleFileField, DateTimeLocalField
from wtforms.validators import DataRequired


class ImportExperimentForm(FlaskForm):
    
    # exp details
    exp_name = StringField("Experiment name", validators=[DataRequired()])
    init_time = DateTimeLocalField('Init Time', format='%Y-%m-%dT%H:%M', validators=[DataRequired()])
    bioreactor_type = SelectField("Bioreactor type", choices=[("bioflo", "BioFlo"), ("pioreactor", "Pioreactor")], validators=[DataRequired()])
    exp_files = MultipleFileField("Experiment File", validators=[FileRequired(), FileAllowed(['csv'], "Only CSV files are allowed.")])
    
    create = SubmitField('Import')



