import xarray as xr
import numpy as np
import data_models, dataset_creation, output_formatting
from fastapi import HTTPException

# NOTES      
#   the package numba could be used to vectorise complicated processing if required. It is probably easier to use native numpy though. 



def broadcast_dataarray_over_non_found_dimensions(dataarray: xr.DataArray, all_dimension_sizes_dict: dict[str,int] ):
    broadcast_dataarray = dataarray.expand_dims(dim={dimension:all_dimension_sizes_dict[dimension] for dimension in all_dimension_sizes_dict.keys() if dimension not in dataarray.dims})
    return broadcast_dataarray


def get_bias_of_model_and_observation_values(model_values: np.ndarray, observation_values: np.ndarray):
    return model_values - observation_values


def get_compressed_values(values, mask):
    return np.ma.MaskedArray(values,mask).compressed()

def remove_valid_times_not_in_observation_dataset(model_values: np.ndarray, index_data_dict:dict, observation_dataset: xr.Dataset):
    valid_time_coordinates, valid_time_coordinate_indexes= np.unique(index_data_dict['valid_time'],return_inverse=True)

    #get new mask based on valid time
    valid_time_values_in_both, ind1, ind2 = np.intersect1d(valid_time_coordinates,observation_dataset.valid_time.values, return_indices=True)
    mask_version_od_valid_time_coordinates = np.ones(valid_time_coordinates.shape, dtype=bool)
    mask_version_od_valid_time_coordinates[ind1] = False
    
    end_mask = mask_version_od_valid_time_coordinates[valid_time_coordinate_indexes]


    #manipulate values
    model_values = get_compressed_values(model_values, end_mask)
    index_data_dict["valid_time"] = get_compressed_values(index_data_dict["valid_time"],end_mask)
    index_data_dict['site_id'] = get_compressed_values(index_data_dict['site_id'],end_mask)
    index_data_dict['base_day_time'] = get_compressed_values(index_data_dict['base_day_time'],end_mask)
    index_data_dict['lead_time'] = get_compressed_values(index_data_dict['lead_time'],end_mask)
    index_data_dict['base_date'] = get_compressed_values(index_data_dict['base_date'],end_mask)
    

    return model_values, index_data_dict


def extract_model_and_observation_source_data_with_indexes(model_dataarray: xr.DataArray,observation_dataset: xr.Dataset):
    model_values, index_data_dict = get_model_values_with_corresponding_indexes(model_dataarray=model_dataarray, observation_dataset=observation_dataset)
    model_values, index_data_dict = remove_valid_times_not_in_observation_dataset(model_values=model_values, index_data_dict=index_data_dict, observation_dataset=observation_dataset)
    
    observation_values = get_observation_values_for_specified_sites_and_valid_times(observation_dataset=observation_dataset,
                                                                                    site_id_values=index_data_dict["site_id"],
                                                                                    valid_time_values=index_data_dict["valid_time"])

    return model_values, observation_values, index_data_dict



