import os

# IMPORTANT NOTES
# "."s in observation source names with . in them changed to (point)
# This should generally be done if there are any .s in the names but currently done only for observation sources as aeronet created a problem. CAN BE GENERALISED EASILY USING THE FUNCTI 


# COPY, PASTE AND ADD/EDIT AS NEEDED

API_DIRECTORY = os.path.dirname(__file__)
UNFORMATTED_DATA_DIRECTORY_ADDRESS= os.path.join(API_DIRECTORY,"example_data") #without separator!
FORMATTED_DATA_DIRECTORY_ADDRESS =  os.path.join(API_DIRECTORY,"formatted_example_data")
FORMATTED_DATA_DIRECTORY_ADDRESS_WITH_SEPARATOR = os.path.join(FORMATTED_DATA_DIRECTORY_ADDRESS, '')

ORDER_OF_INFO_TYPES_FROM_FS = ("Observation Sources", "Months", "Parameters", "Models")

STARTING_DATA_JSON_LOCATION=os.path.join(API_DIRECTORY,"starting_data.json")
AVAILABILITY_JSON_LOCATION = os.path.join(API_DIRECTORY,"availability_data.json")
AVAILABILITY_PICKLE_LOCATION = os.path.join(API_DIRECTORY,"availability_data.pickle")


ALIAS_TYPES = {
    "ModelAlias":"ModelAlias",
    "ObservationSourceAlias":"ObservationSourceAlias"
}

INDEX_NAMES = ["valid_time","lead_time","base_day_time","base_date","site_id"]

CONSISTENT_DIMENSION_NAMES = {
    'base_date': 'base_date',
    'site_id' : 'site_id',
    'models':'models',
    'lead_time':'lead_time',
    'base_day_time':'base_day_time'
    }

MODEL_ALIASES = {  # manually defined, more than 1 alias could maybe be used as multi-language support?
    "0078-21-0000-3": ["model of 0078"],
    "hylz-21-0000-3": ["model of hylz"],
    "oper-117-0000-3": ["operational 117h"],
    "oper-21-0000-3": ["operational 21h"],
    "operfc-21-0000-3": ["operational combined (fc)"],
    "model_name": [
        "model_alias_1",
        "model_alias_2",
    ],
}

OBSERVATION_SOURCE_ALIASES = {  # manually defined, more than 1 alias could maybe be used as multi-language support?
    "aeronet_1.5_V3": ["Aeronet 1.5 V3"],
    "airbase_meteofrance": ["Airbase Meteofrance"],
    "airnow": ["Airnow"],
    "china_aq_globvalsvr": ["China Global"],
    "observation_source_name": [
        "observation_source_alias_1",
        "observation_source_alias_2",
    ],
}


#TODO ADD METADATA ON COMPOSITE MODELS (WHEN IS WHICH EXACT MODEL USED)
MANUALLY_ADDED_DATA = {
    "axis_based_on_singular_model_or_observation_data_name_list": ["Sample Size","Mean","Median"],
    "axis_based_on_concurrent_model_and_observation_data_name_list": ["Bias"],
    "alias_type_name_dict":ALIAS_TYPES,
    "consistent_dimension_name_dict":CONSISTENT_DIMENSION_NAMES
}



