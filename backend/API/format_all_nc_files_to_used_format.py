import xarray
import numpy as np
import os, traceback
import datetime
from general_functions_and_variables import get_all_file_paths_dictionary_in, get_all_individual_file_paths_in
import pandas as pd
import verisualiser_settings




# NOTES
# XARRAY DOES NOT SUPPORT SAVING WITH LOWER THAN NANOPRECISION DATETIMES/TIMEDELTAS
# TODO IT MAY BE A BETTER IDEA TO STORE THE VALID TIMES AND TIME TUPLES PER VALID TIMES IN A SEPARATE FILE AS THEY ARE NOT PARTICULARLY A PART OF THE ACTUAL DATASET AND ARE PROBLEMATIC TO WORK WITH (size unknown)
# THIS MAY SPEED UP THE API A LOT



# TODO CLEAN THIS UP

# CONSTANTS
TO_BE_USED_DATA_LOCATION = os.path.join(verisualiser_settings.UNFORMATTED_DATA_DIRECTORY_ADDRESS,"") #"" for separator
TO_BE_WRITTEN_DATA_LOCATION = os.path.join(verisualiser_settings.FORMATTED_DATA_DIRECTORY_ADDRESS, "")
# dtypes less than ns will are converted to ns when writing to xarray objects anyway!




# FUNCTIONS
def save_dataset_to_path(dataset:xarray.Dataset,path:str,variables_to_compress:list[str]):
    dataset.to_netcdf(
        engine="h5netcdf",
        path=path,
        encoding={variable: {"compression": "gzip","compression_opts": 9} for variable in variables_to_compress},
        mode="w",
    )
                                    
def remove_empty_folders(root):  #https://stackoverflow.com/a/65624165/26489593 

    deleted = set()
    
    for current_dir, subdirs, files in os.walk(root, topdown=False):

        still_has_subdirs = False
        for subdir in subdirs:
            if os.path.join(current_dir, subdir) not in deleted:
                still_has_subdirs = True
                break
    
        if not any(files) and not still_has_subdirs:
            os.rmdir(current_dir)
            deleted.add(current_dir)

    return deleted


def add_mask(dataset): #dataset is assumed to be unstacked
    np_masked_array_object_to_be_masked = np.ma.MaskedArray(data=dataset.model_values.values)
    mask = np.ma.masked_invalid(np_masked_array_object_to_be_masked).mask #full mask
    
    
    dataset_with_mask = dataset.assign(
        {"site_date_availability_mask":xarray.Variable(
            dims=["site_id","base_date","lead_time","base_day_time"],data=mask,encoding={"dtype":bool})})

    return dataset_with_mask


def get_hours_for_day_and_step(day_count: int, step: int):
    hour_list = []
    for day in range(day_count):
        for i in range(int(24 / step)):  # fine because stored in symmetric days
            hour_list.append(day * 24 + step * i)

    return hour_list


def create_new_file_directory(directory: str):
    if not os.path.exists(directory):
        os.makedirs(directory)

def remove_files_in_directory(directory: str):
    for file in os.scandir(directory):
        os.remove(file)

def make_new_file_path(
    file_path: str, max_lead_time: int | None = None, minimum_step: int | None = None
):
    new_file_path_ending = ""
    rest_of_file_path = file_path
    depth = 4
    # os.path.split(path)[0] returns the start, [1] returns the ending

    # change file name !according to the current names by luke (separated by _), in the format model-max_lead_time-possible_base_times-minimum_step
    if (
        max_lead_time and minimum_step
    ):  # if model, [a:b] a inclusive, b exclusive, index starting from 0 and from the start of string

        new_file_path_ending = (  # Get the file name first
            "/" + os.path.split(rest_of_file_path)[1] + new_file_path_ending
        )

        rest_of_file_path = os.path.split(rest_of_file_path)[0]
        new_file_path_ending = (
            new_file_path_ending.split(sep="_")[0]
            + "-"
            + str(max_lead_time)
            + "-"
            + new_file_path_ending.split(sep="_")[1][:-3]
            + "-"
            + str(minimum_step)
            + new_file_path_ending.split(sep="_")[1][-3:]
        )
        depth = 3

    for i in range(depth):  # go back depth entities (folder or file)
        new_file_path_ending = (
            "/" + os.path.split(rest_of_file_path)[1] + new_file_path_ending
        )
        rest_of_file_path = os.path.split(rest_of_file_path)[0]
    return TO_BE_WRITTEN_DATA_LOCATION + new_file_path_ending


