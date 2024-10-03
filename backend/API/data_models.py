# IMPORTS
import pydantic, typing, enum
import pandas as pd
import xarray as xr
import datetime, ujson, jsonref, traceback

from fastapi import HTTPException

import verisualiser_settings

from general_functions_and_variables import get_data_from_json_file, get_data_from_pickle_file





# NOTES
# • typing.Literal[value] used for static values
# • Only make defaults on the highest order needed
# • Base models are non inheritable, enums support ints or strings

# • Current naming convention:
# ("space_")(descriptive_)type(_"list")
#  where text with () are optional strings, normal text are variables and text with "" is taken literally
 
# normal type names used other than for string which is used as "name"
# the string "list" added to the end if the field is a list
# the string "space" added to the start if there is a namespace conflict in python





# FUNCTIONS




def find_number_of_wanted_base_times(lead_time_range_int: int):#hard coded to be up to 4
    if lead_time_range_int>12: #remember that it cannot be more than 24 as well
        return 1
    elif lead_time_range_int>6:
        return 2
    elif lead_time_range_int>=0:#possible to want one lead time
        return 4

def get_indexed_base_hour_name_list(base_hour_name_list, number_of_wanted_base_times):
    if len(base_hour_name_list) <= number_of_wanted_base_times:
        indexed_base_hour_name_list = base_hour_name_list

    elif len(base_hour_name_list) > number_of_wanted_base_times:
        base_time_index_list = range(0, len(base_hour_name_list), len(base_hour_name_list)/number_of_wanted_base_times)#index out of range
        indexed_base_hour_name_list = [base_hour_name_list[index] for index in base_time_index_list]
    
    return indexed_base_hour_name_list

# RANGES INCLUSIVE ON START, EXCLUSIVE ON END
def find_lead_time_int_list(max_lead_time: int, step_hour_int: int, lead_time_range_list: list, model_name: str):
    all_lead_times=list(range(0,max_lead_time+1,step_hour_int))
    lead_time_int_list = [lead_time for lead_time in all_lead_times if lead_time>=lead_time_range_list[0] and lead_time<lead_time_range_list[1]]
    if len(lead_time_int_list) == 0:
        raise HTTPException(status_code=400, detail=f"""Selected model {model_name} does not have any lead time values between the selected range {lead_time_range_list[0]}-{lead_time_range_list[1]}.\n
                            Model max lead time: {max_lead_time}, model step: {step_hour_int}""")
    else: return lead_time_int_list

def check_fullness_of_lead_time_and_base_hour_selection_or_create_it_from_lead_time_range(lead_and_base_time_selection: typing.ForwardRef('LeadTimeAndBaseHourSelection'), model_list: list[typing.ForwardRef('Model')]): # type: ignore
    if lead_and_base_time_selection.lead_time_range: #only range of lead_and_base_time
        lead_time_range = lead_and_base_time_selection.lead_time_range
        number_of_wanted_base_times = find_number_of_wanted_base_times(lead_time_range_int=lead_time_range[1]-lead_time_range[0])
        #make range into individual_lead_time_selection_dict
        individual_lead_time_selection_dict_from_lead_time_range = {}
        temp_lead_time_per_base_time_dict={}
        for model in model_list:
            indexed_base_hour_name_list = get_indexed_base_hour_name_list(model.base_hour_name_list, number_of_wanted_base_times)
            lead_time_int_list = find_lead_time_int_list(model.max_lead_hour_int.value, model.step_hour_int.value, lead_time_range, model.name.value)
            for base_time in indexed_base_hour_name_list:
                temp_lead_time_per_base_time_dict[base_time.name]=LeadTimesPerBaseTime(lead_time_int_list=lead_time_int_list)
            individual_lead_time_selection_dict_from_lead_time_range[model.name]=BaseTimesPerModel(lead_time_per_base_time_dict=temp_lead_time_per_base_time_dict)
        
        individual_lead_time_selection_dict = individual_lead_time_selection_dict_from_lead_time_range
    
    else: individual_lead_time_selection_dict = lead_and_base_time_selection.individual_lead_time_selection_dict     
    
    #validate individual_lead_time_selection_dict - received as range or not
    model_name_list=[model.name.name for model in model_list]
    model_name_set_from_individual = set([model.name for model in individual_lead_time_selection_dict.keys()])
    #   if there is a model in model_name_set, for which there are no lead/base times in the dict
    if len(set(model_name_list) - model_name_set_from_individual)!=0: 
        raise HTTPException(status_code=400, detail="Not all models have assigned base and lead times.")
    # if there are duplicates
    for model_name in list(set(model_name_list)): #! this modifies model_name_list
        model_name_list.remove(model_name) #removes the first occurence
    if len(model_name_list)!=0:
        raise HTTPException(status_code=400, detail=f"The model(s) {model_name_list} are duplicated as shown here.")
    # #if there is a base time in the dict which doesn't exist in model base times
    for model in model_list:
        base_times_in_dict_not_in_model= set([base_hour_name.name for base_hour_name in individual_lead_time_selection_dict[model.name].lead_time_per_base_time_dict.keys()]) - set(
            [base_hour_name.name for base_hour_name in model.base_hour_name_list])
        if len(base_times_in_dict_not_in_model)!=0:
            raise HTTPException(status_code=400, detail=f"The model {model.name.name} doesn't have the selected base hour(s) {base_times_in_dict_not_in_model}.")
    #   if there are lead times in selection greater than the max lead time of model
        for base_hour_name in model.base_hour_name_list:
            max_lead_time_given =max(list(individual_lead_time_selection_dict[model.name].
                    lead_time_per_base_time_dict[base_hour_name].lead_time_int_list))
            if max_lead_time_given > model.max_lead_hour_int.value:
                raise HTTPException(status_code=400, detail=f"The greatest lead time given {max_lead_time_given} for model {model.name.name} is greater than the max lead time of this model {model.max_lead_hour_int.value}.") 


    # else:
    return individual_lead_time_selection_dict  


