import os, ujson, pickle
from typing import Literal
import numpy as np

# DTYPES
TIMES_DTYPE = np.dtype([('base_day_time', 'timedelta64[ns]'), ('base_date', 'datetime64[ns]'), ('lead_time', 'timedelta64[ns]')])
VALID_TIME_WITH_TIMES_DTYPE = np.dtype([('valid_time', 'datetime64[ns]'),('times', TIMES_DTYPE)])



FILE_PATH_TYPES=Literal["model","obs","all"]
def get_all_file_paths_dictionary_in(folder_path: str, file_path_type:FILE_PATH_TYPES = "all"): #file type "model" defined as not obs.nc
    file_path_dictionary = {}
    for observation_source in os.scandir(folder_path):
        if observation_source.is_dir(): #if not logs.txt
            file_path_dictionary[observation_source] = {}  # initialise
            for month in os.scandir(observation_source.path):
                if month.is_dir(): #if not site data.nc
                    file_path_dictionary[observation_source][month] = {}
                    for parameter in os.scandir(month.path):
                        file_path_dictionary[observation_source][month][parameter] = []
                        for file in os.scandir(parameter.path):
                            if file_path_type=="all" or file_path_type=="obs" and file.path[-6:]=="obs.nc" or file_path_type=="model" and not file.path[-6:]=="obs.nc":
                                file_path_dictionary[observation_source][month][parameter].append(
                                    file.path
                                )

    return file_path_dictionary



def get_all_individual_file_paths_in(all_file_paths: dict):
    return [file_path for observation_source in all_file_paths.keys()    
        for month in all_file_paths[observation_source].keys()
            for parameter in all_file_paths[observation_source][month].keys()
                for file_path in all_file_paths[observation_source][month][parameter]
                ]
    



def change_string_to_string_in_elements_of_set(from_string,to_string,set_to_be_changed):
    for name in set_to_be_changed:
        if from_string in name:
            set_to_be_changed.add(name.replace(from_string,to_string))
            set_to_be_changed.remove(name)
    return set_to_be_changed




def save_to_file_as_json(data, saving_location):
    print(f"saving to {saving_location}")
    with open(saving_location, "w") as file:
        ujson.dump(data, file, indent=4)



def save_to_file_as_pickled(data, saving_location):
    print(f"saving to {saving_location}")
    with open(saving_location, "wb") as file:
        pickle.dump(data, file)




def get_data_from_json_file(location: str):
    with open(location, "r") as file:
        data = ujson.load(file)   
    return data



def get_data_from_pickle_file(location: str):
    with open(location, "rb") as file:
        data = pickle.load(file)   
    return data