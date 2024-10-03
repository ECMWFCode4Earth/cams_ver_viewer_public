"use client"
import Menu from "@/app/ui/menu/menu";
import React, { Suspense } from "react";
import { startingdata } from "../lib/custom types/startingdata";
import { bodyDataMenu } from "../lib/custom types/bodydata";
import dynamic from "next/dynamic";
import { isBodyDataMenu } from "../lib/util/isBodyData";
import Loading from "../loading";

const AllPlots = dynamic(() => import("../plot/allplots"), {
  ssr: false,
});
const Histogram2d = dynamic(() => import("../plot/2dhistogram"), {
  ssr: false,
});
export function Client(
    {startingData, searchParams}:{startingData:startingdata; searchParams?: {
        [key: string]: string | string[] | number | undefined;
        NoP: number;
      }}
      
){
 const [bodyData, setBodyData] = React.useState<(bodyDataMenu|{})[]>([{}]) 
 let plots= Array()
 bodyData.map((value,index)=>{
 if(isBodyDataMenu(value)){
   plots.push(<Suspense fallback={<Loading/>}><AllPlots key={`plot_${index}`} plotData={value} index={index} bodyData={bodyData} setBodyData={setBodyData} /></Suspense>)}else{ plots.push(`Please Select Preferred Settings and Update plot ${index}`);
  }
 })

    return(<>
    <div id="plot" className="absolute left-24 columns-1">

    {plots}       
      {/*bodyData.map((value,index)=><AllPlots key={`plot_${index}`} plotData={value} index={index} />)*/}
        {/*<GeolocPlot startingData={startingData} bodyData={bodyData[0]}/>*/}
    </div><div className="absolute right-24 columns-1">
            <Menu startingData={startingData} bodyData={bodyData} setBodyData={setBodyData} />
        </div></>)  

}