def get_model_values_with_corresponding_indexes(model_dataarray: xr.DataArray, observation_dataset: xr.Dataset): #outputs values directly

    #broadcast values
    #   for converting to valid time format
    broadcast_site_id_dataarray = broadcast_dataarray_over_non_found_dimensions(dataarray=model_dataarray.site_id,
                                                                                all_dimension_sizes_dict=model_dataarray.sizes) # type: ignore
    broadcast_valid_times_dataarray = broadcast_dataarray_over_non_found_dimensions(dataarray=model_dataarray.valid_times_per_time_tuple,
                                                                                    all_dimension_sizes_dict=model_dataarray.sizes) # type: ignore
    #   for converting back
    broadcast_base_day_time_dataarray = broadcast_dataarray_over_non_found_dimensions(dataarray=model_dataarray.base_day_time,
                                                                                all_dimension_sizes_dict=model_dataarray.sizes) # type: ignore
    broadcast_lead_time_dataarray = broadcast_dataarray_over_non_found_dimensions(dataarray=model_dataarray.lead_time,
                                                                                    all_dimension_sizes_dict=model_dataarray.sizes) # type: ignore
    broadcast_base_date_dataarray = broadcast_dataarray_over_non_found_dimensions(dataarray=model_dataarray.base_date,
                                                                                    all_dimension_sizes_dict=model_dataarray.sizes) # type: ignore
    #get the order correct
    #   for converting to valid time format
    ordered_model_dataarray = model_dataarray.transpose("site_id", "base_date", "lead_time", "base_day_time")
    ordered_valid_times_dataarray = broadcast_valid_times_dataarray.transpose( "site_id", "base_date", "lead_time", "base_day_time")
    ordered_site_id_dataarray = broadcast_site_id_dataarray.transpose( "site_id", "base_date", "lead_time", "base_day_time")
    #   for converting back
    ordered_base_day_time_dataarray = broadcast_base_day_time_dataarray.transpose( "site_id", "base_date", "lead_time", "base_day_time")
    ordered_lead_time_dataarray = broadcast_lead_time_dataarray.transpose( "site_id", "base_date", "lead_time", "base_day_time")
    ordered_base_date_dataarray = broadcast_base_date_dataarray.transpose( "site_id", "base_date", "lead_time", "base_day_time")

    #get the model mask
    model_mask = dataset_creation.get_np_mask_of_given_dataarray(ordered_model_dataarray)
    #flatten the values using mask
    #   for converting to valid time format
    flattened_model_values = np.ma.MaskedArray(data=ordered_model_dataarray.values,mask=model_mask).compressed()
    flattened_valid_time_values = np.ma.MaskedArray(data=ordered_valid_times_dataarray.values,mask=model_mask).compressed()
    flattened_site_id_values = np.ma.MaskedArray(data=ordered_site_id_dataarray.values,mask=model_mask).compressed()
    #   for converting back
    flattened_base_day_time_values = np.ma.MaskedArray(data=ordered_base_day_time_dataarray.values,mask=model_mask).compressed()
    flattened_lead_time_values = np.ma.MaskedArray(data=ordered_lead_time_dataarray.values,mask=model_mask).compressed()
    flattened_base_date_values = np.ma.MaskedArray(data=ordered_base_date_dataarray.values,mask=model_mask).compressed()
    
    #format for understanding
    index_data_dict ={
        'valid_time':flattened_valid_time_values,
        'site_id':flattened_site_id_values,
        'base_day_time':flattened_base_day_time_values,
        'lead_time':flattened_lead_time_values,
        'base_date':flattened_base_date_values
        } 
    
    return flattened_model_values, index_data_dict


def get_observation_values_for_specified_sites_and_valid_times(observation_dataset: xr.Dataset, site_id_values:list, valid_time_values:list):
    site_index = xr.DataArray(site_id_values)
    valid_time_index = xr.DataArray(valid_time_values)
    observation_values = observation_dataset.observation_values.loc[site_index,valid_time_index].values
    
    return observation_values


def average_values_over_index_for_ndarray_with_na(values: np.ndarray):

    masked_values_array = np.ma.masked_invalid(values)
    averaged_values_over_index = masked_values_array.mean(axis=1)

    return averaged_values_over_index


