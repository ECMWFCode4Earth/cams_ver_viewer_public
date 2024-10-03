import { metadata, model_dict, nameString, observation_source_dict } from "./startingdata"

export type availability={
  observation_source: {
    name: string,
    metadata: metadata
  }|null,
  parameter: nameString|null,
  space_model_list: model_dict[]|null
}

export type availableSelectionsType={
  request: any  
  response:{
  month_list: 
        {
            name: string
        }[],
        observation_source_without_site_list: {
        name: string,
        metadata:metadata
      }[],
    parameter_list: 
        {
            name: string
        }[]
    space_model_list: model_dict[]
    observation_source_with_site_list_list: observation_source_dict[]}
}
      
    
  