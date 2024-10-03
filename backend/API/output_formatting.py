import data_models
import numpy as np
import pandas as pd
from fastapi import HTTPException
import datetime, typing

# dicts are normally formatted at source, so no reformatting required here



def format_to_fcob_data(model_values: np.ndarray, observation_values: np.ndarray):
    return data_models.FCOBData(fcob_data=[data_models.FloatData(data=model_values.tolist()),data_models.FloatData(data=observation_values.tolist())])


def format_to_singular_axis(axis_name):
    return data_models.SingularAxis(name=axis_name)

def format_to_comparative_axis(axis_name):
    return data_models.ComparativeAxis(name=axis_name)

def format_ndarray_to_datetime_list(ndarray: np.ndarray):
     return pd.to_datetime(arg=ndarray).to_pydatetime().tolist()

def format_ndarray_to_timedelta_list(ndarray: np.ndarray):
     return pd.to_timedelta(arg=ndarray).to_pytimedelta().tolist()



def format_to_site_list_with_coordinates_lists(site_name_list:list[str], latitude_float_list:list[float], longitude_float_list:list[float]):
     return data_models.SiteCoordinatesLists(site_name_list=site_name_list,
                                                     latitude_float_list=latitude_float_list,
                                                     longitude_float_list=longitude_float_list)



def format_to_index_data(index: data_models.Index, index_data_values: np.ndarray, observation_source_name: data_models.ENUMS['ObservationSourceName']): # type: ignore
    match index.name.name:
        case 'valid_time':
              return data_models.IndexDataValidTime(index=index, data_type_list=format_ndarray_to_datetime_list(ndarray=index_data_values))
        case 'lead_time':
              return data_models.IndexDataLeadTime(index=index, data_type_list=format_ndarray_to_timedelta_list(ndarray=index_data_values))
        case 'base_day_time':
              return data_models.IndexDataBaseDayTime(index=index, data_type_list=format_ndarray_to_timedelta_list(ndarray=index_data_values))
        case 'base_date':
              return data_models.IndexDataBaseDate(index=index, data_type_list=format_ndarray_to_datetime_list(ndarray=index_data_values))
        case 'site_id':
              site_name_list=index_data_values.tolist()
              latitude_float_list, longitude_float_list = data_models.get_latitude_and_longitude_lists_for_site_list_and_observation_source(site_name_list=site_name_list, observation_source_name=observation_source_name)
              return data_models.IndexDataSiteId(index=index, data_type_list=format_to_site_list_with_coordinates_lists(
                   site_name_list=site_name_list, latitude_float_list=latitude_float_list,longitude_float_list=longitude_float_list))
        case _:
              raise HTTPException(status_code=500, detail="Index name not found while formatting. This should normally not be possible.")



def format_to_axis_data(axis: data_models.SingularAxis | data_models.ComparativeAxis, axis_float_values:np.ndarray):
    return data_models.AxisData(axis=axis, float_list=axis_float_values.astype('f').tolist()) #astype f as these will be checked for floatness


def format_to_plotting_data_per_model(model: data_models.Model, index:data_models.Index, index_data_values:np.ndarray,
                                      axis_data_dict: dict[data_models.ENUMS["SingularAxisName"]|data_models.ENUMS["ComparativeAxisName"], data_models.AxisData],# type: ignore
                                      observation_source_name: data_models.ENUMS['ObservationSourceName']):  # type: ignore
    return data_models.PlottingDataPerModel(model=model, index_data=format_to_index_data(index=index, index_data_values=index_data_values, observation_source_name=observation_source_name), axis_data_dict=axis_data_dict)


def format_to_fcob_pair_response(plotting_data_per_model_dict:dict[data_models.ENUMS["ModelName"], data_models.get_pydantic_type_of_list_of_type_and_exact_length(list[float], 2)]): # type: ignore
    return data_models.FCOBPairResponse(fc_ob_pair_data_per_model=plotting_data_per_model_dict) #raw data


def format_to_observation_data(index_data, float_list):
    pass #return data_models.ObservationData(name='observations', index_data=index_data, float_list=float_list)



def format_to_model_plotting_data_response(plotting_data_per_model_dict:dict[data_models.ENUMS["ModelName"], data_models.PlottingDataPerModel], # type: ignore
                                           plotting_data_for_observations_averaged: data_models.ObservationData): 
    
    return data_models.ModelPlottingDataResponse(plotting_data_per_model_dict=plotting_data_per_model_dict,
                                                 plotting_data_for_observations_averaged=plotting_data_for_observations_averaged)



def format_model_data_to_plotting_response(plotting_data_per_model_dict:dict[data_models.ENUMS["ModelName"], data_models.FCOBData|data_models.PlottingDataPerModel], # type: ignore
                            model_processing_selection: data_models.ModelProcessingSelection | data_models.FCOBPairProcessingSelection):
    if type(model_processing_selection) == data_models.ModelProcessingSelection:
        response = format_to_model_plotting_data_response(plotting_data_per_model_dict=plotting_data_per_model_dict, plotting_data_for_observations_averaged=None)#TODO change  # type: ignore
    
    elif type(model_processing_selection) == data_models.FCOBPairProcessingSelection:
        response = format_to_fcob_pair_response(plotting_data_per_model_dict=plotting_data_per_model_dict)
    
    return response



