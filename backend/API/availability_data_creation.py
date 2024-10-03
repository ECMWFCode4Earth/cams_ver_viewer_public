from general_functions_and_variables import get_all_file_paths_dictionary_in, get_all_individual_file_paths_in, save_to_file_as_json, save_to_file_as_pickled
from verisualiser_settings import FORMATTED_DATA_DIRECTORY_ADDRESS, AVAILABILITY_JSON_LOCATION, AVAILABILITY_PICKLE_LOCATION, FORMATTED_DATA_DIRECTORY_ADDRESS_WITH_SEPARATOR, ORDER_OF_INFO_TYPES_FROM_FS
import os
from itertools import combinations

#NOTES
#when checking if current request available, for each info type get the intersection of the results from availability checking, then check if all of the sent full names from the frontend exist in this intersection  

# decoded smaller when pickle, encoded smaller when json, possibly because of python's optimisations
SAVE_DECODED = True #if true, save with decoded strings, if false, save with encoded strings
SAVE_AS_JSON = True #if true, save as json, if false, save as pickle



def add_info_type_number_to_start_of_int(int_to_add_to_start:int, info_type_number: int):
    return int(str(info_type_number) + str(int_to_add_to_start))


def get_encoding_and_decoding_dictionaries(all_file_paths_as_name_tuples_list:list, info_type_number_per_info_type_dict:dict):
    all_unique_full_name_set_dict       = {}
    all_unique_full_name_list_dict      = {}                    # info type                 --> full name
    from_full_name_to_encoded_name      = {}                    # info type, full name      -->  encoded name 
    from_encoded_name_to_full_name      = {}                    # info type, encoded name   -->  full name

        #get unique names as dictionary
    for file_info_tuple in all_file_paths_as_name_tuples_list:
        for i,file_info in enumerate(file_info_tuple):
            all_unique_full_name_set_dict.setdefault(ORDER_OF_INFO_TYPES_FROM_FS[i], set()).add(file_info)

    #make the set dicts info into list dict
    for info_type in all_unique_full_name_set_dict.keys():
        all_unique_full_name_list_dict[info_type] = list(all_unique_full_name_set_dict[info_type])

    #get dictionaries for encoding and decoding full names
    for info_type in all_unique_full_name_list_dict.keys():
        for i, full_name in enumerate(all_unique_full_name_list_dict[info_type], start=1):
            encoded_int = add_info_type_number_to_start_of_int(int_to_add_to_start=i, info_type_number=info_type_number_per_info_type_dict[info_type])

            from_full_name_to_encoded_name[full_name] =   encoded_int
            from_encoded_name_to_full_name[encoded_int] = full_name
    
    return from_full_name_to_encoded_name, from_encoded_name_to_full_name




def get_combinations_list_of_list_of_tuple(tuple_list:list [tuple], wanted_combination_length: int):
    tuple_combinations_set = set()
    for iterated_tuple in tuple_list:
        tuple_combinations_set.update(list(combinations(iterable=iterated_tuple, r=wanted_combination_length)))
    return list(tuple_combinations_set)



def get_missing_element(in_tuple: tuple, existing_elements_tuple: tuple): #accepts and returns ints
    return int(*(set(in_tuple)-set(existing_elements_tuple)))




def get_one_dimension_downed_combinations_list(tuple_list:list [tuple], info_separated:bool):
    combination_tuple_with_removed_data_list = list()
    combination_tuple_list = list()
    wanted_combination_length = len(tuple_list[0])-1

    for iterated_tuple in tuple_list:
        combination_tuples_in_tuple_list = list(combinations(iterable=iterated_tuple, r=wanted_combination_length))
        for combination_tuple in combination_tuples_in_tuple_list:
            if info_separated:
                new_tuple_with_info_separated = (combination_tuple,get_missing_element(in_tuple=iterated_tuple,existing_elements_tuple=combination_tuple))
                combination_tuple_with_removed_data_list.append(new_tuple_with_info_separated)
            elif not info_separated:
                combination_tuple_list.append(combination_tuple)
    
    if info_separated:
        return combination_tuple_with_removed_data_list
    elif not info_separated:
        return combination_tuple_list



