from apps.neomodel.model import Experiment, Bioreactor, BioreactorType, Measurement, MeasurementType, TIME_UNITS
from neomodel import db
import pandas as pd
import os


UPLOAD_FOLDER = "uploads"

def process_experiment_files(exp_name, init_time, bioreactor_type, files):
    """
    Function to process the uploaded experiment file (CSV).
    """

    try:
        # check experiment name availability
        exp = Experiment.nodes.get_or_none(name=exp_name)
        if exp:
            return False, "The experiment name already exists"
        
        # check bioreactor type
        if bioreactor_type == "pioreactor": 
            create_pioreactor_experiment(exp_name, init_time, files)

        elif bioreactor_type == "bioflo":
            create_bioflow_experiment(exp_name, init_time, files)

        for file in files:
            os.makedirs(os.path.join(UPLOAD_FOLDER, exp_name), exist_ok=True)
            file.save(os.path.join(UPLOAD_FOLDER, exp_name, file.filename))

        return True, "Experiment imported successfully"
    
    except Exception as e:
        print(f"Error processing file: {e}")
        return False, "Error processing the file. See the logs for additional information."


@db.transaction
def create_pioreactor_experiment(exp_name, init_time, files):

    expected_columns ={"od_reading": 'OD600', "temperature_c": "Temperature"}
    
    # create experiment node
    exp = Experiment(name=exp_name, start_time=init_time).save()

    # get bioreactor type node
    br_type = BioreactorType.nodes.get_or_none(name="Pioreactor")

    if not br_type:
        raise ValueError("Bioreactor type 'Pioreactor' not found in the database. Please create it before importing experiments.")

    measurement_query = """
        MATCH (b:Bioreactor {bio_id: $bio_id})
        MATCH (mt:MeasurementType {name: $m_type})
        UNWIND $rows AS row
        CREATE (m:Measurement {
            time: row.time,
            time_unit: row.time_unit,
            value: row.value,
            value_unit: row.value_unit
        })
        CREATE (m)-[:FROM]->(b)
        CREATE (m)-[:IS_TYPE]->(mt)
    """

    for file in files:
        df = pd.read_csv(file)
        
        # create bioreactor node and connect to experiment and br_type
        br = Bioreactor(name=df['pioreactor_unit'].iloc[0]).save()
        
        exp.bioreactor.connect(br)
        br.type.connect(br_type)

        # create measurement nodes and connect to bioreactor
        for col, measurement_type in expected_columns.items():
            if col in df.columns:
                df_filtered = df[['hours_since_experiment_created', col]].dropna(subset=[col])

                # get measurement type node
                m_type = MeasurementType.nodes.get_or_none(name=measurement_type)
                if not m_type:
                    raise ValueError(f"Measurement type '{measurement_type}' not found in the database. Please create it before importing experiments.")
                
                # create measurement nodes and connect to bioreactor
                rows = []
                for row in df_filtered.itertuples():
                    row_dict = row._asdict()
                    
                    rows.append({
                        "time": row_dict['hours_since_experiment_created'],
                        "time_unit": TIME_UNITS["h"],
                        "value": row_dict[col],
                        "value_unit": "-"
                    })

                    # 5000 items batch size to avoid memory issues
                    if len(rows) >= 5000:
                        db.cypher_query(measurement_query, {"rows": rows, "bio_id": br.bio_id, "m_type": measurement_type})
                        rows = []

                # create remaining measurement nodes
                if rows:
                    db.cypher_query(measurement_query, {"rows": rows, "bio_id": br.bio_id, "m_type": measurement_type})

    return True, "Experiment imported successfully"
               
            
@db.transaction
def create_bioflow_experiment(exp_name, init_time, files):
    
    expected_columns ={"Biomass [g/l]": 'Biomass', "Glucose [g/l]": "Glucose"}
    
    # create experiment node
    exp = Experiment(name=exp_name, start_time=init_time).save()

    # get bioreactor type node
    br_type = BioreactorType.nodes.get_or_none(name="BioFlo")

    if not br_type:
        raise ValueError("Bioreactor type 'BioFlo' not found in the database. Please create it before importing experiments.")

    measurement_query = """
        MATCH (b:Bioreactor {bio_id: $bio_id})
        MATCH (mt:MeasurementType {name: $m_type})
        UNWIND $rows AS row
        CREATE (m:Measurement {
            time: row.time,
            time_unit: row.time_unit,
            value: row.value,
            value_unit: row.value_unit
        })
        CREATE (m)-[:FROM]->(b)
        CREATE (m)-[:IS_TYPE]->(mt)
    """

    for file in files:
        df = pd.read_csv(file)
        
        # create bioreactor node and connect to experiment and br_type
        br = Bioreactor(name='BioFlo01').save()
        
        exp.bioreactor.connect(br)
        br.type.connect(br_type)

        # create measurement nodes and connect to bioreactor
        for col, measurement_type in expected_columns.items():
            if col in df.columns:
                df.rename(columns={col: measurement_type, "Time [h]": "Time"}, inplace=True)

                df_filtered = df[['Time', measurement_type]].dropna(subset=[measurement_type])

                # get measurement type node
                m_type = MeasurementType.nodes.get_or_none(name=measurement_type)
                if not m_type:
                    raise ValueError(f"Measurement type '{measurement_type}' not found in the database. Please create it before importing experiments.")
                
                # create measurement nodes and connect to bioreactor
                rows = []
                for row in df_filtered.itertuples():
                    row_dict = row._asdict()
                    
                    rows.append({
                        "time": row_dict['Time'],
                        "time_unit": TIME_UNITS["h"],
                        "value": row_dict[measurement_type],
                        "value_unit": "g/l"
                    })

                    # 5000 items batch size to avoid memory issues
                    if len(rows) >= 5000:
                        db.cypher_query(measurement_query, {"rows": rows, "bio_id": br.bio_id, "m_type": measurement_type})
                        rows = []

                # create remaining measurement nodes
                if rows:
                    db.cypher_query(measurement_query, {"rows": rows, "bio_id": br.bio_id, "m_type": measurement_type})

    return True, "Experiment imported successfully"