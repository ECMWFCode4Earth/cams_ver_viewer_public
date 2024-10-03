import { metadata, nameString } from "./startingdata"

export type fetchModelandSite={
    space_model_dataset_selection: {
      base_model_dataset_selection: {
        month_selection: {
          month_range: (nameString|null)[],
          month_list: null
        },
        observation_source_without_site_list: {
          name: string|null,
          metadata: metadata|null
        },
        parameter: nameString[]|null,
        space_model_list: [
          {
            name: string|null,
            base_name: string|null,
            base_hour_name_list: [
              string
            ]|null,
            max_lead_hour_int: number|null,
            step_hour_int: number|null,
            metadata: metadata|null
          }
        ]
      },
      pre_processing_selection: {
        match_models_selection: {
          tolerance_float: number|null
        },
        consistent_across_selection: {
          dimension_name: nameString|null,
          tolerance_float: number|null
        }
      }
    }
  }