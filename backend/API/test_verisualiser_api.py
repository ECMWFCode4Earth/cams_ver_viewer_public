from fastapi.testclient import TestClient
from VerisualiserAPI import verisualiser_api
from data_models import (ModelPlottingDataRequest, LeadTimeAndBaseHourSelection, FCOBPairProcessingSelection,ModelDatasetSelection,BaseModelDatasetSelection,MonthSelection,
Month,Metadata,ObservationSourceWithoutSite,Parameter,Model,ModelPreProcessingSelection, ModelProcessingSelection, ModelDatasetAvailabilityRequest, WantedModelsSelection,
 Index, SingularAxis, ALL_MODELS_DICTIONARY, ALL_OBSERVATION_SOURCES_WITHOUT_SITE_LIST_DICTIONARY, ComparativeAxis, ModelAvailableDatesAndSitesRequest, DateAndSiteSelection, ConsistentDimensionSelection, ConsistentDimension )

from fastapi.encoders import jsonable_encoder

import httpx, datetime
#httpx needs to be installed to use this test functionality,
# to enable automatic creation of requirements.txt, it is imported here


# FUNCTIONS

EXAMPLE_MODEL_PLOTTING_DATA_REQUEST_MODEL = ModelPlottingDataRequest(
    space_model_dataset_selection=ModelDatasetSelection(
        base_model_dataset_selection=BaseModelDatasetSelection(
            month_selection=MonthSelection(month_range=(Month(name="202210"),Month(name="202301"))),
            observation_source_without_site_list=ObservationSourceWithoutSite(name="aeronet_1.5_V3", metadata=Metadata(alias_list=None)),
            parameter=Parameter(name="AOD675"),
            space_model_list=[Model(name="oper-21-0000-3",base_name="oper",base_hour_name_list=["0000"],max_lead_hour_int=21,step_hour_int=3,metadata=Metadata(alias_list=None)),
                              Model(name="operfc-21-0000-3",base_name="operfc",base_hour_name_list=["0000"],max_lead_hour_int=21,step_hour_int=3,metadata=Metadata(alias_list=None)),
                              Model(name="0078-21-0000-3",base_name="0078",base_hour_name_list=["0000"],max_lead_hour_int=21,step_hour_int=3,metadata=Metadata(alias_list=None)),
                              Model(name="hylz-21-0000-3",base_name="hylz",base_hour_name_list=["0000"],max_lead_hour_int=21,step_hour_int=3,metadata=Metadata(alias_list=None))]
        ),
        pre_processing_selection=ModelPreProcessingSelection(
            consistent_dimension_selection_list=[ConsistentDimensionSelection(dimension=ConsistentDimension(name='models'),existing_across=0.4)]
        )),
    lead_and_base_time_selection=LeadTimeAndBaseHourSelection(lead_time_range=(10,20)),
    date_and_site_selection =None, #DateAndSiteSelection(date_list=[datetime.date(year=2018,month=6,day=5)],
    #                                                             site_list='all'),
    space_model_processing_selection= 
    
    #uncomment the one you currently want and comment the other for easy switching
    #FCOBPairProcessingSelection(pre_averaging_step=None))
    ModelProcessingSelection(
        pre_averaging_step=None,
        index=Index(name="valid_time"),
        indexed_axis_list=[SingularAxis(name='Sample Size')]),
        wanted_models_selection=WantedModelsSelection(space_model_list=[Model(name="oper-21-0000-3",base_name="oper",base_hour_name_list=["0000"],max_lead_hour_int=21,step_hour_int=3,metadata=Metadata(alias_list=None))]))



EXAMPLE_MODEL_AVAILABLE_DATES_AND_SITES_REQUEST_MODEL = ModelAvailableDatesAndSitesRequest(space_model_dataset_selection=ModelDatasetSelection(
        base_model_dataset_selection=BaseModelDatasetSelection(
            month_selection=MonthSelection(month_range=(Month(name="202210"),Month(name="202301"))),
            observation_source_without_site_list=ObservationSourceWithoutSite(name="aeronet_1.5_V3", metadata=Metadata(alias_list=None)),
            parameter=Parameter(name="AOD675"),
            space_model_list=[Model(name="oper-21-0000-3",base_name="oper",base_hour_name_list=["0000"],max_lead_hour_int=21,step_hour_int=3,metadata=Metadata(alias_list=None)),
                            Model(name="operfc-21-0000-3",base_name="operfc",base_hour_name_list=["0000"],max_lead_hour_int=21,step_hour_int=3,metadata=Metadata(alias_list=None)),
                            Model(name="0078-21-0000-3",base_name="0078",base_hour_name_list=["0000"],max_lead_hour_int=21,step_hour_int=3,metadata=Metadata(alias_list=None)),
                            Model(name="hylz-21-0000-3",base_name="hylz",base_hour_name_list=["0000"],max_lead_hour_int=21,step_hour_int=3,metadata=Metadata(alias_list=None))]
        ),
        pre_processing_selection=ModelPreProcessingSelection(
            consistent_dimension_selection_list=[ConsistentDimensionSelection(dimension=ConsistentDimension(name='site_id'), existing_across=0.3)]
        )), lead_and_base_time_selection=LeadTimeAndBaseHourSelection(lead_time_range=(10,20)),
        get_coordinates_for_sites=True)