def convert_tuple(tuple_to_convert: tuple, conversion_dictionary: dict):
    new_items_list = []
    for item in tuple_to_convert:
        new_items_list.append(conversion_dictionary[item])
    return tuple(new_items_list)



def convert_tuples_list(tuples_list: list, conversion_dictionary: dict):
    converted_tuples_list = []
    for old_tuple in tuples_list:
        new_tuple = convert_tuple(tuple_to_convert=old_tuple, conversion_dictionary=conversion_dictionary) 
        converted_tuples_list.append(new_tuple)
    
    return converted_tuples_list


def get_info_dict(int_tuples_list: list):
    info_dict = {'len1':{},'len2':{},'len3':{},'len4':{}}
    #   {len4:{combinations:{1:set[all related 1 typed infos]}}} 

    for int_tuple in int_tuples_list:
            info_dict['len4'][int_tuple]=()
    
    temp_int_tuples_list = int_tuples_list
    for i in reversed(range(1,4)):#only doing for len3 to len 1
        info_int_tuples = get_one_dimension_downed_combinations_list(tuple_list=temp_int_tuples_list, info_separated=True)
        for info_tuple in info_int_tuples:
            if not info_dict['len'+str(i)].setdefault(info_tuple[0]):
                info_dict['len'+str(i)][info_tuple[0]]=set()
            info_dict['len'+str(i)][info_tuple[0]].add(info_tuple[1])
        temp_int_tuples_list = [info_tuple[0] for info_tuple in info_int_tuples if len(info_tuple)>0]



    return info_dict


# for 4 --> 3,2,1

def get_all_combinations(of_tuple: tuple):
    combinations_list = []

    if len(of_tuple)>1:
        temp_tuples_list = [of_tuple]
        for i in reversed(range(1,len(of_tuple))):
            one_shorter_combinations_list = get_one_dimension_downed_combinations_list(tuple_list=temp_tuples_list, info_separated=False)
            combinations_list.extend(one_shorter_combinations_list)
            temp_tuples_list = one_shorter_combinations_list

    elif len(of_tuple)==1:
        combinations_list = [of_tuple]
    
    return combinations_list
        
def separate_different_info_types(of_info_list: list, decoding_dict: dict, info_type_per_info_type_number_dict: dict):#of_list: list, decoding_dict: dict, info_type_per_info_type_number_dict: dict): #decoding_dict and info_type_per_info_type_number_dict here for SAVE_DECODED
    info_type_separated_dictionary = {}

    for info in of_info_list:
        if not SAVE_DECODED: info_type_separated_dictionary.setdefault(int(str(info)[0]),list()).append(info)
        elif SAVE_DECODED: info_type_separated_dictionary.setdefault(info_type_per_info_type_number_dict[int(str(info)[0])],list()).append(decoding_dict[info])

    # #add each info to set to not repeat
    # for info in of_list:
    #     if not SAVE_DECODED: info_type_separated_set_dictionary.setdefault(int(str(info)[0]),set()).add(info)
    #     elif SAVE_DECODED: info_type_separated_set_dictionary.setdefault(info_type_per_info_type_number_dict[int(str(info)[0])],set()).add(info)

    # #convert to list
    # for key in info_type_separated_set_dictionary.keys():
    #     if not SAVE_DECODED: info_type_separated_list_dictionary[key] = list(info_type_separated_set_dictionary[key])
    #     elif SAVE_DECODED: info_type_separated_list_dictionary[key] = convert_tuple(tuple(info_type_separated_set_dictionary[key]), decoding_dict)
        
    return info_type_separated_dictionary




def get_info_list(for_tuple: tuple, info_dict: dict):
    # all_combinations = get_all_combinations(of_tuple=for_tuple)
    # all_infos_set = set()

    # for found_combination in all_combinations:
    #     all_infos_set.update(info_dict['len'+str(len(found_combination))][found_combination])
    # return list(all_infos_set)
    return list(info_dict['len'+str(len(for_tuple))][for_tuple])
    



    

