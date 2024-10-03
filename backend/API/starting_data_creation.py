import os
import datetime
from general_functions_and_variables import get_all_file_paths_dictionary_in, get_all_individual_file_paths_in, change_string_to_string_in_elements_of_set, save_to_file_as_json
import xarray as xr, pandas
import verisualiser_settings

# OBSERVATION DATA CURRENTLY ASSUMED TO BE NON EXISTANT ON MONTHS WHERE NO MODEL DATA EXISTS.
# Basically, it isn't checked separately if models or observations are available, they're assumed to be the same
# CONSTANTS


ORDER_OF_DATA_FROM_FS = ("observation_sources", "months", "parameters", "model_data")

# FUNCTIONS
def get_formatted_aliases(alias_name_dict):
    formatted_alias_name_dict = {}
    for alias_type_name in alias_name_dict.keys():
        for alias in alias_name_dict[alias_type_name]:
            formatted_alias_name_dict.setdefault(alias_type_name,list()).append(alias.replace(".","(point)"))
    return formatted_alias_name_dict


def add_aliases_and_value_lists(base_data): #also deletes old values

    model_data = base_data["models"]
    observation_source_data=base_data["observation_sources"]

    base_data["name_lists"]={}
    model_name_set = set()
    max_lead_hour_ints_set = set()
    base_hours_set = set()
    step_hour_ints_set = set()
    model_alias_name_set = set()
    observation_source_alias_name_set = set()


    for model in model_data.keys():
        #collect sets of model data (same values removed)
        model_name_set.add(model_data[model]["model_name"])
        max_lead_hour_ints_set.add(model_data[model]["max_lead_hour"])
        base_hours_set.update(model_data[model]["base_hours"])
        step_hour_ints_set.add(model_data[model]["step_hour"])
        #add model aliases (also to name set)
        formatted_model_alias_name_dict = get_formatted_aliases(verisualiser_settings.MODEL_ALIASES)
        if model in formatted_model_alias_name_dict:
            base_data["models"][model]["aliases"] = formatted_model_alias_name_dict[model]
            model_alias_name_set.update(formatted_model_alias_name_dict[model])
        else:
            base_data["models"][model]["aliases"] = None
    
        
    for observation_source in observation_source_data.keys():
        #add observation source aliases (!"."s changed here )(also to name set)
        
        formatted_observation_source_alias_name_dict = get_formatted_aliases(alias_name_dict=verisualiser_settings.OBSERVATION_SOURCE_ALIASES)
        if observation_source in formatted_observation_source_alias_name_dict:
            base_data["observation_sources"][observation_source]["aliases"] = formatted_observation_source_alias_name_dict[observation_source]
            observation_source_alias_name_set.update(formatted_observation_source_alias_name_dict[observation_source])

        else:
            base_data["observation_sources"][observation_source]["aliases"] = None



    base_data["name_lists"]["observation_source_name_list"]=list(set(base_data["observation_sources"]))
    base_data["name_lists"]["model_name_list"] = list(model_name_set)
    base_data["name_lists"]["max_lead_hour_int_list"] = list(max_lead_hour_ints_set)
    base_data["name_lists"]["base_hour_name_list"] = list(base_hours_set)
    base_data["name_lists"]["step_hour_int_list"] = list(step_hour_ints_set)
    base_data["name_lists"]["observation_source_alias_name_list"] = list(observation_source_alias_name_set)
    base_data["name_lists"]["model_alias_name_list"] = list(model_alias_name_set)
    base_data["name_lists"]["index_name_list"] = verisualiser_settings.INDEX_NAMES
    base_data["name_lists"]["month_info"] = {}
    (base_data["name_lists"]["month_info"]["min_month_name"],
    base_data["name_lists"]["month_info"]["max_month_name"],
    base_data["name_lists"]["month_info"]["missing_month_list"]) = find_missing_months(set(base_data["months"]))


    return base_data

