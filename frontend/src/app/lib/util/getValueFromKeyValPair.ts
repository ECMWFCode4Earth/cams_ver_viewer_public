export function getValueFromKeyValPair(dict: {[Key:string]:any}){
    return Object.entries(dict).map(([key,value]) => value)
  }