def pre_average_model_and_observation_values(
        model_values: np.ndarray, observation_values: np.ndarray,
    requested_index_coordinates: np.ndarray, requested_index_coordinate_indexes: np.ndarray,
    pre_averaging_step: int | None ):
    
    value_list=[]
    for values in [model_values,observation_values]:
        intermediate_ndarray = np.full(shape=(len(requested_index_coordinates),len(values)),
                                    fill_value=np.nan,
                                    dtype=np.float32)

        indexes = np.add(requested_index_coordinate_indexes*len(values),np.arange(len(values)))

        np.put(a=intermediate_ndarray, ind=indexes, v=values)
        # shape: [0]-->index dimension, [1]--> value dimension
        if pre_averaging_step:
            index_length=intermediate_ndarray.shape[0]
            value_length=intermediate_ndarray.shape[1]
            # get remainder length to cut the ndarray first and then get it back together
            remainder_length = index_length%pre_averaging_step
            rest_length= index_length - remainder_length

            #get actual values
            pre_averaged_remainder=np.array([])
            if remainder_length!=0:
                remainder_ndarray = intermediate_ndarray[-remainder_length:]
                
                #reshape to make ready for pre averaging
                reshaped_remainder = remainder_ndarray.reshape((1,value_length*remainder_length))
                #average
                pre_averaged_remainder = average_values_over_index_for_ndarray_with_na(reshaped_remainder)
                pre_averaged_full_array = pre_averaged_remainder

            if remainder_length!=index_length:#if remainder isn't the same as the full
                rest_of_ndarray = intermediate_ndarray[:rest_length] #int actually not required, just for correct types
                reshaped_rest = rest_of_ndarray.reshape((int(rest_length/pre_averaging_step),value_length*pre_averaging_step))
                pre_averaged_rest = average_values_over_index_for_ndarray_with_na(reshaped_rest)
                pre_averaged_full_array = np.concatenate((pre_averaged_rest,pre_averaged_remainder),axis=0)
            #get index values
            pre_averaged_remainder=np.array([])
            old_coordinate_dtype = requested_index_coordinates.dtype
            intermediate_coordinates=requested_index_coordinates.astype('int64')
            if remainder_length!=0:
                remainder_coordinates = intermediate_coordinates[-remainder_length:]
                
                #reshape to make ready for pre averaging
                reshaped_remainder = remainder_coordinates.reshape((1,remainder_length))
                #average
                pre_averaged_remainder = reshaped_remainder.mean(axis=1)
                pre_averaged_full_coordinate_array = pre_averaged_remainder.astype(old_coordinate_dtype)

            if remainder_length!=index_length:#if remainder isn't the same as the full
                rest_of_coordinates = intermediate_coordinates[:rest_length] #int actually not required, just for correct types
                reshaped_rest = rest_of_coordinates.reshape((int(rest_length/pre_averaging_step),pre_averaging_step))
                pre_averaged_rest = reshaped_rest.mean(axis=1)
                pre_averaged_full_coordinate_array = np.concatenate((pre_averaged_rest,pre_averaged_remainder),axis=0).astype(old_coordinate_dtype)

            value_list.append((pre_averaged_full_array,pre_averaged_full_coordinate_array))
        else:
            value_list.append((intermediate_ndarray, requested_index_coordinates))
                    
                
    
    #       model           observation (array of values and indexes)
    return value_list[0], value_list[1]



def process_model_values_using_singular_axis(model_values: np.ndarray, observation_values: np.ndarray, indexed_singular_axis_name: str) :#TODO NOW
    #doesnt matter if we check observation values or model values, they should have the same shape and value locations
    # so using model values when possible
    if model_values.ndim==1: #if pre averaged,  do not need to mask as already valid values at all places
        match indexed_singular_axis_name: # will expand dims on observations to make later averaging easier
            case 'Sample Size':
                processed_singular_axis_model_values,processed_singular_axis_observation_values = np.ones_like(model_values), np.ones_like(observation_values)
            case 'Mean':
                processed_singular_axis_model_values,processed_singular_axis_observation_values = model_values, observation_values
            case 'Median':
                processed_singular_axis_model_values,processed_singular_axis_observation_values = model_values, observation_values
            case _:
                raise HTTPException(status_code=500, detail="Singular axis name not found. This shouldn't happen normally, check the starting data.")
        
        return processed_singular_axis_model_values, np.expand_dims(processed_singular_axis_observation_values,1) 

    elif model_values.ndim==2: #if not pre averaged, do need to mask as nans exist
        masked_model_values, masked_observation_values = np.ma.masked_invalid(model_values), np.ma.masked_invalid(observation_values)
        match indexed_singular_axis_name:
            case 'Sample Size':
                sample_size = dataset_creation.get_inverse_of_mask(masked_model_values.mask).sum(axis=1)
                return sample_size, sample_size
            case 'Mean':
                model_mean, observation_mean = masked_model_values.mean(axis=1), masked_observation_values.mean(axis=1)
                return model_mean, observation_mean
            case 'Median':
                model_median, observation_median = masked_model_values.median(axis=1), masked_observation_values.median(axis=1)
                return model_median, observation_median
            case _:
                raise HTTPException(status_code=500, detail="Singular axis name not found. This shouldn't happen normally, check the starting data.")
    else: raise HTTPException(status_code=500, detail='''This shouldn't happen, see the dataset processing file.''')




