import { metadata, model_dict, nameString } from "./startingdata"

// for requests
export type bodydata = {
  space_model_dataset_selection: {
      base_model_dataset_selection: {
          month_selection: {
              month_range:(nameString|null)[]
          },
          observation_source_without_site_list: {
              name: string,
              metadata: metadata
          },
          parameter: nameString 
          space_model_list: model_dict[]
      },
      pre_processing_selection: {
          match_models_selection: number, 
          consistent_dimension_selection_list: {dimension: {name: string}, existing_across: number}[]
      }
  },
  lead_and_base_time_selection: {
      lead_time_range: number[]
  },
  date_and_site_selection: {date_list:"all"|string[], site_list: "all"|string[]},
  space_model_processing_selection:  {fcob_pair_processing: boolean} | {
      pre_averaging_step: number,
      index: nameString,
      indexed_axis_list: nameString[]
  },
  wanted_models_selection: {
    space_model_list: model_dict[]}
}

export type bodyDataMenu= {
  observationSource: string,
  models: model_dict[],
  parameter: nameString,
  dates:{
    startDate: nameString | null,
    endDate: nameString | null, 
  },
  preAveraging: number,
  leadTime: number[],
  matchModels:number,
  ShowFCOBpairs: boolean | null,
  ShowFCOBpairsas:string,
  index:nameString,
  axes:nameString[],
  site_list: string[]| "all"
  
  consistentDimensions: nameString[],
  existingAcross:{name:string, existingAcross:number}[]
  
} 