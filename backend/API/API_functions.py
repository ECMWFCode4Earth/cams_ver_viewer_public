import combined_processing
import data_models
import traceback
from fastapi import HTTPException



def get_possible_dataset_combinations(model_dataset_availability_request: data_models.ModelDatasetAvailabilityRequest):
    try:
        response = combined_processing.get_possible_dataset_combinations(model_dataset_availability_request=model_dataset_availability_request)
    
    except Exception as exception:
        print(exception,"\n\n", traceback.format_exc())
        raise HTTPException(status_code=500, detail='Something went wrong with the possible dataset combinations.'+
                            f" It's probably because (one of) the requested combination(s) could not be found. Relevant detail: {exception}")
    
    return response





def get_model_plotting_data(model_plotting_data_request:data_models.ModelPlottingDataRequest):
    try:
        model_plotting_data = combined_processing.get_model_plotting_data(model_plotting_data_request=model_plotting_data_request)
    except Exception as exception:
        print(exception,"\n\n", traceback.format_exc())
        raise HTTPException(status_code=500, detail=f'Something went wrong with the handling of the model plotting request. Relevant detail: {exception}')
    
    return model_plotting_data
    


def get_available_dates_and_sites(available_dates_and_sites_request: data_models.ModelAvailableDatesAndSitesRequest):
    try:
        available_dates_and_sites = combined_processing.get_available_dates_and_sites(available_dates_and_sites_request=available_dates_and_sites_request)

    except Exception as e:
        print(e,"\n\n", traceback.format_exc())

    return available_dates_and_sites