def complete_and_sort_sites_and_add_mask_to_model_datasets():
    all_model_file_paths = get_all_file_paths_dictionary_in(folder_path=TO_BE_WRITTEN_DATA_LOCATION, file_path_type="model")
    for observation_source in all_model_file_paths.keys():

        corresponding_observation_site_dataset = xarray.open_dataset(os.path.join(observation_source,"observation_sites.nc"))
        all_observation_sites_in_observation_source_set = set(corresponding_observation_site_dataset.site_name.values)

        for month in all_model_file_paths[observation_source].keys():
            for parameter in all_model_file_paths[observation_source][month].keys():
                for model_file_path in all_model_file_paths[observation_source][month][parameter]:
                    #load the dataset
                    with xarray.open_dataset(model_file_path, engine="h5netcdf") as model_dataset:
                        #make new site_id index
                        all_observation_sites_in_model_file_set = set(model_dataset.site_id.values)
                        sites_not_in_dataset = list(all_observation_sites_in_observation_source_set - all_observation_sites_in_model_file_set)
                        new_site_index_for_model = np.concatenate((list(all_observation_sites_in_model_file_set),sites_not_in_dataset))
                        model_dataset_with_all_site_ids = model_dataset.reindex({"site_id":new_site_index_for_model})
                        #add mask
                        mask_added_dataset=add_mask(model_dataset_with_all_site_ids)
                        #sort
                        site_id_sorted_dataset = mask_added_dataset.sortby("site_id")
                        #load into memory to save
                        model_dataset_to_save_in_memory = site_id_sorted_dataset.load()
                    #save dataset
                    save_dataset_to_path(dataset=model_dataset_to_save_in_memory,path=model_file_path,variables_to_compress=["model_values","site_date_availability_mask"])
        print(f"Completed and sorted sites of and added mask to all datasets for models of {observation_source.path}")
    

    #complete observation source sites
    all_observation_source_file_paths = get_all_file_paths_dictionary_in(folder_path=TO_BE_WRITTEN_DATA_LOCATION, file_path_type="obs")
    for observation_source in all_observation_source_file_paths.keys():

        corresponding_observation_site_dataset = xarray.open_dataset(os.path.join(observation_source,"observation_sites.nc"))
        all_observation_sites_in_observation_source_set = set(corresponding_observation_site_dataset.site_name.values)
    
        for month in all_observation_source_file_paths[observation_source].keys():
            for parameter in all_observation_source_file_paths[observation_source][month].keys():
                for obs_file_path in all_observation_source_file_paths[observation_source][month][parameter]:
                    with xarray.open_dataset(obs_file_path, engine="h5netcdf") as observation_dataset:
                            #make new site_id index
                            all_observation_sites_in_observation_file_set = set(observation_dataset.site_id.values)
                            sites_not_in_dataset = list(all_observation_sites_in_observation_source_set - all_observation_sites_in_observation_file_set)
                            new_site_index_for_observation = np.concatenate((list(all_observation_sites_in_observation_file_set),sites_not_in_dataset))
                            observation_dataset_with_all_site_ids = observation_dataset.reindex({"site_id":new_site_index_for_observation})
                            #sort
                            site_id_sorted_dataset = observation_dataset_with_all_site_ids.sortby("site_id")
                            #load into memory to save
                            observation_dataset_to_save_in_memory = site_id_sorted_dataset.load()
                    #save dataset
                    save_dataset_to_path(dataset=observation_dataset_to_save_in_memory,path=obs_file_path,variables_to_compress=["observation_values"])
        print(f"Completed and sorted sites of observations of {observation_source.path}")
                
            

        