EXAMPLE_MODEL_MODEL_DATASET_AVAILABILITY_REQUEST_MODEL = ModelDatasetAvailabilityRequest(
    observation_source=None,#ALL_OBSERVATION_SOURCES_WITHOUT_SITE_LIST_DICTIONARY['aeronet_1.5_V3'],
    parameter=Parameter(name='AOD675'),
    space_model_list=None#[ALL_MODELS_DICTIONARY['oper-21-0000-3'],ALL_MODELS_DICTIONARY['0078-21-0000-3']],
)



#BASIC TESTING

client = TestClient(verisualiser_api)

def test_get_starting_data():
    starting_data = client.get("/get-starting-data")
    assert starting_data.status_code == 200

def test_get_schemas():    
    schemas = client.get("/get-JSON-schemas")
    assert schemas.status_code == 200    

def test_get_dereferenced_schemas():    
    dereferenced_schemas = client.get("/get-dereferenced-JSON-schemas")
    assert dereferenced_schemas.status_code == 200    


def format_example_request_model_as_json(example_request_model):
    plotting_data_request_dictionary = example_request_model.model_dump()
    #remove duplicates created from validating the model twice
    if plotting_data_request_dictionary['space_model_dataset_selection']['base_model_dataset_selection']['month_selection']['month_range']:
        del plotting_data_request_dictionary['space_model_dataset_selection']['base_model_dataset_selection']['month_selection']['month_list']
    if plotting_data_request_dictionary['lead_and_base_time_selection']['lead_time_range']:
        del plotting_data_request_dictionary['lead_and_base_time_selection']['individual_lead_time_selection_dict']
    plotting_data_request_json_string = jsonable_encoder(plotting_data_request_dictionary)

    return plotting_data_request_json_string



def format_example_availability_request_model_as_json(example_request_model):
    plotting_data_request_dictionary = example_request_model.model_dump()
    plotting_data_request_json_string = jsonable_encoder(plotting_data_request_dictionary)

    return plotting_data_request_json_string



def test_get_model_plotting_data():
    formatted_request_json = format_example_request_model_as_json(EXAMPLE_MODEL_PLOTTING_DATA_REQUEST_MODEL) 

    model_plotting_data_response = client.post("/get-model-plotting-data",json=formatted_request_json)

    assert model_plotting_data_response.status_code == 200  


def test_get_available_dates_and_sites():
    formatted_request_json = format_example_request_model_as_json(EXAMPLE_MODEL_AVAILABLE_DATES_AND_SITES_REQUEST_MODEL)

    available_dates_and_sites_response = client.post('/get-available-dates-and-sites', json=formatted_request_json)

    assert available_dates_and_sites_response.status_code == 200



def test_get_available_dataset_combination_values():
    formatted_request_json = format_example_availability_request_model_as_json(EXAMPLE_MODEL_MODEL_DATASET_AVAILABILITY_REQUEST_MODEL)

    model_dataset_availability_response = client.post('/get-available-dataset-combination-values', json=formatted_request_json)

    assert model_dataset_availability_response.status_code == 200






import json
def get_example_request_as_json(model):
    return json.dumps(format_example_request_model_as_json(model))
def get_example_availability_request_model_as_json(model):
    return json.dumps(format_example_availability_request_model_as_json(model))


# print(get_example_request_as_json(EXAMPLE_MODEL_AVAILABLE_DATES_AND_SITES_REQUEST_MODEL))
# print(get_example_request_as_json(EXAMPLE_MODEL_PLOTTING_DATA_REQUEST_MODEL))
# print(get_example_availability_request_model_as_json(EXAMPLE_MODEL_MODEL_DATASET_AVAILABILITY_REQUEST_MODEL))