def reshape_model_data(base_data):
    model_data = base_data["model_data"]

    base_data["models"] = {
        model: {
            "model_full_name": model,
            "model_name": model.split("-", 4)[0],
            "max_lead_hour": int(model.split("-", 4)[1]),
            "base_hours": model.split("-", 4)[2].split("_"),
            "step_hour": int(model.split("-", 4)[3]),
        }
        for model in list(model_data)
    }

    del base_data["model_data"]

    return base_data

def get_models_without_alias_list(model_list):
    return list(set(model_list) - set(verisualiser_settings.MODEL_ALIASES.keys()))

def add_sites_to_base_data(base_data):
    observation_source_names = change_string_to_string_in_elements_of_set(set_to_be_changed=set(base_data["observation_sources"]),from_string="(point)",to_string=".")
    base_data["observation_sources"]={}

    for observation_source in list(observation_source_names):
        with xr.open_dataset(os.path.join(verisualiser_settings.FORMATTED_DATA_DIRECTORY_ADDRESS,observation_source,"observation_sites.nc")) as observation_source_dataset:
            base_data["observation_sources"][observation_source]={
            "site_data_with_separate_sites": {
                site_name:{
                    "site_latitude":float(observation_source_dataset.site_latitude.sel(site_name=site_name).values),
                    "site_longitude":float(observation_source_dataset.site_longitude.sel(site_name=site_name).values),
                } for site_name in observation_source_dataset.site_name.values
            },
            "site_data_as_lists":{
                "site_names": observation_source_dataset.site_name.values.tolist(),
                "site_latitudes":observation_source_dataset.site_latitude.values.tolist(),
                "site_longitudes":observation_source_dataset.site_longitude.values.tolist()
                                  }
        }

    return base_data


def find_missing_months(month_str_set: set):

    months = [datetime.datetime.strptime(month_str, "%Y%m") for month_str in month_str_set]
    months.sort()

    min_month = months[0]
    max_month = months[-1]

    month_strings_from_min_to_max_set = set(pandas.period_range(start=min_month, end=max_month, freq='M').strftime("%Y%m"))
    missing_month_list = list(month_strings_from_min_to_max_set - month_str_set)


    min_month_str = min_month.strftime("%Y%m")
    max_month_str = max_month.strftime("%Y%m")


    return min_month_str, max_month_str, missing_month_list
    

# MAIN FUNCS
def get_base_data():

    base_data = dict()
    for key in ORDER_OF_DATA_FROM_FS:
        base_data[key] = set()


    all_file_paths=get_all_individual_file_paths_in(get_all_file_paths_dictionary_in(verisualiser_settings.FORMATTED_DATA_DIRECTORY_ADDRESS, file_path_type="model"))
    
    all_data = [
        file_path.removeprefix(os.path.join(verisualiser_settings.FORMATTED_DATA_DIRECTORY_ADDRESS,"")).removesuffix(".nc").split(os.sep) # "" for separator
        for file_path in all_file_paths
    ]
    for list_of_infos_in_file_name in all_data:
        for i, info in enumerate(list_of_infos_in_file_name):
            base_data[ORDER_OF_DATA_FROM_FS[i]].add(info.replace(".","(point)"))


    for key in base_data.keys():  # turn sets to sorted list
        base_data[key] = sorted(list(base_data[key]))


    model_reshaped_base_data=reshape_model_data(base_data)
    site_added_base_data=add_sites_to_base_data(model_reshaped_base_data)
    aliases_and_value_lists_added_base_data = add_aliases_and_value_lists(site_added_base_data)
    

    return aliases_and_value_lists_added_base_data



def add_extra_data(base_data):

    extra_data_added = {}

    extra_data_added["base_data"] = base_data
    extra_data_added["manually_added"] = verisualiser_settings.MANUALLY_ADDED_DATA

    return extra_data_added



def make_and_save_starting_data(saving_location):
    base_data = get_base_data()
    extra_data_added_data = add_extra_data(base_data=base_data)
    save_to_file_as_json(data=extra_data_added_data, saving_location=saving_location)




make_and_save_starting_data(saving_location=verisualiser_settings.STARTING_DATA_JSON_LOCATION)