def initialise_months(start_month, end_month):
    if start_month == None: 
        start_month_name = list(ENUMS["MinMonthName"])[0].value
    elif type(start_month) == Month:
        start_month_name = start_month.name.value

    if end_month == None:
        end_month_name = list(ENUMS["MaxMonthName"])[0].value
    elif type(end_month) == Month:
        end_month_name = end_month.name.value


    return datetime.datetime.strptime(start_month_name,"%Y%m"), datetime.datetime.strptime(end_month_name,"%Y%m")



def get_latitude_and_longitude_lists_for_site_list_and_observation_source(site_name_list: list, observation_source_name: str):
    related_values = SITE_DATAARRAYS[observation_source_name].sel(site_name=site_name_list)
    return (related_values.site_latitude.values.astype('f').tolist(), related_values.site_longitude.values.astype('f').tolist())



def get_pydantic_type_of_list_of_type_and_exact_length(item_type: type, length: typing.Annotated[int, pydantic.Field(strict=True, gt=0)]):
    return pydantic.conlist(item_type=item_type, min_length=length, max_length=length)


def make_site_enums(observation_source_data_dictionary): #DO NOT LEAVE LOCAL VARIABLES IN THE OPEN
    site_enums=dict()

    
    for observation_source in observation_source_data_dictionary.keys():
        site_name_dictionary = {name: name for name in observation_source_data_dictionary[observation_source]["site_data_as_lists"]["site_names"]}
        site_enums[observation_source]=enum.Enum(observation_source, site_name_dictionary)
    
    
    return site_enums


