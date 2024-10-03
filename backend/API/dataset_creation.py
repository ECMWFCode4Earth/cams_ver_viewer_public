import xarray as xr
from fastapi import HTTPException
import numpy as np
import data_models
from verisualiser_settings import FORMATTED_DATA_DIRECTORY_ADDRESS
import os

# IMPORTANT

def reduce_nones_in_ndarray(array: np.ndarray):
    return array[~np.isnan(array)]



def fill_dataarray_with_nas_using_mask(dataarray: xr.DataArray, np_mask: np.ndarray):
    #mask is np array, convert to xarray
    return xr.DataArray(data= np.ma.MaskedArray(data=dataarray.values, mask=np_mask).filled(np.nan)
                        ,coords=dataarray.coords)


def get_np_mask_of_given_dataarray(dataarray: xr.DataArray):
    return np.ma.masked_invalid(dataarray.values).mask


def get_inverse_of_mask(mask: np.ndarray): #not used
    return np.logical_not(mask)


def get_intersection_of_masks(masks_list: list[np.ndarray]):
    return np.logical_and.reduce(masks_list)


def get_union_of_masks(masks_list: list[np.ndarray]):#Only used for lead and base times
    return np.logical_or.reduce(masks_list)


def get_general_names(base_model_dataset_selection:data_models.BaseModelDatasetSelection):
    observation_source_name = base_model_dataset_selection.observation_source_without_site_list.name.name.replace("(point)",".")
    month_name_list = [month.name.name.replace("(point)",".") for month in base_model_dataset_selection.month_selection.month_list] #type: ignore
    parameter_name = base_model_dataset_selection.parameter.name.name.replace("(point)",".")

    return observation_source_name,month_name_list,parameter_name

def get_file_paths_list_of_observation_dataset(base_model_dataset_selection:data_models.BaseModelDatasetSelection):
    observation_source_name,month_name_list,parameter_name = get_general_names(base_model_dataset_selection)
    all_file_paths_for_observations_list=[]
    for month_name in month_name_list:
        all_file_paths_for_observations_list.append(os.path.join(FORMATTED_DATA_DIRECTORY_ADDRESS,observation_source_name,month_name,parameter_name,"obs.nc"))

    return all_file_paths_for_observations_list

#second ".name"s ffor enums
def get_file_paths_dict_of_model_dataset_for_selection_indexed_by_model_names(base_model_dataset_selection:data_models.BaseModelDatasetSelection):
    observation_source_name,month_name_list,parameter_name = get_general_names(base_model_dataset_selection)
    model_name_list = [model.name.name.replace("(point)",".") for model in base_model_dataset_selection.space_model_list]

    all_file_paths_for_model_dict={}
    for model_name in model_name_list:
        for month_name in month_name_list:
            all_file_paths_for_model_dict.setdefault(model_name,list()).append(os.path.join(FORMATTED_DATA_DIRECTORY_ADDRESS,observation_source_name,month_name,parameter_name,model_name+".nc"))

    return all_file_paths_for_model_dict

def open_and_combine_all_model_observation_datasets(base_model_dataset_selection: data_models.BaseModelDatasetSelection):
    all_file_paths_list = get_file_paths_list_of_observation_dataset(base_model_dataset_selection=base_model_dataset_selection)
    combined_dataset = xr.open_mfdataset(all_file_paths_list,engine="h5netcdf",combine="by_coords",
                                                     data_vars=["observation_values"],coords="all", join="outer")
    return combined_dataset


def open_and_combine_all_model_datasets(base_model_dataset_selection: data_models.BaseModelDatasetSelection):
    all_file_paths_dict = get_file_paths_dict_of_model_dataset_for_selection_indexed_by_model_names(base_model_dataset_selection)
    all_datasets_dict = {}
    for model in all_file_paths_dict.keys():
        all_datasets_dict[model] = xr.open_mfdataset(all_file_paths_dict[model],engine="h5netcdf",combine="nested",concat_dim="base_date",
                                                     data_vars=["site_date_availability_mask","model_values"],coords="all", join="outer")
    combined_dataset = xr.concat(
        objs=list(all_datasets_dict.values()),
        dim=xr.Variable(dims="models",data=list(all_datasets_dict.keys())),
        join="outer")
    return combined_dataset



