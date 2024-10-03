

export type graphdata= {
    request:any,
    response:
    {
        plotting_data_per_model_dict: {[key:string]: graphdatamodel},
        plotting_data_for_observations_averaged: null},
}
export type FCOB={
    request: any,
    response:{fc_ob_pair_data_per_model:{[key:string]:{fcob_data:{data:number[]}[]}}}
}
export interface fcob_data{data: number[]}[]

export interface graphdatamodel{
    "model": {
        "name": string,
        "base_name": string,
        "base_hour_name_list": number[]
        "max_lead_hour_int": number,
        "step_hour_int": number,
        "metadata": {
            "alias_list": 
                {
                    "name": string,
                    "alias_type": string
                }[]
            
        }
    },
    "index_data": {
        "index": {
            "name": string
        },
        "data_type_list": string[] | {site_name_list: string[], latitude_float_list: number[], longitude_float_list: number[]}
    },
    "axis_data_dict": {
        [key:string]: axis_data
    }
}
type axis_data={
    
        "axis": {
            "name": string
        },
        "float_list": number[]
    
}