def make_enums(starting_data_dictionary,model_data,observation_source_data):
    enums=dict()


    singular_axis_name_dictionary = {
        name: name for name in starting_data_dictionary["manually_added"]["axis_based_on_singular_model_or_observation_data_name_list"]
    }
    enums["SingularAxisName"] = enum.Enum("SingularAxisName", singular_axis_name_dictionary)


    comparative_axis_name_dictionary = {
        name: name for name in starting_data_dictionary["manually_added"]["axis_based_on_concurrent_model_and_observation_data_name_list"]
    }
    enums["ComparativeAxisName"] = enum.Enum("ComparativeAxisName", comparative_axis_name_dictionary)


    index_name_dictionary = {
        name: name for name in starting_data_dictionary["base_data"]["name_lists"]["index_name_list"]
    }
    enums["IndexName"] = enum.Enum("IndexName", index_name_dictionary)


    step_hour_int_dictionary = {
        str(integer): integer for integer in starting_data_dictionary["base_data"]["name_lists"]["step_hour_int_list"]
    }
    enums["StepHourInt"] = enum.IntEnum("StepHourInt", step_hour_int_dictionary)


    max_lead_hour_int_dictionary = {
        str(integer): integer for integer in starting_data_dictionary["base_data"]["name_lists"]["max_lead_hour_int_list"]
    }
    enums["MaxLeadHourInt"] = enum.IntEnum("MaxLeadHourInt", max_lead_hour_int_dictionary)


    observation_source_name_dictionary = {
        name: name for name in starting_data_dictionary["base_data"]["name_lists"]["observation_source_name_list"]
    }
    enums["ObservationSourceName"] = enum.Enum("ObservationSourceName", observation_source_name_dictionary)


    observation_source_alias_name_dictionary = {
        name: name for name in starting_data_dictionary["base_data"]["name_lists"]["observation_source_alias_name_list"]
    }
    enums["ObservationSourceAliasName"] = enum.Enum("ObservationSourceAliasName", observation_source_alias_name_dictionary)


    model_alias_name_dictionary = {
        name: name for name in starting_data_dictionary["base_data"]["name_lists"]["model_alias_name_list"]
    }
    enums["ModelAliasName"] = enum.Enum("ModelAliasName", model_alias_name_dictionary)

    
    model_name_dictionary = { #used for checking
        name: name for name in starting_data_dictionary["base_data"]["name_lists"]["model_name_list"]
    }
    enums["ModelBaseName"] = enum.Enum("ModelBaseName", model_name_dictionary)


    model_full_name_dictionary = {
        name: name for name in model_data.keys()
    }
    enums["ModelName"] = enum.Enum("ModelName", model_full_name_dictionary)


    parameter_name_dictionary = {
        name: name for name in starting_data_dictionary["base_data"]["parameters"]
    }
    enums["ParameterName"] = enum.Enum("ParameterName", parameter_name_dictionary)


    month_name_dictionary = {name: name for name in starting_data_dictionary["base_data"]["months"]}
    enums["MonthName"] = enum.Enum("MonthName", month_name_dictionary)


    month_info_dict=starting_data_dictionary["base_data"]["name_lists"]["month_info"]
    min_month_name_dictionary = {month_info_dict["min_month_name"]:month_info_dict["min_month_name"] }
    enums["MinMonthName"] = enum.Enum("MinMonthName", min_month_name_dictionary)

    max_month_name_dictionary = {month_info_dict["max_month_name"]:month_info_dict["max_month_name"] }
    enums["MaxMonthName"] = enum.Enum("MaxMonthName", max_month_name_dictionary)


    base_hour_name_dictionary = {
        name: name for name in starting_data_dictionary["base_data"]["name_lists"]["base_hour_name_list"]
    }
    enums["BaseHourName"] = enum.Enum("BaseHourName", base_hour_name_dictionary)


    enums["SITE_ENUMS"] = make_site_enums(observation_source_data) #keys are actual observation sources
    
    
    enums["SiteName"] = typing.Union[*enums["SITE_ENUMS"].values()]  # type: ignore


    pre_averaging_step_name_dictionary = {name: name for name in starting_data_dictionary["manually_added"]["pre_averaging_step_name_list"]}
    enums["PreAveragingStepName"] = enum.Enum("PreAveragingStepName", pre_averaging_step_name_dictionary)

    
    consistent_dimension_name_dictionary = starting_data_dictionary["manually_added"]["consistent_dimension_name_dict"] #STATIC!
    enums["ConsistentDimensionName"] = enum.Enum("ConsistentDimensionName", consistent_dimension_name_dictionary)


    alias_type_name_dictionary = starting_data_dictionary["manually_added"]["alias_type_name_dict"] #STATIC!
    enums["AliasTypeName"] = enum.Enum("AliasTypeName", alias_type_name_dictionary)


    return enums





# CONSTANTS
#get data
STARTING_DATA_DICTIONARY = get_data_from_json_file(verisualiser_settings.STARTING_DATA_JSON_LOCATION)
AVAILABILITY_DATA_DICTIONARY = get_data_from_pickle_file(verisualiser_settings.AVAILABILITY_PICKLE_LOCATION) # currently using the pickle file

AVAILABILITY_DICT,                                  AVAILABILITY_INFO_ENCODING_DICT,                                 AVAILABILITY_INT_DECODING_DICT = (#Encoding dicts not needed when not using encoded data
AVAILABILITY_DATA_DICTIONARY['availability_dict'],  AVAILABILITY_DATA_DICTIONARY['availability_info_encoding_dict'], AVAILABILITY_DATA_DICTIONARY['availability_int_decoding_dict'])
# {key:{info_type:list[info]}}
# The availability dict only has possible combinations as keys and
# the value dictionary for a key always include the info encoded in the key
# (so if a key is a,b,c; a, b and c all exist as values in the corresponding keys of the value dictionary) 





#get specific parts of data
MODEL_DATA_DICTIONARY = STARTING_DATA_DICTIONARY["base_data"]["models"]
OBSERVATION_SOURCE_DATA=STARTING_DATA_DICTIONARY["base_data"]["observation_sources"]

#make enums, all ending with Name
ENUMS=make_enums(STARTING_DATA_DICTIONARY,MODEL_DATA_DICTIONARY,OBSERVATION_SOURCE_DATA)

LEAD_TIME_RANGE = get_pydantic_type_of_list_of_type_and_exact_length(item_type=typing.Annotated[int, pydantic.Field(strict=True, ge=0)], length=2) # type: ignore



SITE_DATAARRAYS = {observation_source:xr.DataArray(coords=xr.Coordinates(coords={'site_name':OBSERVATION_SOURCE_DATA[observation_source]['site_data_as_lists']['site_names'],
                                                           'site_latitude':('site_name',OBSERVATION_SOURCE_DATA[observation_source]['site_data_as_lists']['site_latitudes']),
                                                           'site_longitude':('site_name',OBSERVATION_SOURCE_DATA[observation_source]['site_data_as_lists']['site_longitudes'])
                                                           })) for observation_source in OBSERVATION_SOURCE_DATA.keys()}