def format_to_dates_and_sites_data_without_coordinates(date_list:list[datetime.date],site_without_coordinates_list:list[data_models.ENUMS["SiteName"]]): # type: ignore
     return data_models.DateAndSiteResponseWithoutCoordinates(date_list=date_list, site_without_coordinates_list=site_without_coordinates_list)

def format_to_dates_and_sites_data_with_coordinates(date_list:list[datetime.date],site_list_with_coordinates_lists:data_models.SiteCoordinatesLists): # type: ignore
     return data_models.DateAndSiteResponseWithCoordinates(date_list=date_list, site_list_with_coordinates_lists=site_list_with_coordinates_lists)



def format_to_available_dates_and_sites_response(date_and_sites:data_models.DateAndSiteResponseWithCoordinates | data_models.DateAndSiteResponseWithoutCoordinates,
                                                 availability_bool_matrix: list[list[bool]],
                                                 order: typing.Literal["sites, dates"]="sites, dates"):
     return data_models.AvailableDatesAndSitesResponse(date_and_sites= date_and_sites,
                                                       availability_bool_matrix=availability_bool_matrix,
                                                       order=order)

def format_available_dates_and_sites_to_response(site_id_name_ndarray: np.ndarray, base_date_ndarray: np.ndarray,
                                                 existance_mask: np.ndarray, observation_source_name: data_models.ENUMS['ObservationSourceName'],   # type: ignore
                                                 get_coordinates_for_sites: bool): 
    site_id_list = site_id_name_ndarray.tolist()
    base_date_list =  format_ndarray_to_datetime_list(ndarray=base_date_ndarray)
    existance_mask_as_list =existance_mask.tolist()

    date_and_sites_without_coordinates = format_to_dates_and_sites_data_without_coordinates(date_list=base_date_list, site_without_coordinates_list=site_id_list)
    
    latitude_float_list, longitude_float_list = data_models.get_latitude_and_longitude_lists_for_site_list_and_observation_source(site_name_list=site_id_list, observation_source_name=observation_source_name)
    site_list_with_coordinates_lists = format_to_site_list_with_coordinates_lists(site_name_list=site_id_list, latitude_float_list= latitude_float_list, longitude_float_list=longitude_float_list)
    date_and_sites_with_coordinates = format_to_dates_and_sites_data_with_coordinates(date_list=base_date_list, site_list_with_coordinates_lists=site_list_with_coordinates_lists)

    if get_coordinates_for_sites:
        date_and_sites_data = date_and_sites_with_coordinates
    elif not get_coordinates_for_sites:
        date_and_sites_data = date_and_sites_without_coordinates
    
    return format_to_available_dates_and_sites_response(date_and_sites=date_and_sites_data, availability_bool_matrix=existance_mask_as_list)




#{"Observation Sources":list(), "Months":list(), "Parameters":list(), "Models":list()} #TODO reformat all this properly
def format_to_model_dataset_availability_response(selectable_dict:dict[str,list[str]], original_model_dataset_availability_request: data_models.ModelDatasetAvailabilityRequest):
    month_list, observation_source_without_site_list, parameter_list, model_list = None,None,None,None
    original_observation_source, original_parameter = original_model_dataset_availability_request.observation_source,   original_model_dataset_availability_request.parameter

    #Usage of (point) is inconsistent. Trying a hotfix for now via replace but an important TODO to standardise.

    if len(selectable_dict['Months'])!= 0: #! Not taken from dict, always available
        month_list = [data_models.Month(name=month_name) for month_name in selectable_dict['Months']]
    else: raise Exception("No matching months found for given request: " + str(original_model_dataset_availability_request))
    

    if len(selectable_dict['Observation Sources'])!= 0: #! taken from dict
        observation_source_without_site_list = [data_models.ALL_OBSERVATION_SOURCES_WITHOUT_SITE_LIST_DICTIONARY[observation_source_name] for observation_source_name in selectable_dict['Observation Sources']]
    elif original_observation_source: observation_source_without_site_list = [original_observation_source]
    else: raise Exception(f"This shouldn't be able to happen.")
    
    if len(selectable_dict['Parameters'])!= 0: #! taken from dict
        parameter_list = [data_models.Parameter(name=parameter_name.replace('.','(point)')) for parameter_name in selectable_dict['Parameters']]
    elif original_parameter: parameter_list= [original_parameter]
    else: raise Exception("This shouldn't be able to happen.")
    
    if len(selectable_dict['Models'])!= 0: #! taken from dict
        model_list = [data_models.ALL_MODELS_DICTIONARY[model_name] for model_name in selectable_dict['Models']]
    #we probably don't need a statement like above here?
    else: raise Exception("This shouldn't be able to happen.")

    return data_models.ModelDatasetAvailabilityResponse(month_list=month_list,
                                                        observation_source_without_site_list=observation_source_without_site_list,
                                                        parameter_list=parameter_list,
                                                        space_model_list=model_list)
     