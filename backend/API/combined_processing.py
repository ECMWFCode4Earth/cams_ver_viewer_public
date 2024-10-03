import data_models
import dataset_creation, dataset_processing, output_formatting, availability_data_processing
import numpy as np
import xarray as xr
from fastapi import HTTPException



def get_model_plotting_data(model_plotting_data_request: data_models.ModelPlottingDataRequest):
      #get request data in variables for easier access
   space_model_dataset_selection,                              individual_lead_time_selection_dict,date_and_site_selection,                                        space_model_processing_selection=(
      model_plotting_data_request.space_model_dataset_selection,  model_plotting_data_request.lead_and_base_time_selection.individual_lead_time_selection_dict,   model_plotting_data_request.date_and_site_selection,model_plotting_data_request.space_model_processing_selection)
      
   (base_model_dataset_selection,                                       pre_processing_selection)=(
            space_model_dataset_selection.base_model_dataset_selection, space_model_dataset_selection.pre_processing_selection)
      
   wanted_models_selection = model_plotting_data_request.wanted_models_selection

        #get masked values
   masked_model_values_dataarray = dataset_creation.get_masked_model_values_dataarray(base_model_dataset_selection=base_model_dataset_selection,
                                                                                            pre_processing_selection=pre_processing_selection,
                                                                                            date_and_site_selection=date_and_site_selection,
                                                                                            individual_lead_time_selection_dict=individual_lead_time_selection_dict) # type: ignore


        #process masked values
   plotting_data_per_model_dict, observation_data_per_model_dict= dataset_processing.get_plotting_data_per_model_dict(base_model_dataset_selection=base_model_dataset_selection,
                                                                                          masked_model_values_dataarray=masked_model_values_dataarray,
                                                                                          space_model_processing_selection=space_model_processing_selection,
                                                                                          wanted_models_selection=wanted_models_selection) # type: ignore
         #average observation data properly
            
   averaged_observation_data = dataset_processing.average_observation_data_properly(observation_data_dict=observation_data_per_model_dict)
         
      #format to response #TODO observation data
   response = output_formatting.format_model_data_to_plotting_response(plotting_data_per_model_dict=plotting_data_per_model_dict,
                                                               model_processing_selection=space_model_processing_selection)
      
   return response
        
def get_possible_dataset_combinations(model_dataset_availability_request: data_models.ModelDatasetAvailabilityRequest):
   observation_source, parameter, model_list = model_dataset_availability_request.observation_source, model_dataset_availability_request.parameter, model_dataset_availability_request.space_model_list 
   all_request_combinations, request_combination_without_models = availability_data_processing.get_all_request_combinations_list(observation_source=observation_source, parameter=parameter, model_list=model_list) 
        
   # get available infos in sets, the output formatted same as temp variable, in the lists there is just info though
   temp_selectable_sets_lists = {"Observation Sources":list(), "Months":list(), "Parameters":list(), "Models":list()}
   for request_combination in all_request_combinations:
      if request_combination not in data_models.AVAILABILITY_DICT.keys():
            raise HTTPException(status_code=400, detail=f'{request_combination} not found.')
      for info_type in data_models.AVAILABILITY_DICT[request_combination].keys():
            temp_selectable_sets_lists[info_type].append(set(data_models.AVAILABILITY_DICT[request_combination][info_type]))#will append a list of available data
   
   #if models given, also add possible models taken by making a request without the model in request
   if request_combination_without_models:      
      temp_selectable_sets_lists['Models'].append (set(data_models.AVAILABILITY_DICT[request_combination_without_models]['Models']))

   # get intersection of sets in each list
   new_selectable_dict = availability_data_processing.convert_info_type_sets_to_intersected_sets_list_per_info_type(
       temp_selectable_sets_lists=temp_selectable_sets_lists
   )

   
   response = output_formatting.format_to_model_dataset_availability_response(selectable_dict=new_selectable_dict, original_model_dataset_availability_request=model_dataset_availability_request )

   return response



def get_available_dates_and_sites(available_dates_and_sites_request: data_models.ModelAvailableDatesAndSitesRequest):
   space_model_dataset_selection, lead_and_base_time_selection = available_dates_and_sites_request.space_model_dataset_selection, available_dates_and_sites_request.lead_and_base_time_selection
   pre_processing_selection = space_model_dataset_selection.pre_processing_selection
   get_coordinates_for_sites = available_dates_and_sites_request.get_coordinates_for_sites

   base_model_dataset_selection = space_model_dataset_selection.base_model_dataset_selection
   consistent_dimension_selection_list = pre_processing_selection.consistent_dimension_selection_list
   individual_lead_time_selection_dict = lead_and_base_time_selection.individual_lead_time_selection_dict
   observation_source_name = base_model_dataset_selection.observation_source_without_site_list.name.name
   
   with dataset_creation.open_and_combine_all_model_datasets(base_model_dataset_selection) as combined_dataset:
      with combined_dataset.site_date_availability_mask.load() as combined_site_date_availability_mask:

         inverse_mask = dataset_creation.get_inverse_of_mask(combined_site_date_availability_mask.values)
         inverted_mask_dataarray = xr.DataArray(data=inverse_mask, coords=combined_site_date_availability_mask.coords)

         np_model_mask = dataset_creation.make_model_mask(inverted_mask_dataarray=inverted_mask_dataarray,
                                                             consistent_dimension_selection_list=consistent_dimension_selection_list,
                                                             individual_lead_time_selection_dict=individual_lead_time_selection_dict)# type: ignore
         
         #invert mask back to use it
         np_mask = dataset_creation.get_inverse_of_mask(np_model_mask)

         masked_values_nad_dataarray = dataset_creation.fill_dataarray_with_nas_using_mask(dataarray=combined_site_date_availability_mask, np_mask=np_mask)

   non_existing_removed_da = masked_values_nad_dataarray.dropna(dim='site_id',how='all').dropna(dim='base_date',how='all')  
   site_id_name_ndarray, base_date_ndarray = non_existing_removed_da.site_id.values, non_existing_removed_da.base_date.values
   #invert once more to be able to use np.any
   inverted_existance_mask = dataset_creation.get_inverse_of_mask(non_existing_removed_da.transpose("site_id", "base_date", "lead_time", "base_day_time","models").values).any(axis=(2,3,4))
   existance_mask = dataset_creation.get_inverse_of_mask(inverted_existance_mask)
   
   return output_formatting.format_available_dates_and_sites_to_response(site_id_name_ndarray=site_id_name_ndarray,
                                                                         base_date_ndarray= base_date_ndarray,
                                                                         existance_mask=existance_mask,
                                                                         observation_source_name=observation_source_name,
                                                                         get_coordinates_for_sites=get_coordinates_for_sites)