def write_file_in_new_format():
    create_new_file_directory(directory=TO_BE_WRITTEN_DATA_LOCATION)
    log_file = open(TO_BE_WRITTEN_DATA_LOCATION + "logs.txt", "a")
    all_file_paths = get_all_file_paths_dictionary_in(TO_BE_USED_DATA_LOCATION, file_path_type="all")

    for observation_source in all_file_paths.keys():
        print(f"Now writing the files of observation source {observation_source.name}.")
        site_name_list_for_observation_source=set()
        site_data_list_for_observation_source=[]
        for month in all_file_paths[observation_source].keys():
            for parameter in all_file_paths[observation_source][month].keys():

                dataset_for_locations = xarray.open_dataset(all_file_paths[observation_source][month][parameter][0])  # take the first file
                dataset_for_locations = dataset_for_locations.swap_dims({"site":"site_id"}) # to index dim site we swap its name to the coordinate site_id

                new_location_ids=list(set(dataset_for_locations.site_id.values)-site_name_list_for_observation_source)
                
                site_name_list_for_observation_source.update(new_location_ids) #lists are ordered
                site_data_list_for_observation_source.extend([[str(id),float(dataset_for_locations.site_lat.sel(site_id=id).values),float(dataset_for_locations.site_lon.sel(site_id=id).values)] for id in new_location_ids])

                for file_path in all_file_paths[observation_source][month][parameter]:
                    dataset = xarray.open_dataset(file_path)
                    step = round(
                        24 / (len(dataset.valid_time) / 30)
                    )  # round cuz 31/28 days is also possible

                    site_id = dataset.site_id.values
                    base_date = dataset.valid_time.thin(8).values
                    base_day_time = [datetime.timedelta(hours=0)]
                    valid_time = dataset.valid_time.values

                    if (file_path[len(file_path) - 6 :] == "obs.nc"):  # is observation, ends with obs.nc
                        observations = dataset.value.values
                        try:
                            dataset_data = np.reshape(
                                a=observations,
                                newshape=(len(site_id), len(valid_time)),
                                order="C",
                            )
                            new_dataset = xarray.Dataset(
                                coords={
                                    "site_id": site_id,
                                    "valid_time": valid_time,
                                },  # base time is the outermost  arrays ...
                                data_vars={"observation_values": (("site_id", "valid_time"), dataset_data)}
                            )

                            new_file_path = make_new_file_path(file_path)
                            new_file_dir = os.path.split(new_file_path)[0]
                            create_new_file_directory(new_file_dir)

                            new_dataset.to_netcdf(
                                engine="h5netcdf",
                                path=new_file_path,
                                encoding={
                                    "observation_values": {
                                        "compression": "gzip",
                                        "compression_opts": 9,
                                    }
                                },
                                mode="w",
                            )
                            # print("obs:",file_path)
                        except ValueError:
                            log_file.write(
                                "error, the file path is:" + file_path + "\n"
                            )
                            log_file.write(
                                "the time dimension is"
                                + str(len(dataset.valid_time))
                                + "long\n\n"
                            )

                    else:  # is model
                        lead_time = get_hours_for_day_and_step(
                            day_count=len(dataset.forecast_day), step=step
                        )
                        lead_time_length_per_day=int(len(lead_time)/ len(dataset.forecast_day.values))
                        maximum_lead_time = max(lead_time)
                        try:
                            # file path and file dir creation
                            new_file_path = make_new_file_path(
                                file_path=file_path,
                                max_lead_time=maximum_lead_time,
                                minimum_step=step,
                            )

                            new_file_dir = os.path.split(new_file_path)[0]
                            create_new_file_directory(new_file_dir)

                            # Creating data in new format
                            temp_dataset_list = [] #list for each lead time day
                            for (day) in dataset.forecast_day.values:  # day indexed from 1
                                lead_time_indexes = [lead_time_length_per_day* (day - 1),
                                                     lead_time_length_per_day* day
                                ]
                                temp_lead_time_values = [pd.Timedelta(value=lead_time_int, unit="hour") for lead_time_int in lead_time[
                                    lead_time_indexes[0] : lead_time_indexes[1]
                                ]]

                                daily_data = dataset.value.sel(forecast_day=day).values

                                temp_dataset_data = np.reshape(
                                    a=daily_data,
                                    newshape=(
                                        len(site_id),
                                        len(base_date),
                                        len(temp_lead_time_values),
                                        len(base_day_time),
                                    ),
                                    order="C",
                                )
                                new_temp_dataset = xarray.Dataset(
                                    coords={
                                        "site_id": site_id,
                                        "base_date": base_date,
                                        "lead_time": temp_lead_time_values,
                                        "base_day_time": base_day_time,
                                    },  # base time is the outermost  arrays ...
                                    data_vars={"model_values": (("site_id","base_date","lead_time","base_day_time"), temp_dataset_data)}
                                )
                                temp_dataset_list.append(new_temp_dataset)

                            new_dataset = xarray.concat(
                                objs=temp_dataset_list, dim="lead_time"
                            )

                            
                            
                            #ADD VALID TIMES PER TIME TUPLE
                            valid_times_per_time_tuple_coords = xarray.Coordinates(coords={"valid_times_per_time_tuple":
                                                                                   xarray.Variable(dims=("base_day_time","base_date","lead_time"),
                                                        data=np.reshape(a=[
                                                        base_day_time+base_date+lead_time
                                                        for base_day_time in new_dataset.base_day_time.values
                                                        for base_date in new_dataset.base_date.values
                                                        for lead_time in new_dataset.lead_time.values],newshape=(len(base_day_time),len(base_date),len(lead_time)))
                                                        )
                                                        })
                            
                            new_dataset_with_assigned_valid_time_per_time_tuple_coordinates=new_dataset.assign_coords(valid_times_per_time_tuple_coords)



                            #ADD TIME TUPLES PER VALID TIME
                            # IMPORTANT: TURNED OUT TO BE UNNECESSARY
                            # time_tuples_per_valid_time = list()
                            
                            # for base_day_time in new_dataset_with_assigned_valid_time_per_time_tuple_coordinates.base_day_time.values:
                            #     for base_date in new_dataset_with_assigned_valid_time_per_time_tuple_coordinates.base_date.values:
                            #         for lead_time in new_dataset_with_assigned_valid_time_per_time_tuple_coordinates.lead_time.values:
                            #             current_valid_time=new_dataset_with_assigned_valid_time_per_time_tuple_coordinates.valid_times_per_time_tuple.sel(base_day_time=base_day_time,base_date=base_date,lead_time=lead_time).values
                            #             time_tuples_per_valid_time.append((current_valid_time,(base_day_time,base_date,lead_time)))


                            # np_time_array_of_arrays = np.array((time_tuples_per_valid_time),VALID_TIME_WITH_TIMES_DTYPE)
                            
                            # def test_np_time_array(): #TODO move somewhere else
                            #     valid_time_count_time_dict = {}
                            #     for row in np_time_array_of_arrays:
                            #         valid_time_count_time_dict[row[0]] = valid_time_count_time_dict.setdefault(row[0],0) +1
                            #     print(valid_time_count_time_dict)

                            # valid_time_and_times_list = [[],[]]
                            # for row in np_time_array_of_arrays:
                            #     valid_time_and_times_list[0].append(row[0])
                            #     valid_time_and_times_list[1].append(row[1]) 


                            # for i,times in enumerate(valid_time_and_times_list[1]):
                            #     valid_time_and_times_list[1][i]=times.tobytes()
                            
                            
                            # valid_time_coords= xarray.Coordinates(coords={'valid_time': valid_time_and_times_list[0]})
                        
                            # time_tuples_per_valid_time_coords= xarray.Coordinates(coords={"time_tuples_per_valid_time": ("valid_time", valid_time_and_times_list[1])})
                            
                            
                            # new_dataset_with_assigned_valid_time_coordinates = new_dataset_with_assigned_valid_time_per_time_tuple_coordinates.assign_coords(coords=valid_time_coords)

                            # new_dataset_with_time_tuple_per_valid_time_coordinates = new_dataset_with_assigned_valid_time_coordinates.assign_coords(coords=time_tuples_per_valid_time_coords)



                            #remove duplicates in valid_time
                            # new_dataset_with_duplicates_in_valid_time_removed = new_dataset_with_time_tuple_per_valid_time_coordinates.drop_duplicates(dim="valid_time")


                            try:
                                save_dataset_to_path(dataset=new_dataset_with_assigned_valid_time_per_time_tuple_coordinates,
                                                           path=new_file_path, variables_to_compress=["model_values"])
                                
                            except Exception as e:
                                print(e,"\n", traceback.format_exc())
                        except ValueError as e:  #uncomment below when developing
                            print(e, ", the file path is: " + file_path )#,"\n", traceback.format_exc())
                            log_file.write(
                                str(e) + ", the file path is: " + file_path + "\n"
                            )
                            log_file.write(
                                "the time dimension is"
                                + str(len(dataset.valid_time))
                                + "long\n\n"
                            )
                            remove_files_in_directory(directory=new_file_dir)
                            break #to keep the directory deleted
                        except Exception as e:
                            print(e,"\n", traceback.format_exc())

                        # print("model:",file_path)
        site_dataset_for_observation_source=xarray.Dataset(data_vars={"site_latitude": ("site_name", [data[1] for data in site_data_list_for_observation_source]),"site_longitude": ("site_name", [data[2] for data in site_data_list_for_observation_source])},coords={"site_name":[data[0] for data in site_data_list_for_observation_source]})
        site_dataset_for_observation_source.to_netcdf(
                                engine="h5netcdf",
                                path=os.path.join(TO_BE_WRITTEN_DATA_LOCATION,observation_source.name,"observation_sites.nc"),
                                encoding={
                                    "site_latitude": {
                                        "compression": "gzip",
                                        "compression_opts": 9,
                                    },
                                     "site_longitude": {
                                        "compression": "gzip",
                                        "compression_opts": 9,
                                    }
                                },
                                mode="w",
                            )

    print("these folders have been removed: ", list(remove_empty_folders(TO_BE_WRITTEN_DATA_LOCATION)))
    
    #add missing sites
    complete_and_sort_sites_and_add_mask_to_model_datasets()
    
    log_file.write(
        "----------Finished creating new files.----------\n"
        + str(datetime.datetime.now())
        + "\n\n\n\n"
    )
    log_file.close()
    print("finished")
    return None


write_file_in_new_format()