def process_model_values_using_comparative_axis(model_values: np.ndarray, observation_values: np.ndarray, indexed_comparative_axis_name: str ):
    if model_values.ndim==1: #if pre averaged, do not need to mask as already valid values at all places IMPORTANT: This is one dimensional data, functions should work with this: axis0:index
        match indexed_comparative_axis_name:
            case 'Bias':
                averaged_processed_comparative_axis_values = get_bias_of_model_and_observation_values(
                    model_values, observation_values)
            case _:
                raise HTTPException(status_code=500, detail="Comparative axis name not found. This shouldn't happen normally, check the starting data.")
    
    elif model_values.ndim==2: #if not pre averaged, do need to mask as nans exist, IMPORTANT: This is two dimensional data, functions should work with this: axis0:index, axis1:individual values
        #as such all functions should ideally work with masked arrays. Otherwise, the normally masked values can be filled via .filled(value) to make it work with the function.
        #(Obviously, the filled values should not effect the result of the calculation, so be careful about what the values are filled with)
        masked_model_values, masked_observation_values = np.ma.masked_invalid(model_values), np.ma.masked_invalid(observation_values)
        match indexed_comparative_axis_name:
            case 'Bias':
                non_averaged_processed_comparative_axis_values = get_bias_of_model_and_observation_values(
                    masked_model_values, masked_observation_values)
            case _:
                raise HTTPException(status_code=500, detail="Comparative axis name not found. This shouldn't happen normally, check the starting data.")
        averaged_processed_comparative_axis_values = average_values_over_index_for_ndarray_with_na(values=non_averaged_processed_comparative_axis_values)
    else: raise HTTPException(status_code=500, detail='''This shouldn't happen, see the dataset processing file.''')

    return averaged_processed_comparative_axis_values




def process_single_model_for_axes(model_values:np.ndarray,
                                          observation_values:np.ndarray,
                                          requested_index_coordinates:np.ndarray,
                                          requested_index_coordinate_indexes:np.ndarray,
                                           indexed_axis_list: list[data_models.ComparativeAxis | data_models.SingularAxis],
                                           pre_averaging_step: int|None):


    axis_data_dict={}
    observation_data_dict={}
    #also may not be pre averaged, [0] --> value, [1] --> index
    possibly_pre_averaged_model_values_with_indexes, possibly_pre_averaged_observation_values_with_indexes = pre_average_model_and_observation_values(
        model_values=model_values,observation_values=observation_values,
        requested_index_coordinates=requested_index_coordinates,
        requested_index_coordinate_indexes=requested_index_coordinate_indexes,
        pre_averaging_step=pre_averaging_step)

    temp_model_vals = possibly_pre_averaged_model_values_with_indexes[0]
    temp_observation_vals = possibly_pre_averaged_observation_values_with_indexes[0]

    for axis in indexed_axis_list:
        axis_name=axis.name.name

        


        if type(axis)==data_models.SingularAxis:
            # do process both for observations and models but leave the data for observations raw and combine it later in process_single_model_dataset_for_axes
            
            processed_model_values, processed_observation_values = process_model_values_using_singular_axis(model_values=temp_model_vals,
                                                                          observation_values=temp_observation_vals,
                                                                          indexed_singular_axis_name=axis_name)
            
            observation_data_dict[axis_name]=None #processed_observation_values #TODO
            #This data is pre-averaged just above and will be processed here. 
            #later, it will be averaged over models and data if not pre averaged

            processed_model_values_averaged_over_index = processed_model_values

        elif type(axis)==data_models.ComparativeAxis:
            processed_model_values_averaged_over_index = process_model_values_using_comparative_axis(model_values=temp_model_vals,
                                                                          observation_values=temp_observation_vals,
                                                                          indexed_comparative_axis_name=axis_name)
        

        
        # model values not necessarily averaged over index here (can also happen at pre averaging)
        axis_data_dict[axis_name]=output_formatting.format_to_axis_data(axis=axis,axis_float_values=processed_model_values_averaged_over_index)
        

    return axis_data_dict, observation_data_dict, possibly_pre_averaged_model_values_with_indexes[1]



