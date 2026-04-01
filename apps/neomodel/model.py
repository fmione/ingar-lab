import os
from neomodel import config, StructuredNode, StructuredRel, FloatProperty, DateTimeProperty, StringProperty, IntegerProperty, JSONProperty, BooleanProperty, RelationshipTo
from neomodel.sync_.cardinality import One, OneOrMore, ZeroOrOne, ZeroOrMore
from neomodel import db
from uuid import uuid4
from apps import login_manager
from flask_login import UserMixin


host = os.environ.get("NEO4J_HOST")
port = os.environ.get("NEO4J_PORT")
user = os.environ.get("NEO4J_USER")
password = os.environ.get("NEO4J_PASSWORD")

config.DATABASE_URL = f'bolt://{user}:{password}@{host}:{port}'
config.AUTO_INSTALL_LABELS = True

# login manager from Flask session
@login_manager.user_loader
def user_loader(id):
    user = User.nodes.get_or_none(user_id=id)
    return user if user else None

@login_manager.request_loader
def request_loader(request):
    username = request.form.get('username')
    user = User.nodes.get_or_none(username=username)
    return user if user else None

class Person(StructuredNode):
    user_id = StringProperty(unique_index=True, default=uuid4)
    username = StringProperty(unique_index=True)
    enabled = BooleanProperty()
    password = StringProperty()
    email = StringProperty(unique_index=True)


# Flask user definition (UserMixin) for session management, with Person properties
class User(Person, UserMixin):
    # override get_id method to return user_id from neomodel 
    # because is not allowed to use id property in neomodel definition
    def get_id(self):
        try:
            return str(self.user_id)
        except AttributeError:
            raise NotImplementedError("No `id` attribute - override `get_id`") from None
        


# -- enums
TIME_UNITS = {"h": "h", "m": "m", "s": "s"}
MEASUREMENT_TYPES = {"DOT": "DOT", "OD600": "OD600", "Biomass": "Biomass", "Acetate": "Acetate", "Glucose": "Glucose", "Volume": "Volume", "Fluo_RFP": "Fluo_RFP"}
WORKFLOW_NODE_STATUS = {"success": "success", "failed": "failed", "running": "running", "skipped": "skipped"}
WORKFLOW_NODE_TRIGGER_RULES = {"all_success": "all_success", "one_success": "one_success", "all_failed": "all_failed", "one_failed": "one_failed", 
                               "none_failed": "none_failed", "all_done": "all_done", "all_skipped": "all_skipped", "none_skipped": "none_skipped"}

# -- relationships with properties


# -- nodes
class Experiment(StructuredNode):
    name = StringProperty(unique_index=True, required=True)   
    description = StringProperty()   
    start_time = DateTimeProperty(required=True)

    objective = RelationshipTo('Objective', 'DESIGNED_FOR', cardinality=ZeroOrOne)
    feeding_config = RelationshipTo('FeedingConfig', 'HAS', cardinality=ZeroOrOne)
    bioreactor = RelationshipTo('Bioreactor', 'INCLUDES', cardinality=OneOrMore)
    workflow_node = RelationshipTo('WorkflowNode', 'HAS_COMPUTATIONAL_WORKFLOW', cardinality=ZeroOrOne)

class Objective(StructuredNode):
    name = StringProperty(unique_index=True, required=True)
    description = StringProperty(required=True)

class FeedingConfig(StructuredNode):
    glc_feed_concentration = FloatProperty()
    glc_feed_concentration_unit = StringProperty()

class Bioreactor(StructuredNode):
    bio_id = StringProperty(unique_index=True, default=lambda: str(uuid4()))
    name = StringProperty(required=True)
    
    type = RelationshipTo('BioreactorType', 'INSTANCE_OF', cardinality=One)
    strain = RelationshipTo('Strain', 'USES', cardinality=ZeroOrOne)

class BioreactorType(StructuredNode):
    name = StringProperty(unique_index=True, required=True)   
    volume = FloatProperty()
    volume_unit = StringProperty()

class Strain(StructuredNode):
    name = StringProperty(unique_index=True, required=True)
    supplier = StringProperty()
    acquisition_date =DateTimeProperty()
    doi = StringProperty()

class WorkflowNode(StructuredNode):
    task_id = StringProperty(required=True)
    trigger_rule = StringProperty(choices=WORKFLOW_NODE_TRIGGER_RULES, required=True)
    status = StringProperty(choices=WORKFLOW_NODE_STATUS, required=True)
    init_time = DateTimeProperty(required=True)
    end_time = DateTimeProperty(default=None)

    workflow_node = RelationshipTo('WorkflowNode', 'DEPENDENCY', cardinality=ZeroOrMore)
    computational_method = RelationshipTo('ComputationalMethod', 'EXECUTES', cardinality=ZeroOrOne)
    computational_environment = RelationshipTo('ComputationalEnvironment', 'EXECUTED_IN', cardinality=ZeroOrOne)
    feeding_setpoint = RelationshipTo('FeedingSetpoint', 'CALCULATES', cardinality=ZeroOrMore)
    measurement = RelationshipTo('Measurement', 'GETS', cardinality=ZeroOrMore)
    model_state = RelationshipTo('ModelState', 'PREDICTS', cardinality=ZeroOrMore)
    model_parameter = RelationshipTo('ModelParameter', 'ESTIMATES', cardinality=ZeroOrMore)

class ComputationalMethod(StructuredNode):
    name = StringProperty(unique_index=True, required=True)
    package = StringProperty()
    language = StringProperty()
    url = StringProperty()

class ComputationalEnvironment(StructuredNode):
    cpu = StringProperty(required=True)
    ram = StringProperty(required=True)
    operating_system = StringProperty(required=True)
    gpu = StringProperty()
    docker_container = BooleanProperty()
    docker_image = StringProperty()
    hpc = BooleanProperty()
    requirements = StringProperty()

class FeedingSetpoint(StructuredNode):
    time = IntegerProperty(required=True)
    time_unit = StringProperty(choices=TIME_UNITS, required=True)
    value = FloatProperty(required=True)
    value_unit = StringProperty(required=True)

    bioreactor = RelationshipTo('Bioreactor', 'FOR', cardinality=One)

class Measurement(StructuredNode):
    time = FloatProperty(required=True)
    time_unit = StringProperty(choices=TIME_UNITS, required=True)
    value = FloatProperty(required=True)
    value_unit = StringProperty(required=True)

    bioreactor = RelationshipTo('Bioreactor', 'FROM', cardinality=One)
    type = RelationshipTo('MeasurementType', 'IS_TYPE', cardinality=One)
    device = RelationshipTo('Device', 'TAKEN_FROM', cardinality=ZeroOrOne)
    protocol = RelationshipTo('ProtocolTask', 'TAKEN_FOLLOWING', cardinality=ZeroOrOne)

class MeasurementType(StructuredNode):
    name = StringProperty(unique_index=True, required=True)

class Device(StructuredNode):
    name = StringProperty(unique_index=True, required=True)
    model = StringProperty(required=True)
    type = StringProperty(required=True)
    manufacturer = StringProperty()
    driver = StringProperty()

class ProtocolTask(StructuredNode):
    name = StringProperty(unique_index=True, required=True)
    description = StringProperty(required=True)
    doi = StringProperty()
    steps = StringProperty()

