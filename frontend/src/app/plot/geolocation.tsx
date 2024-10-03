"use client";
import { bodyDataMenu } from "@/app/lib/custom types/bodydata";

import Plotly, { PlotlyHTMLElement } from "plotly.js-dist";
import { Dispatch, SetStateAction, useEffect } from "react";

export default function GeolocPlot({
  selectedbodyData,
  name,
  lon,
  lat,
  index,
  bodyData,
  setBodyData,
  colorScaleData,
  sizeScaleData,
}: {
  selectedbodyData: bodyDataMenu;
  name: string[];
  lon: number[];
  lat: number[];
  index: number;
  bodyData: bodyDataMenu[];
  setBodyData: Dispatch<SetStateAction<({} | bodyDataMenu)[]>>
  colorScaleData: number[];
  sizeScaleData: number[];
}) {
  console.log(name[0])
  let plot_div_id = "plot_div_" + index as string +"_map";

  useEffect(() => { 
    Plotly.newPlot(plot_div_id, data, layout);
    
 (document.getElementById(plot_div_id) as PlotlyHTMLElement).on('plotly_click', function(data){
  const nextBodyData: (bodyDataMenu|{})[] = bodyData.map((item:bodyDataMenu|{},i) => {
    if (i === index ) { //Number constructor is used to make the if statement typesafe, would still work
     
      item={
        observationSource: bodyData[i].observationSource,
        models:bodyData[i].models,
        parameter: bodyData[i].parameter,
        dates: bodyData[i].dates,
        preAveraging: bodyData[i].preAveraging,
        leadTime:bodyData[i].leadTime,
        matchModels:bodyData[i].matchModels,
        ShowFCOBpairs: bodyData[i].ShowFCOBpairs,
        ShowFCOBpairsas: bodyData[i].ShowFCOBpairsas,
        index: {name:"valid_time"},
        axes: bodyData[i].axes,
        site_list: data.points.map((points: any)=>{return points.name as string}),
        existingAcross: bodyData[i].existingAcross
     }
      return item ;
    } else {
      // The rest haven't changed
      return item;
    }
  });
  setBodyData(nextBodyData);
})
  });

  /*const name: string[]= startingData.dataset.observation_source_dict[bodyData.observationSource].site_with_coordinates_list.map(e=>e.name);
  const lon: number[]=  startingData.dataset.observation_source_dict[bodyData.observationSource].site_with_coordinates_list.map(e=>e.longitude_float);
  const lat: number[]=  startingData.dataset.observation_source_dict[bodyData.observationSource].site_with_coordinates_list.map(e=>e.latitude_float);*/
  const data = [{

    type: 'scattergeo',

    mode: 'markers',
    text: name,
    lon: lon,
    lat:lat,

    marker: {
        colorscale: [[0,'rgb(5, 10, 172)'],[0.35,'rgb(40, 60, 190)'],[0.5,'rgb(70, 100, 245)'], [0.6,'rgb(90, 120, 245)'],[0.7,'rgb(106, 137, 247)'],[1,'rgb(220, 220, 220)']], 
        size: sizeScaleData.map((e)=>e/40),
        colorbar: {

          title: `${bodyData[index].axes[0].name}`,

          ticksuffix:'',

          showticksuffix: 'last'

      },
        color: colorScaleData,

        line: {

            width: 0

        }

    },

    name: selectedbodyData.observationSource + 'map',
    
    textposition: [

        'top right', 'top left', 'top center', 'bottom right', 'top right',

        'top left', 'bottom right', 'bottom left', 'top right', 'top right'

    ],


   

}];
  const layout = {
    
    width: 1000,
    height: 600,
    geo: {
        showcountries: true,
        scope: 'world',

        resolution: 50

    }

};
  return <div id={plot_div_id} />;

}

