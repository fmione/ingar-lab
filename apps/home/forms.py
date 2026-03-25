# # -*- encoding: utf-8 -*-
# """
# Copyright (c) 2019 - present AppSeed.us
# """

from flask_wtf import FlaskForm
from flask_wtf.file import FileField, FileAllowed, FileRequired
from wtforms import StringField, FloatField, IntegerField, SubmitField, FormField, FieldList, SelectField, BooleanField



class ImportExperimentForm(FlaskForm):
    
    # exp details
    exp_name = StringField("Experiment name")
    exp_file = FileField("Experiment File", validators=[FileRequired(), FileAllowed(['csv', 'xls', 'json'])])
    
    create = SubmitField('Import')