# MODELS
# MODELS USED FOR MODELS IN SELECTIONS (LOWEST ORDER MODELS) (ALSO TEMP)
class BaseTime(pydantic.BaseModel): #TEMP
    name: ENUMS["BaseHourName"] # type: ignore


class LeadTimesPerBaseTime(pydantic.BaseModel): #TEMP
    lead_time_int_list: list[int]


class BaseTimesPerModel(pydantic.BaseModel): #TEMP
    lead_time_per_base_time_dict: dict[ENUMS["BaseHourName"],LeadTimesPerBaseTime] # type: ignore




# MODELS USED FOR SELECTIONS (LOW ORDER MODELS)


class SiteWithCoordinates(pydantic.BaseModel):
    name: ENUMS["SiteName"] # type: ignore
    latitude_float: typing.Annotated[float, pydantic.Field(strict=True, ge=-90, le=90)]
    longitude_float: typing.Annotated[float, pydantic.Field(strict=True, ge=-180, le=180)]


class SiteCoordinatesLists(pydantic.BaseModel):
    site_name_list: list[ENUMS["SiteName"]] # type: ignore
    latitude_float_list: list[typing.Annotated[float, pydantic.Field(strict=True, ge=-90, le=90)]]
    longitude_float_list: list[typing.Annotated[float, pydantic.Field(strict=True, ge=-180, le=180)]]

class Month(pydantic.BaseModel):
    name: ENUMS["MonthName"] # type: ignore 

MONTH_RANGE = get_pydantic_type_of_list_of_type_and_exact_length(item_type=Month| None, length=2)  # type: ignore


class Parameter(pydantic.BaseModel):
    name: ENUMS["ParameterName"] # type: ignore


class Alias(pydantic.BaseModel):
    name: ENUMS["ModelAliasName"] | ENUMS["ObservationSourceAliasName"] # type: ignore
    alias_type: ENUMS["AliasTypeName"] # type: ignore
    def model_post_init(self, __context):
        if self.name not in ENUMS[self.alias_type.value+"Name"]._member_map_.values():
            raise HTTPException(status_code=400, detail=f"Given alias \"{self.name.value}\" does not exist as an alias type \"{self.alias_type.value}\"")         
        


class Metadata(pydantic.BaseModel): 
    alias_list: list[Alias] | None


class ConsistentDimension(pydantic.BaseModel): 
    name: ENUMS["ConsistentDimensionName"] # type: ignore


class ObservationSourceWithSiteList(pydantic.BaseModel): 
    name: ENUMS["ObservationSourceName"] # type: ignore
    site_with_coordinates_list: list[SiteWithCoordinates]
    site_list_with_coordinates_lists: SiteCoordinatesLists
    metadata: Metadata


class ObservationSourceWithoutSite(pydantic.BaseModel):
    name: ENUMS["ObservationSourceName"] # type: ignore
    metadata: Metadata


class Model(pydantic.BaseModel):
    name: ENUMS["ModelName"] # type: ignore
    base_name: ENUMS["ModelBaseName"] # type: ignore
    base_hour_name_list: list[ENUMS["BaseHourName"]] # type: ignore
    max_lead_hour_int: ENUMS["MaxLeadHourInt"]  # type: ignore
    step_hour_int: ENUMS["StepHourInt"] # type: ignore
    metadata: Metadata  

    def model_post_init(self, __context):
        #check if the name matches with parameters
        base_hour_name_list_string = "_".join([base_hour_name.value for base_hour_name in self.base_hour_name_list])
        list_for_name_string=[self.base_name.value, str(self.max_lead_hour_int.value), base_hour_name_list_string, str(self.step_hour_int.value)]
        name_string_from_parameters = "-".join(list_for_name_string)
        if self.name.value!= name_string_from_parameters:
            raise HTTPException(status_code=400, detail=f"Model parameters evaulating to name \"{name_string_from_parameters}\" do not match its name \"{self.name.value}\"")         
            




ALL_MODELS_DICTIONARY = {MODEL_DATA_DICTIONARY[model]["model_full_name"]:
            Model(
                name=MODEL_DATA_DICTIONARY[model]["model_full_name"],
                base_name=MODEL_DATA_DICTIONARY[model]["model_name"],
                base_hour_name_list=[base_hour for base_hour in MODEL_DATA_DICTIONARY[model]["base_hours"]],
                max_lead_hour_int=MODEL_DATA_DICTIONARY[model]["max_lead_hour"],
                step_hour_int=MODEL_DATA_DICTIONARY[model]["step_hour"],
                metadata=Metadata(alias_list=[Alias(name=model_alias_name, alias_type="ModelAlias") for model_alias_name in MODEL_DATA_DICTIONARY[model]["aliases"]]),
            )
            for model in MODEL_DATA_DICTIONARY
        }
