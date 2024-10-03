
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse


import data_models
import API_functions

# Currently used packages: "fastapi","xarray[complete]"-->[io] and [parallel] specifically, pandas, numpy, pytest, httpx, jsonref, ujson (just for saving to file in availability_data_creation.py)





# NOTES FOR UPDATES
# o If an endpoint is to be replaced by a more advanced one capable of doing the same work,
# it may be better to keep the deprecated endpoint for legacy applications for some time.
# o Specifying response models in request functions slows down the server a lot for large responses. Be wary.




verisualiser_api = FastAPI()
# REQUESTS
# WITHOUT REQUEST BODY
@verisualiser_api.get("/")
def root():
    return "See /docs for documentation."


@verisualiser_api.get("/get-starting-data", response_model=data_models.StartingDataResponse)
def get_starting_data():
    return data_models.STARTING_DATA_GENERATED_ON_STARTUP


@verisualiser_api.get("/get-JSON-schemas", response_model=dict)
def get_schemas():
    return data_models.MODEL_JSON_SCHEMAS


@verisualiser_api.get("/get-dereferenced-JSON-schemas")
def get_dereferenced_schemas():
    return JSONResponse(content=data_models.DEREFERENCED_MODEL_JSON_SCHEMAS)


# WITH REQUEST BODY
# Model available dataset combinations request
@verisualiser_api.post("/get-available-dataset-combination-values") 
def get_available_dataset_combination_values(model_dataset_availability_request:data_models.ModelDatasetAvailabilityRequest):
    model_dataset_availability_response = API_functions.get_possible_dataset_combinations(model_dataset_availability_request)
    return  data_models.ModelDatasetAvailabilityResponseWithRequest(request=model_dataset_availability_request,response=model_dataset_availability_response)



# TODO Model available dates and sites request 
@verisualiser_api.post("/get-available-dates-and-sites")
def get_available_dates_and_sites(available_dates_and_sites_request:data_models.ModelAvailableDatesAndSitesRequest):
    available_dates_and_sites_response = API_functions.get_available_dates_and_sites(available_dates_and_sites_request=available_dates_and_sites_request)
    return data_models.ModelAvailableDatesAndSitesResponseWithRequest(request=available_dates_and_sites_request,
                                                                      response=available_dates_and_sites_response)


# TODO Model plotting data request
@verisualiser_api.post("/get-model-plotting-data")
def get_model_plotting_data(model_plotting_data_request: data_models.ModelPlottingDataRequest):
    model_plotting_data_response = API_functions.get_model_plotting_data(model_plotting_data_request)
    return data_models.ModelPlottingDataResponseWithRequest(request=model_plotting_data_request,
                                                            response= model_plotting_data_response)




# TESTING VALIDATION
@verisualiser_api.post("/test-model-plotting-data-request", response_model=data_models.ModelPlottingDataRequest)
def test_model_plotting_data_request(model_plotting_data_request: data_models.ModelPlottingDataRequest):
    return model_plotting_data_request



# CORS
origins = [
    "http://127.0.0.1:3000",
    "http://localhost:3000",
    #"http://localhost:443",
]  # 3000: web app, 443 python requests library


verisualiser_api.add_middleware(  # TO BE CONFIGURED - Currently allows everything from the specified "origins"
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)



