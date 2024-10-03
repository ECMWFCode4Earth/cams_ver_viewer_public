import { model_dict } from "../custom types/startingdata";

export function getSmallestMaxLead(dict: model_dict[]){
    const maxleadtime:number[]= Array();
    dict.map((model)=> maxleadtime.push(model.max_lead_hour_int))
    return Math.min(...maxleadtime)
}