def get_final_availability_dict(info_dict: dict, decoding_dict:dict, info_type_per_info_type_number_dict:dict): #decoding_dict and info_type_per_info_type_number_dict here for SAVE_DECODED
        # IMPORTANT: order matters in tuples, so full name tuples should be specifically encoded in order, in availability dict and also when checking availability dict. This happens automatically in python here as they are ordered lists.
    final_availability_dict         = {}                            # int tuple        -->  ints per info type
                                                                                        #{int_tuple:{1:int_list}}
                                                    # int tuples ordered always from the info type with the smallest number to the largest

    for length in info_dict.keys(): #for each length
        for int_tuple in info_dict[length].keys(): #for each info in length

            info_list_of_tuple = get_info_list(for_tuple=int_tuple, info_dict=info_dict)
            
            if not SAVE_DECODED: final_availability_dict[int_tuple] =  separate_different_info_types(of_info_list=info_list_of_tuple, decoding_dict=decoding_dict, info_type_per_info_type_number_dict=info_type_per_info_type_number_dict)
            elif SAVE_DECODED: final_availability_dict[convert_tuple(int_tuple, decoding_dict)] =  separate_different_info_types(of_info_list=info_list_of_tuple, decoding_dict=decoding_dict, info_type_per_info_type_number_dict=info_type_per_info_type_number_dict)

    return final_availability_dict


def get_availability_data_to_save_to_file():

    info_type_number_per_info_type_dict = {"Observation Sources":1, "Months":2, "Parameters":3, "Models":4}
    info_type_per_info_type_number_dict = {1:"Observation Sources", 2:"Months", 3:"Parameters", 4:"Models"}
    #info type numbers should start from 1, otherwise they won't work with ints. Also they should have a consistent length in base 10 as ints.
    

    all_file_names = get_all_individual_file_paths_in(all_file_paths=get_all_file_paths_dictionary_in(folder_path=FORMATTED_DATA_DIRECTORY_ADDRESS, file_path_type='model'))
    all_file_paths_as_name_tuples_list = [tuple(file_path.removesuffix(".nc").removeprefix(FORMATTED_DATA_DIRECTORY_ADDRESS_WITH_SEPARATOR).split(os.sep, 4)) for file_path in all_file_names]

    encoding_dict, decoding_dict = get_encoding_and_decoding_dictionaries(all_file_paths_as_name_tuples_list=all_file_paths_as_name_tuples_list,
                                                           info_type_number_per_info_type_dict=info_type_number_per_info_type_dict)

    int_tuples_list = convert_tuples_list(tuples_list=all_file_paths_as_name_tuples_list, conversion_dictionary=encoding_dict)

    info_dict = get_info_dict(int_tuples_list=int_tuples_list) #! contains sets

    final_availability_dict = get_final_availability_dict(info_dict=info_dict, decoding_dict=decoding_dict, info_type_per_info_type_number_dict=info_type_per_info_type_number_dict)
    
    return final_availability_dict, encoding_dict, decoding_dict



def get_availability_data_and_save_to_file(as_json:bool):
    availability_dict, encoding_dict, decoding_dict = get_availability_data_to_save_to_file()
    if as_json:
        saving_location = AVAILABILITY_JSON_LOCATION
        save_to_file_as_json(data={
        'availability_dict':availability_dict,
        'availability_info_encoding_dict':encoding_dict,
        'availability_int_decoding_dict':decoding_dict
    },
    saving_location = saving_location)
        
    elif not as_json:
        saving_location = AVAILABILITY_PICKLE_LOCATION
        save_to_file_as_pickled(data={
        'availability_dict':availability_dict,
        'availability_info_encoding_dict':encoding_dict,
        'availability_int_decoding_dict':decoding_dict
    },
    saving_location = saving_location)

    print(f'Saved availability data to file: {saving_location}.')



get_availability_data_and_save_to_file(as_json=SAVE_AS_JSON)