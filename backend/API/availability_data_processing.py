from data_models import ObservationSourceWithoutSite, Parameter, Model



def add_existing_to_tuple(observation_source:ObservationSourceWithoutSite|None, parameter:Parameter|None):
    if observation_source and parameter: return (observation_source.name.name, parameter.name.name)
    elif observation_source: return observation_source.name.name,
    elif parameter: return parameter.name.name,
    else: raise ValueError('This is logically impossible.')


def get_all_request_combinations_list(observation_source:ObservationSourceWithoutSite|None, parameter:Parameter|None, model_list:list[Model]|None):
    
    #TODO check at input if any exists?
    all_request_combinations = []
    if model_list:
        for model in model_list:
            if parameter or observation_source:
                all_request_combinations.append(tuple(add_existing_to_tuple(observation_source, parameter)+(model.name.name,)))
            else: all_request_combinations.append(tuple(model.name.name))
    else:
        if parameter or observation_source:
            all_request_combinations.append(add_existing_to_tuple(observation_source, parameter))



    request_combination_without_models = None
    if model_list:
        if parameter or observation_source:
            request_combination_without_models=add_existing_to_tuple(observation_source, parameter)
    

    return all_request_combinations, request_combination_without_models
    


def convert_info_type_sets_to_intersected_sets_list_per_info_type(temp_selectable_sets_lists:dict[str,list[set]]):
    new_selectable_dict={}
    for info_type in temp_selectable_sets_lists.keys():
        if len(temp_selectable_sets_lists[info_type])!=0:
            if len(temp_selectable_sets_lists[info_type])==1:
                intersection_set = temp_selectable_sets_lists[info_type][0]
            elif len(temp_selectable_sets_lists[info_type])>1:
                intersection_set = temp_selectable_sets_lists[info_type][0].intersection(*temp_selectable_sets_lists[info_type][1:])
        else: intersection_set = set()

        new_selectable_dict[info_type] = list(intersection_set)
        
    return new_selectable_dict


