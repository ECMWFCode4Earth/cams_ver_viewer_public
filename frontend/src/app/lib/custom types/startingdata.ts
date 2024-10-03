
export type startingdata = {
  dataset: {
    month_dict: {[key:string]:nameString};
    parameter_dict: {[key:string]:nameString};
    space_model_dict: {[key:string]: model_dict};
    observation_source_dict: {[key:string]: observation_source_dict};
  };
  processing: {
    consistent_dimension_list: nameString[];
    index_list: nameString[];
    singular_axis_list: nameString[];
    comparative_axis_list: nameString[];
  };
};
export interface metadata{alias_list: {name: string ;alias_type: string}[]}
export interface nameString{name: string;}
interface Site{
  name: string;
  latitude_float: number;
  longitude_float: number;
}
export interface observation_source_dict{
  name: string;
  site_with_coordinates_list: Site[];
  metadata: metadata;
}

export interface model_dict{
name: string;
base_name: string;
max_lead_hour_int: number;
base_hour_name_list: string[];
step_hour_int: number;
metadata:metadata;
}