ALL_OBSERVATION_SOURCES_WITHOUT_SITE_LIST_DICTIONARY = {observation_source:
            ObservationSourceWithoutSite(
                name=observation_source,
                metadata=Metadata(alias_list=[Alias(name=observation_source_alias_name, alias_type="ObservationSourceAlias"
                                                    ) for observation_source_alias_name in OBSERVATION_SOURCE_DATA[observation_source]["aliases"]]),
            )
            for observation_source in OBSERVATION_SOURCE_DATA.keys()
        }

class SingularAxis(pydantic.BaseModel):
    name: ENUMS["SingularAxisName"] # type: ignore


class ComparativeAxis(pydantic.BaseModel):
    name: ENUMS["ComparativeAxisName"] # type: ignore


class Index(pydantic.BaseModel):
    name: ENUMS["IndexName"] # type: ignore



class ConsistentDimensionSelection(pydantic.BaseModel):
    dimension: ConsistentDimension # type: ignore
    existing_across: typing.Annotated[float, pydantic.Field(strict=True, ge=0, le=1)]





# LOWER SELECTIONS - MODELS USED FOR UPPER SELECTIONS (LOWER MIDDLE ORDER MODELS)
# Incoming
class MonthSelection(pydantic.BaseModel):
    month_range: MONTH_RANGE | None = None# type: ignore IF THE MONTH RANGE IS VALID, THE MONTH LIST IS USED AS IS
    month_list: list[Month] | None = None# As this is a list of month objects, only valid months will be used. (checked)
    #the month list doesn't remain as None. It is initalised with month_range values if None.





class ModelPreProcessingSelection(pydantic.BaseModel):  # none means not selected
    consistent_dimension_selection_list: list[ConsistentDimensionSelection] | None


    #1 in tolerance is interpreted as not enabled
    def model_post_init(self, __context):
        if self.consistent_dimension_selection_list:
            all_requested_consistent_dimension_names = [consistent_dimension_selection.dimension.name.name for consistent_dimension_selection in self.consistent_dimension_selection_list]
            for dimension_name in list(set(all_requested_consistent_dimension_names)):
                    all_requested_consistent_dimension_names.remove(dimension_name)
            if len(all_requested_consistent_dimension_names) != 0:
                raise HTTPException(status_code=400, detail=f'More than one of a dimension selected. Extra selected dimensions: {all_requested_consistent_dimension_names}')
            for i, consistent_dimension_selection in enumerate(self.consistent_dimension_selection_list):
                if consistent_dimension_selection.existing_across == 0:
                        self.consistent_dimension_selection_list.pop(i)
                
            if len(self.consistent_dimension_selection_list) == 0:
                self.consistent_dimension_selection_list=None
    

# UPPER SELECTIONS AND DATA - MODELS USED FOR COMMUNICATON MODELS (UPPER MIDDLE ORDER MODELS)
# Ambiguous
class DateAndSiteSelection(pydantic.BaseModel): #used for requesting specific sites
    date_list: list[datetime.date] | typing.Literal['all']
    site_list: list[ENUMS["SiteName"]] | typing.Literal['all'] # type: ignore
#This is the only unchecked selection which will give errors when not found! Done like this for speed as checking would need redundant steps.


class DateAndSiteResponseWithoutCoordinates(pydantic.BaseModel):# used for giving available sites
    date_list: list[datetime.date] 
    site_without_coordinates_list: list[ENUMS["SiteName"]]  # type: ignore

class DateAndSiteResponseWithCoordinates(pydantic.BaseModel):
    date_list: list[datetime.date]
    site_list_with_coordinates_lists: SiteCoordinatesLists  

class BaseModelDatasetSelection(pydantic.BaseModel):
    month_selection: MonthSelection 
    observation_source_without_site_list: ObservationSourceWithoutSite
    parameter: Parameter
    space_model_list: list[Model] 

    def model_post_init(self, __context):
        self.month_selection = check_and_initalise_month_selection(month_selection=self.month_selection,
                                                                   observation_source=self.observation_source_without_site_list,
                                                                       parameter=self.parameter,
                                                                       space_model_list=self.space_model_list)


# Incoming
class ModelDatasetSelection(pydantic.BaseModel):
    base_model_dataset_selection: BaseModelDatasetSelection
    pre_processing_selection: ModelPreProcessingSelection

class WantedModelsSelection(pydantic.BaseModel):
    space_model_list: list[Model]


class LeadTimeAndBaseHourSelection(pydantic.BaseModel):
    lead_time_range: LEAD_TIME_RANGE | None =None# type: ignore
    individual_lead_time_selection_dict: dict[ENUMS["ModelName"], BaseTimesPerModel] | None =None  # type: ignore
    
    def model_post_init(self, __context):
        if self.lead_time_range and self.individual_lead_time_selection_dict: #both
            raise HTTPException(status_code=400, detail="Both a range and a dictionary is given as lead time/base time selection. Exactly one should be given.")
        elif not self.lead_time_range and not self.individual_lead_time_selection_dict: #none
            raise HTTPException(status_code=400, detail="No range or list is given as lead time/base time selection. Exactly one should be given.")
        if self.lead_time_range:
            if self.lead_time_range[0] > self.lead_time_range[1]: # possible to want one lead time (case ==)
                raise HTTPException(status_code=400, detail="Start lead time in lead time range greater than end lead time.")
            if self.lead_time_range[1] - self.lead_time_range[0] > 24:
                raise HTTPException(status_code=400, detail="Lead time range greater than 24hours. If you want to use a range greater than 24hours, please use the manual lead time selection.")
       
        #additional validation done on ModelPlottingDataRequest, the ones lower on the hierarchy validated first