def get_lead_time_and_base_time_mask(inverted_mask_dataarray: xr.DataArray, # type: ignore
                                     individual_lead_time_selection_dict: dict[data_models.ENUMS["ModelName"], data_models.BaseTimesPerModel]): # type: ignore
    individual_mask_combinations_list=[]
    for model in individual_lead_time_selection_dict.keys():
        for base_time in individual_lead_time_selection_dict[model].lead_time_per_base_time_dict.keys():
            lead_time_timedelta_list=[np.timedelta64(lead_time_int,'h') for lead_time_int in individual_lead_time_selection_dict[model].lead_time_per_base_time_dict[base_time].lead_time_int_list]
            base_time_timedelta=np.timedelta64(int(base_time.value),'h')

            wanted_subset_of_file_mask=inverted_mask_dataarray.sel(models=model.value,
                lead_time=lead_time_timedelta_list,base_day_time=base_time_timedelta)
            
            xarray_mask_in_full_shape = wanted_subset_of_file_mask.combine_first(xr.zeros_like(inverted_mask_dataarray,bool)) #Use zeroes like as inverted mask is 1 where available
            np_mask_in_full_shape = xarray_mask_in_full_shape.transpose('models','site_id','base_date','lead_time','base_day_time').values


            individual_mask_combinations_list.append(np_mask_in_full_shape)
    
    #create final mask by or operations (union) on all masks
    final_mask = get_union_of_masks(masks_list=individual_mask_combinations_list)

    return final_mask


def find_indexes_in_tuple(tuple_to_find_indexes_in: tuple, indexes_to_find: tuple):
    found_indexes_list = []

    for index in indexes_to_find:
        found_indexes_list.append(tuple_to_find_indexes_in.index(index))

    return found_indexes_list




def get_consistent_dimensions_masks_list(inverted_mask_dataarray: xr.DataArray,
                                   consistent_dimension_selection_list:list[data_models.ConsistentDimensionSelection]):
    
    consistent_dimension_masks_list = []

    for consistent_dimension_selection in consistent_dimension_selection_list:
        #prepare constants
        selected_dimension_name, existing_across = consistent_dimension_selection.dimension.name.name, consistent_dimension_selection.existing_across
        
        dimensions_list_without_selected_dimension = ['models','site_id','base_date','lead_time','base_day_time']
        dimensions_list_without_selected_dimension.remove(selected_dimension_name)

        #prepare values
        transposing_order_for_selected_consistent_dimension = (selected_dimension_name,*dimensions_list_without_selected_dimension)
        transposing_order_as_axis_numbers = inverted_mask_dataarray.get_axis_num(dim=transposing_order_for_selected_consistent_dimension)
        transposed_inverted_mask_dataarray = inverted_mask_dataarray.transpose(*transposing_order_for_selected_consistent_dimension)
        size_of_selected_dimension = transposed_inverted_mask_dataarray.coords[selected_dimension_name].size #[0,...] indexes just one slice from the first axis
        original_shape = transposed_inverted_mask_dataarray.shape
        tolerance_size = size_of_selected_dimension * existing_across

        reverse_transposing_order=find_indexes_in_tuple(tuple_to_find_indexes_in=transposing_order_as_axis_numbers, indexes_to_find=(0,1,2,3,4))

        #calculate and broadcast mask
        existing_values_summed_over_selected_consistent_dimension = np.sum(transposed_inverted_mask_dataarray.values, axis=0)
        created_inverted_np_mask = np.where(existing_values_summed_over_selected_consistent_dimension   >=  tolerance_size, 1,0)
        broadcast_inverted_np_mask = np.broadcast_to(array=created_inverted_np_mask, shape=original_shape)
        
        reordered_back_np_mask = broadcast_inverted_np_mask.transpose(reverse_transposing_order)
        consistent_dimension_masks_list.append(reordered_back_np_mask)

    return consistent_dimension_masks_list 




# for dimension_coordinates in transposed_inverted_mask_dataarray.coords[consistent_dimension_selection.dimension_name.name]:
def get_all_pre_processing_masks_list(inverted_mask_dataarray: xr.DataArray, # type: ignore
                       consistent_dimension_selection_list:list[data_models.ConsistentDimensionSelection] | None,
                       individual_lead_time_selection_dict: dict[data_models.ENUMS["ModelName"], data_models.BaseTimesPerModel]): # type: ignore
    all_masks_list=[]

    #apply consistent dimensions if requested
    # don't forget to check if consistent_dimension_selection_list exists
    #DON'T FORGET TO TRANSPOSE DATAARRAYS AFTER GETTING THE MASK
    
    if consistent_dimension_selection_list:
        consistent_dimensions_masks_list = get_consistent_dimensions_masks_list(inverted_mask_dataarray=inverted_mask_dataarray,
                                                                    consistent_dimension_selection_list=consistent_dimension_selection_list)
        all_masks_list.extend(consistent_dimensions_masks_list)


    #always apply lead time/base time selection
    lead_time_and_base_time_mask = get_lead_time_and_base_time_mask(
        inverted_mask_dataarray=inverted_mask_dataarray,
        individual_lead_time_selection_dict=individual_lead_time_selection_dict) 
    
    all_masks_list.append(lead_time_and_base_time_mask)
    


    return all_masks_list





