"use client"
import { Box } from "@mui/material";
import { nameString } from "../../../lib/custom types/startingdata";
import React from "react";
import {CustomSlider} from "./CustomSlider"

export function ConsistentDimensionsExistingAcross({consistentDimensions,dimension,setDimension}:{consistentDimensions:nameString[];dimension:{name:string, existingAcross:number}[];setDimension:React.Dispatch<React.SetStateAction<{
    name: string;
    existingAcross: number;
}[]>> }){
    if (consistentDimensions.length>=1) {return consistentDimensions.map((e,i)=> { 
        return (<CustomSlider key={dimension[i].name} onChange={(event: Event, newValue: number | number[], activeThumb: number)=> handleChangeExistingAcross(i,event,newValue,activeThumb) } value={dimension[i].existingAcross} label={dimension[i].name===undefined?"":dimension[i].name +" existing across %    "} sliderdata={{
            default_val: 0,
            min: 0,
            max: 100,
            step: 1
        }} ></CustomSlider>
    
    )
})}else <p>1</p>
    
         
function handleChangeExistingAcross(i:number,event: Event, newValue: number | number[], activeThumb: number): void {
    const nextDimension: {name:string, existingAcross:number}[] = dimension.map((d, index) => {
     if (i === index ) { 
       d={
         name:dimension[i].name,
         existingAcross: Array.isArray(newValue)? newValue[0]:newValue
      }
       return d ;
     } else {
       // The rest haven't changed
       return d;
     }
   });
   setDimension(nextDimension);
 }
}