def get_plotting_data_per_model_dict(base_model_dataset_selection:data_models.BaseModelDatasetSelection,
                                     masked_model_values_dataarray: xr.DataArray,
                                     space_model_processing_selection: (data_models.ModelProcessingSelection|
                                                                        data_models.FCOBPairProcessingSelection),
                                        wanted_models_selection: data_models.WantedModelsSelection
                                     ):
    
    observation_source_name = base_model_dataset_selection.observation_source_without_site_list.name.name

    plotting_data_per_model_dict={}
    observation_data_per_model_dict={}
    
    wanted_model_list = wanted_models_selection.space_model_list
    # wanted_models_selection.space_model_list initialised before to selected dataset models if None!
    
    for model in wanted_model_list:
        model_name=model.name.name
        observation_data_dict={}

        # select model dataarray
        dataarray_for_specific_model = masked_model_values_dataarray.sel(models=model_name)

        # get model and observation values along with their indexes and relevant info
        with dataset_creation.open_and_combine_all_model_observation_datasets(base_model_dataset_selection=base_model_dataset_selection).load() as observation_dataset:
            model_values, observation_values, index_data_dict = extract_model_and_observation_source_data_with_indexes( # type: ignore
                        model_dataarray=dataarray_for_specific_model,observation_dataset=observation_dataset)
        

        

        # if request in normal axis format # TODO format this all to some function like: get data for single model
        if type(space_model_processing_selection)==data_models.ModelProcessingSelection:
            requested_index=space_model_processing_selection.index
            requested_index_name=requested_index.name.name
            # get relevant data on coordinates
            requested_index_coordinates, requested_index_coordinate_indexes= np.unique(index_data_dict[requested_index_name],return_inverse=True)
                
            
            axis_data_dict, observation_data_dict, possibly_pre_averaged_index_coordinates = process_single_model_for_axes(model_values=model_values,
                                                                                observation_values=observation_values,
                                                                            requested_index_coordinates=requested_index_coordinates,
                                                                            requested_index_coordinate_indexes=requested_index_coordinate_indexes,
                                                                            indexed_axis_list=space_model_processing_selection.indexed_axis_list,
                                                                            pre_averaging_step=space_model_processing_selection.pre_averaging_step)
            
            formatted_data= output_formatting.format_to_plotting_data_per_model(model=model, index=requested_index,
            index_data_values=possibly_pre_averaged_index_coordinates, axis_data_dict=axis_data_dict, observation_source_name=observation_source_name)

        
        elif type(space_model_processing_selection)==data_models.FCOBPairProcessingSelection:
            # data isn't pre averaged, automatically assigned to response                     
            formatted_data = output_formatting.format_to_fcob_data(model_values=model_values,observation_values=observation_values)
        
        plotting_data_per_model_dict[model_name] = formatted_data
        observation_data_per_model_dict[model_name]=observation_data_dict #observation data dict indexed by axes
    
    return plotting_data_per_model_dict, observation_data_per_model_dict










# format: dict[str: dict[str: dataarray]]
#           model_name  sng axis name  index and actual data
# dataarrays of each axis will be merged and averaged over models  
def average_observation_data_properly(observation_data_dict):
    pass #TODO