#important to apply match models, consistent across (also lead and base times?) (the ones here) first as they may affect date and sites available
def make_model_mask(inverted_mask_dataarray: xr.DataArray,
                    consistent_dimension_selection_list:list[data_models.ConsistentDimensionSelection] | None,
                    individual_lead_time_selection_dict: dict[data_models.ENUMS["ModelName"], data_models.BaseTimesPerModel]): #type: ignore
    

    #get masks for lead and base time as well as match models, consistent across if they apply
    all_masks_list = get_all_pre_processing_masks_list(inverted_mask_dataarray, consistent_dimension_selection_list, individual_lead_time_selection_dict)
    # get intersection of masks from previous step
    intersected_mask = get_intersection_of_masks(masks_list=all_masks_list)
    
    return intersected_mask




def constrain_model_mask_by_dates_and_sites(inverted_mask_dataarray: xr.DataArray, mask:np.ndarray, 
                                 date_and_site_selection: data_models.DateAndSiteSelection|None):
    
    try:
        if date_and_site_selection:
            date_list, site_list= date_and_site_selection.date_list, date_and_site_selection.site_list

            if date_list=='all' and site_list=="all":
                raise HTTPException(status_code=400, detail="This shouldn't have happened. Check the data models.")
                
            elif date_list=='all' and site_list!="all":
                wanted_subset_of_file_mask = inverted_mask_dataarray.sel(site_id=[site.name for site in site_list])
            
            elif date_list!='all' and site_list=="all":
                wanted_subset_of_file_mask = inverted_mask_dataarray.sel(base_date=date_list)

            elif date_list!='all' and site_list!="all":
                wanted_subset_of_file_mask = inverted_mask_dataarray.sel(base_date=date_list,
                                                                         site_id=[site.name for site in site_list])
            
            
            xarray_mask_in_full_shape = wanted_subset_of_file_mask.combine_first(xr.zeros_like(inverted_mask_dataarray,bool)) #Use zeroes like as inverted mask is 1 where available
            np_mask_in_full_shape = xarray_mask_in_full_shape.transpose('models','site_id','base_date','lead_time','base_day_time').values

            mask = get_intersection_of_masks([mask, np_mask_in_full_shape])

        elif not date_and_site_selection:
            mask = mask
            
    except KeyError as error:
        raise HTTPException(status_code=400, detail=f'''The sent sites or dates not found in dataset.
                            Please use the /get-available-dates-and-sites request to check available dates and sites when creating the model plotting request. Error text:{error}''')

    return mask


def get_masked_model_values_dataarray(base_model_dataset_selection: data_models.BaseModelDatasetSelection, pre_processing_selection: data_models.ModelPreProcessingSelection,
                                      date_and_site_selection: data_models.DateAndSiteSelection|None,
                                      individual_lead_time_selection_dict: dict[data_models.ENUMS["ModelName"], data_models.BaseTimesPerModel]): # type: ignore
    
    with open_and_combine_all_model_datasets(base_model_dataset_selection) as combined_dataset:
        with combined_dataset.site_date_availability_mask as combined_site_date_availability_mask:
            #make mask for dataset
            #IMPORTANT: we get the inverse of the mask for the union and intersection functions to work correctly. Normally the mask is true where no values and false where there are values
            #but if we'd like to get the intersection of places where it is available, we need the places where it is available to be true and no values false.

            inverse_mask = get_inverse_of_mask(combined_site_date_availability_mask.values)
            inverted_mask_dataarray = xr.DataArray(data=inverse_mask, coords=combined_site_date_availability_mask.coords)
            pre_processing_mask = make_model_mask(inverted_mask_dataarray=inverted_mask_dataarray,
                                                                consistent_dimension_selection_list=pre_processing_selection.consistent_dimension_selection_list,
                                                                individual_lead_time_selection_dict=individual_lead_time_selection_dict) # type: ignore

            np_mask_fully_constrained_by_dates_and_sites = constrain_model_mask_by_dates_and_sites(inverted_mask_dataarray=inverted_mask_dataarray,
                                                                                                   mask=pre_processing_mask,
                                                                                            date_and_site_selection=date_and_site_selection)
            #invert mask back to use it
            np_mask = get_inverse_of_mask(np_mask_fully_constrained_by_dates_and_sites)
        
        with combined_dataset.model_values as combined_model_values_dataarray:
            masked_model_values_dataarray = fill_dataarray_with_nas_using_mask(dataarray=combined_model_values_dataarray,
                                                                    np_mask=np_mask)
        
    return masked_model_values_dataarray