class ModelProcessingSelection(pydantic.BaseModel):
    pre_averaging_step: typing.Annotated[int, pydantic.Field(ge=0)] | None 
    index: Index  # Data is always indexed by one axis
    indexed_axis_list: list[ComparativeAxis | SingularAxis]
    def model_post_init(self, __context):
        if self.index==Index(name="site_id") or self.pre_averaging_step==0:#pre averaging over sites not allowed,
            #a pre averaging step of 0 is defaulted to None for convenience (step of 1 averages over values on the index)
            self.pre_averaging_step=None


class FCOBPairProcessingSelection(pydantic.BaseModel):
    fcob_pair_processing: typing.Literal[True]



# Outgoing
class DatasetStartingAvailabilityData(pydantic.BaseModel):
    observation_source_dict: dict[ENUMS["ObservationSourceName"],ObservationSourceWithSiteList] # type: ignore
    month_dict: dict[ENUMS["MonthName"], Month] # type: ignore
    parameter_dict: dict[ENUMS["ParameterName"], Parameter]# type: ignore
    space_model_dict: dict[ENUMS["ModelName"], Model] # type: ignore


class ProcessingAvailabilityData(pydantic.BaseModel):
    consistent_dimension_list: list[ConsistentDimension]
    index_list: list[Index]  
    singular_axis_list: list[SingularAxis]
    comparative_axis_list: list[ComparativeAxis] 



class IndexDataValidTime(pydantic.BaseModel):
    index: Index
    data_type_list: list[datetime.datetime] # type: ignore

class IndexDataLeadTime(pydantic.BaseModel):
    index: Index
    data_type_list: list[datetime.timedelta] # type: ignore

class IndexDataBaseDayTime(pydantic.BaseModel):
    index: Index
    data_type_list: list[datetime.time] # type: ignore

class IndexDataBaseDate(pydantic.BaseModel):
    index: Index
    data_type_list: list[datetime.date] # type: ignore

class IndexDataSiteId(pydantic.BaseModel):
    index: Index
    data_type_list: SiteCoordinatesLists

class AxisData(pydantic.BaseModel):
    axis: SingularAxis | ComparativeAxis
    float_list: list[float]


class ObservationData(pydantic.BaseModel):
    name: typing.Literal["observations"]
    index_data: IndexDataBaseDate|IndexDataBaseDayTime|IndexDataLeadTime|IndexDataValidTime|IndexDataSiteId
    axis_data_dict: dict[ENUMS["SingularAxisName"] , AxisData]   # type: ignore


class PlottingDataPerModel(pydantic.BaseModel):
    model: Model
    index_data: IndexDataBaseDate|IndexDataBaseDayTime|IndexDataLeadTime|IndexDataValidTime|IndexDataSiteId
    axis_data_dict: dict[ENUMS["SingularAxisName"]|ENUMS["ComparativeAxisName"], AxisData] # type: ignore



# COMMUNICATION MODELS (HIGH ORDER MODELS)
# Ambiguous



# Incoming
class ModelDatasetAvailabilityRequest(pydantic.BaseModel):
    observation_source: ObservationSourceWithoutSite | None 
    parameter: Parameter | None 
    space_model_list: list[Model] | None

    def model_post_init(self, __context):
        if not self.observation_source and not self.parameter and not self.space_model_list:
            raise HTTPException(status_code=400, detail='No dataset availability request values given. For getting all possible combinations, use the GET request /get-starting-data.')



class ModelAvailableDatesAndSitesRequest(pydantic.BaseModel):
    space_model_dataset_selection: ModelDatasetSelection
    lead_and_base_time_selection: LeadTimeAndBaseHourSelection
    get_coordinates_for_sites: bool
    
    def model_post_init(self, __context):
        self.lead_and_base_time_selection.individual_lead_time_selection_dict = check_fullness_of_lead_time_and_base_hour_selection_or_create_it_from_lead_time_range(
            lead_and_base_time_selection = self.lead_and_base_time_selection, model_list = self.space_model_dataset_selection.base_model_dataset_selection.space_model_list)





