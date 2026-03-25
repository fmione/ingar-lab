# # -*- encoding: utf-8 -*-
# """
# Copyright (c) 2019 - present AppSeed.us
# """

from flask_wtf import FlaskForm
from wtforms import StringField, FloatField, IntegerField, SubmitField, FormField, FieldList, SelectField, BooleanField
from wtforms.validators import Optional


TIME_UNITS = [("h", "Hours"), ("m", "Minutes"), ("s", "Seconds")]
VOLUME_UNITS = [("μl", "Microliter"), ("ml", "Milliliter"), ("l", "Liter")]
CONCENTRATION_UNITS = [("gl", "Grams/Liter")]

class ResponsibleForm(FlaskForm):
    resp_name = SelectField('Name')
    resp_role = SelectField('Role')
    resp_delete = SubmitField("Delete")

# class ComputationalMethodForm(FlaskForm):
#     cm_type = StringField("Type")
#     cm_name = StringField("Name")
    
class MBRGroupForm(FlaskForm):
    group_name = StringField("MBR Group Name")
    mbr_exp_ids = StringField('MBR Exp IDs')
    comp_method = SelectField('Comp Method (optional)')
    strain = SelectField('Strain')
    plasmid = SelectField('Plasmid')
    model = SelectField('Model (optional)')
    
    mbr_group_delete = SubmitField("Delete")

class FeedingConfigForm(FlaskForm):
    feeding_start = FloatField("Time Start", validators=[Optional()])
    feeding_start_unit = SelectField("Time Start Unit", choices=TIME_UNITS, validators=[Optional()])
    feeding_stop = FloatField("Time Stop", validators=[Optional()])
    feeding_stop_unit = SelectField("Time Stop Unit", choices=TIME_UNITS, validators=[Optional()])
    feeding_frequency = FloatField("Frequency", validators=[Optional()])
    feeding_frequency_unit = SelectField("Frequency Unit", choices=TIME_UNITS, validators=[Optional()])
    minimal_feed_volume = FloatField("Minimal Volume", validators=[Optional()])
    minimal_feed_volume_unit = SelectField("Minimal Volume Unit", choices=VOLUME_UNITS, validators=[Optional()])
    maximal_feed_volume = FloatField("Maximal Volume", validators=[Optional()])
    maximal_feed_volume_unit = SelectField("Maximal Volume Unit", choices=VOLUME_UNITS, validators=[Optional()])

class InductionConfigForm(FlaskForm):
    induction_start = FloatField("Time Start", validators=[Optional()])
    induction_start_unit = SelectField("Time Start Unit", choices=TIME_UNITS, validators=[Optional()])
    induction_value = FloatField("Concentration Value", validators=[Optional()])
    induction_unit = SelectField("Concentration Unit", choices=CONCENTRATION_UNITS, validators=[Optional()])
    
class CompWorkflowForm(FlaskForm):
    iterations = IntegerField("Iterations number", validators=[Optional()])
    time_bw_samples = IntegerField("Time Between Samples", validators=[Optional()])
    time_first_sample = IntegerField("Time First Sample", validators=[Optional()])
    time_to_process_sample = IntegerField("Time To Process Sample", validators=[Optional()])
    time_start_checking_db = IntegerField("Time Start Checking DB", validators=[Optional()])
    time_bw_check_db = IntegerField("Time Between Check DB", validators=[Optional()])
    time_unit = SelectField("Units for all values", choices=TIME_UNITS, validators=[Optional()])

class CreateExpConfigForm(FlaskForm):
    # exp details
    exp_run_id = IntegerField("Run ID")
    exp_horizon = FloatField("Horizon")
    exp_horizon_unit = SelectField("Horizon Unit", choices=TIME_UNITS)

    # objective
    objective = SelectField("Select Objective")

    # responsibles
    add_responsible = SubmitField("Add Responsible")
    resp_deleted = BooleanField("Resp. deleted", default=False)
    responsibles = FieldList(FormField(ResponsibleForm), min_entries=1)

    # mbr groups
    add_mbr_group = SubmitField("Add MBR Groups")
    mbr_group_deleted = BooleanField("MBR group deleted", default=False)
    mbr_groups = FieldList(FormField(MBRGroupForm), min_entries=1)

    # feeding config
    feeding = FormField(FeedingConfigForm)

    # induction config
    induction = FormField(InductionConfigForm)

    # computational workflow
    comp_workflow = FormField(CompWorkflowForm)

    create = SubmitField('Create')

