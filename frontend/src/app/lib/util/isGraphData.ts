import { FCOB,  graphdata } from "../custom types/graphdata";

export function isGraphData(graphData:graphdata|FCOB|undefined):graphData is graphdata{
    return (graphData as graphdata).response.plotting_data_for_observations_averaged !== undefined;  
  }


  export function isFCOB(graphData:graphdata|FCOB|undefined):graphData is FCOB{
    return (graphData as FCOB).response.fc_ob_pair_data_per_model !== undefined;
  }