class ModelPlottingDataRequest(pydantic.BaseModel): 
    space_model_dataset_selection: ModelDatasetSelection
    lead_and_base_time_selection: LeadTimeAndBaseHourSelection
    date_and_site_selection: DateAndSiteSelection | None  #This the only unchecked selection which will give errors when not found! Done like this for speed as checking would need redundant steps.   
    space_model_processing_selection: ModelProcessingSelection | FCOBPairProcessingSelection
    wanted_models_selection: WantedModelsSelection | None #the selected models from the dataset used if none

    def model_post_init(self, __context):
        self.lead_and_base_time_selection.individual_lead_time_selection_dict = check_fullness_of_lead_time_and_base_hour_selection_or_create_it_from_lead_time_range(
            lead_and_base_time_selection = self.lead_and_base_time_selection, model_list = self.space_model_dataset_selection.base_model_dataset_selection.space_model_list)

        if self.date_and_site_selection:
            if self.date_and_site_selection.date_list =='all' and self.date_and_site_selection.site_list == 'all':
                self.date_and_site_selection = None 
        
        if self.wanted_models_selection:
            selected_models = [model.name.name for model in self.space_model_dataset_selection.base_model_dataset_selection.space_model_list]
            for model in self.wanted_models_selection.space_model_list:
                if model.name.name not in selected_models:
                    raise HTTPException(status_code=400, detail=f'The wanted model {model.name.name} was not found in the selected models {selected_models}.')
        else: self.wanted_models_selection = WantedModelsSelection(space_model_list=self.space_model_dataset_selection.base_model_dataset_selection.space_model_list)

# currently only multiple months or models supported, not multiple observation sources or parameters
    


# Outgoing
class AvailableDatesAndSitesResponse(pydantic.BaseModel):
    date_and_sites: DateAndSiteResponseWithoutCoordinates | DateAndSiteResponseWithCoordinates
    availability_bool_matrix: list[list[bool]]
    order: typing.Literal["sites, dates"]

    
class ModelDatasetAvailabilityResponse(pydantic.BaseModel):

    month_list: list[Month] |None
    observation_source_without_site_list: list[ObservationSourceWithoutSite] 
    parameter_list: list[Parameter]
    space_model_list: list[Model] 
    

class StartingDataResponse(pydantic.BaseModel):
    dataset: DatasetStartingAvailabilityData
    processing: ProcessingAvailabilityData


class ModelPlottingDataResponse(pydantic.BaseModel): #1 index currently allowed
    plotting_data_per_model_dict: dict[ENUMS["ModelName"], PlottingDataPerModel] # type: ignore
    plotting_data_for_observations_averaged: ObservationData | None


class FloatData(pydantic.BaseModel):
    data: list[float]

class FCOBData(pydantic.BaseModel):
    fcob_data: get_pydantic_type_of_list_of_type_and_exact_length(FloatData,2) # type: ignore


class FCOBPairResponse(pydantic.BaseModel):
    fc_ob_pair_data_per_model: dict[ENUMS["ModelName"],FCOBData ] # type: ignore






#COMBINED COMMUNICATION MODELS (HIGHEST ORDER MODELS)
class ModelDatasetAvailabilityResponseWithRequest(pydantic.BaseModel):
    request:ModelDatasetAvailabilityRequest
    response:ModelDatasetAvailabilityResponse


class ModelAvailableDatesAndSitesResponseWithRequest(pydantic.BaseModel):
    request:ModelAvailableDatesAndSitesRequest
    response:AvailableDatesAndSitesResponse



class ModelPlottingDataResponseWithRequest(pydantic.BaseModel):
    request:ModelPlottingDataRequest
    response:ModelPlottingDataResponse|FCOBPairResponse






# CREATE LIST OF MODELS
REQUESTS=[ModelAvailableDatesAndSitesRequest, ModelPlottingDataRequest]
RESPONSES=[StartingDataResponse, ModelAvailableDatesAndSitesResponseWithRequest, ModelPlottingDataResponseWithRequest]
MODEL_JSON_SCHEMAS= {"REQUESTS":[model.model_json_schema() for model in REQUESTS], 
                "RESPONSES":[model.model_json_schema() for model in RESPONSES]}
# CANNOT PARSE MODEL ANOTHER WAY DIRECTLY, ONLY POSSIBLE TO GENERATE JSON SCHEMA


# Still, dereferencing possible through external library
#pprint(json.loads([jsonref.dumps(jsonref.loads(json.dumps(model_schema))) for model_schema in MODEL_JSON_SCHEMAS["REQUESTS"]][0]))
DEREFERENCED_MODEL_JSON_SCHEMAS = {"REQUESTS":[jsonref.replace_refs (model_schema, jsonschema=True, proxies=False) for model_schema in MODEL_JSON_SCHEMAS["REQUESTS"]], 
                 "RESPONSES":[jsonref.replace_refs (model_schema, jsonschema=True, proxies=False) for model_schema in MODEL_JSON_SCHEMAS["RESPONSES"]]}
def delete_defs(schemas):
    for schema_list in schemas.keys():
        for schema in schemas[schema_list]:
            del schema["""$defs"""]
    return schemas
DEREFERENCED_MODEL_JSON_SCHEMAS = delete_defs(DEREFERENCED_MODEL_JSON_SCHEMAS)



