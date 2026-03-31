from neomodel import db
import pandas as pd


@db.transaction
def get_experiment_info(exp_name):

    query = """
        MATCH (e:Experiment{name: $exp_name})-->(br:Bioreactor)
                    <--(m:Measurement)-->(mt:MeasurementType) 
        RETURN br.name, m.value, m.value_unit, m.time, m.time_unit, mt.name
        ORDER BY m.time ASC
    """

    results, columns = db.cypher_query(query, {"exp_name": exp_name})

    return pd.DataFrame(results, columns=columns)
