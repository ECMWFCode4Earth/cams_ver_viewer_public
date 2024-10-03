"use client"
import { Data } from "plotly.js-dist";
import dynamic from "next/dynamic";
import { bodydata, bodyDataMenu } from "@/app/lib/custom types/bodydata";
import { graphdata, graphdatamodel } from "@/app/lib/custom types/graphdata";
import {isFCOB, isGraphData} from "@/app/lib/util/isGraphData"
//import { getModelandSite } from "../lib/fetchmodelandsite";
import { getModelPlottingData } from "../lib/fetchplottingdata";
import useSWR from "swr";
import React, { Dispatch, SetStateAction } from "react";
import { isBodyDataMenu, isBodyDataMenuArray } from "../lib/util/isBodyData";
import Histogram2d from "./2dhistogram";
import { getValueFromKeyValPair } from "../lib/util/getValueFromKeyValPair";
const GeolocPlot = dynamic(() => import("./geolocation"), {
  ssr: false,
});
const SimPlot = dynamic(() => import("./superimposed"), {
  ssr: false,
});
export default async function AllPlots({plotData,index,bodyData, setBodyData}:{
    plotData:bodyDataMenu;  
    index:number;
    bodyData: ({}|bodyDataMenu)[];
    setBodyData: Dispatch<SetStateAction<({} | bodyDataMenu)[]>>
  }
) {
  const reqData: bodydata = {
    space_model_dataset_selection: {
        base_model_dataset_selection: {
            month_selection: {
                month_range: [plotData.dates.startDate,plotData.dates.endDate]
            },
            observation_source_without_site_list: {
                name: JSON.parse(plotData.observationSource).name,
                metadata: JSON.parse(plotData.observationSource).metadata
            },
            parameter: plotData.parameter,
            space_model_list: plotData.models
        },
        pre_processing_selection: {
            match_models_selection: plotData.matchModels/100,
            consistent_dimension_selection_list: plotData.existingAcross.map((eacross)=> {return {dimension: {"name": eacross.name}, "existing_across": eacross.existingAcross/100}})
        }
    },
    lead_and_base_time_selection: {
        lead_time_range: plotData.leadTime
    },
    "date_and_site_selection": null,
    space_model_processing_selection: plotData.ShowFCOBpairs ? {fcob_pair_processing: true}: {
        pre_averaging_step: plotData.preAveraging, 
        index: plotData.index,
        indexed_axis_list: plotData.axes
    },
    wanted_models_selection: {
    space_model_list: plotData.models}
}
  let dataArray: Data[] = [];
  console.log(reqData)
  return ReturnPlots(reqData, plotData, index)
   

  async function ReturnPlots(reqData:bodydata,plotData:bodyDataMenu, indexx: number) {//graphdata type is currently any
    const {data, error, isLoading} = useSWR(reqData,getModelPlottingData)
    
    if (error) return <div>failed to load</div>
    if (isLoading) return <div>loading...</div>
    const graphData = data
    

    
        if (plotData.ShowFCOBpairs){
          if(isFCOB(graphData))
          return <Histogram2d fcob_data={getValueFromKeyValPair(graphData.response.fc_ob_pair_data_per_model)[0].fcob_data}  />
        }else if (plotData.index.name==="site_id") {
          if (!isGraphData(graphData)){ return <p>{`couldn't fetch plot ${indexx} error`}</p>}
          return Object.entries(graphData.response.plotting_data_per_model_dict).map(([key,value])=> 
            {let scale= Array(0)
              Object.entries(value.axis_data_dict).map(([key,val])=>{ scale.push(val.float_list)})
              const datalist =value.index_data.data_type_list as {
                site_name_list: string[];
                latitude_float_list: number[];
                longitude_float_list: number[];
            }
            
            if (isBodyDataMenuArray(bodyData)) return <GeolocPlot setBodyData={setBodyData} key={`geoplot_${indexx}`} bodyData={bodyData} selectedbodyData={plotData} name={datalist.site_name_list} lat={datalist.latitude_float_list} lon={datalist.longitude_float_list} index={indexx} colorScaleData={scale[0]} sizeScaleData={scale[1]} />})
        } else{
          if (!isGraphData(graphData)){ return <p>{`couldn't fetch plot ${indexx} error`}</p>
        }
        Object.entries(graphData.response.plotting_data_per_model_dict).map(([key,value])=>superImposedData(key,value,plotData));
          return (
            <SimPlot
              plotData={plotData}
              data={dataArray}
              i={index}
            />
          );
        }
        /*else {
          b = i;
          a = 0;
          -/
          return graphData[i].map(multiplotjsx);
        }*/
      

      /*function multiplotjsx(graphDataMap: any) {
        let c = Array();

        console.log("a");
        for (
          let modelnumber = 1;
          modelnumber < plotData.model.length + 1;
          modelnumber++
        ) {
          a++;
          plotcounter++;
          c.push(
            <NewPlot
              plotData={plotData}
              graphData={graphDataMap}
              i={plotcounter - 1}
              a={a - 1}
              y={
                graphDataMap[
                  `${Object.getOwnPropertyNames(graphDataMap)[modelnumber]}`
                ]
              }
            />
          );
        }
        return c;
      }*/
      function superImposedData(modelname:string,value: graphdatamodel, plotData:bodyDataMenu) { //TODO fix type
        Object.entries(value.axis_data_dict).map(([axisname,axisval])=>{
          
        dataArray.push({
            connectgaps: false,
            x: value.index_data.data_type_list,
            y: axisval.float_list,
            name: `${modelname}_${
              plotData.parameter.name
            }_${axisname}`,
            type: "scatter",
            mode: "lines",
            line: { dash: "solid", width: 2 },
            marker: { size: 4 },
          }) })
      
}    }
  }