# MAKE STARTING DATA INSTANCE (RUNS ON STARTUP)
STARTING_DATA_GENERATED_ON_STARTUP = StartingDataResponse(
    dataset=DatasetStartingAvailabilityData(
        observation_source_dict={observation_source:
            ObservationSourceWithSiteList(name=observation_source,
                            site_with_coordinates_list=[SiteWithCoordinates(name=site_name,latitude_float=OBSERVATION_SOURCE_DATA[observation_source.value]["site_data_with_separate_sites"][site_name.value]["site_latitude"],
                                            longitude_float=OBSERVATION_SOURCE_DATA[observation_source.value]["site_data_with_separate_sites"][site_name.value]["site_longitude"])
                                            for site_name in list(ENUMS["SITE_ENUMS"][observation_source.value])],
                            site_list_with_coordinates_lists=SiteCoordinatesLists(site_name_list=[site.name for site in ENUMS["SITE_ENUMS"][observation_source.value]],
                                                                                          latitude_float_list=get_latitude_and_longitude_lists_for_site_list_and_observation_source(site_name_list=[site.name for site in ENUMS["SITE_ENUMS"][observation_source.value]],observation_source_name=observation_source.name)[0],
                                                                                          longitude_float_list=get_latitude_and_longitude_lists_for_site_list_and_observation_source(site_name_list=[site.name for site in ENUMS["SITE_ENUMS"][observation_source.value]],observation_source_name=observation_source.name)[1]),
                                            metadata=Metadata(alias_list=[Alias(name=observation_source_alias, alias_type="ObservationSourceAlias") for observation_source_alias in OBSERVATION_SOURCE_DATA[observation_source.value]["aliases"]]))
                                                                   #Cant index dictionary with enum, need to use enum.value 
            for observation_source in ENUMS["ObservationSourceName"]
        },
        month_dict={month_name:Month(name=month_name) for month_name in ENUMS["MonthName"]},
        parameter_dict={parameter_name:Parameter(name=parameter_name) for parameter_name in ENUMS["ParameterName"]},
        space_model_dict={model_full_name:ALL_MODELS_DICTIONARY[model_full_name.value] for model_full_name in ENUMS["ModelName"]},
    ),
    processing=ProcessingAvailabilityData(
        consistent_dimension_list=[ConsistentDimension(name=consistent_across_name) for consistent_across_name in ENUMS["ConsistentDimensionName"]],
        index_list=[Index(name=index_name) for index_name in ENUMS["IndexName"]],
        singular_axis_list=[SingularAxis(name=singular_axis_name) for singular_axis_name in ENUMS["SingularAxisName"]],
        comparative_axis_list=[ComparativeAxis(name=comparative_axis_name) for comparative_axis_name in ENUMS["ComparativeAxisName"]]
        )
)

import combined_processing
#currently moved here to avoid circular import error
def check_and_initalise_month_selection(month_selection: MonthSelection, observation_source: ObservationSourceWithoutSite|None, parameter: Parameter|None, space_model_list: list[Model]|None): 
    model_dataset_availability_request  =   ModelDatasetAvailabilityRequest(observation_source=observation_source,parameter=parameter,space_model_list=space_model_list)
    
    try:
        possible_dataset_combinations = combined_processing.get_possible_dataset_combinations(model_dataset_availability_request=model_dataset_availability_request)
    except Exception as exception:
        print(exception,"\n\n", traceback.format_exc())
        raise HTTPException(status_code=500, detail='Something went wrong with the possible dataset combinations.'+
                            f" It's probably because (one of) the requested combination(s) could not be found. Relevant detail: {exception}")
    
    if possible_dataset_combinations.month_list:
        if month_selection.month_range and month_selection.month_list: #both
            raise HTTPException(status_code=400, detail="Both a range and a list is given as month selection. Exactly one should be given.")
        elif not month_selection.month_range and not month_selection.month_list: #none
            raise HTTPException(status_code=400, detail="No range or list is given as month selection. Exactly one should be given.")            
        elif month_selection.month_range: #only range
            start_month,end_month = initialise_months(start_month=month_selection.month_range[0], end_month=month_selection.month_range[1])
            if start_month <= end_month:
                    month_selection.month_list = [Month(name=month_name) for month_name in (
                        set(pd.period_range(start=start_month, end=end_month, freq='M').strftime("%Y%m")) & set([month.name.name for month in possible_dataset_combinations.month_list]))
                        ]
            elif start_month > end_month:
                raise HTTPException(status_code=400, detail="Start month in month range later than end month.")
        elif month_selection.month_list: #only list
            if possible_dataset_combinations.month_list:
                month_selection.month_list = [Month(name=month_name) for month_name in ([month.name.name for month in possible_dataset_combinations.month_list])]
                
    else: raise HTTPException(status_code=400, detail=f'No matching month found from request. Request: {model_dataset_availability_request}')        
    return month_selection