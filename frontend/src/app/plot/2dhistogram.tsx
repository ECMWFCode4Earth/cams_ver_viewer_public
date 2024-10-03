"use client";

import Plotly, { AxisType, Dash, Shape } from "plotly.js-dist";
import { title } from 'process';
import { useEffect } from "react";

export default function Histogram2d({
  fcob_data,
 // bodyData
  
  
}: {fcob_data: {data:number[]}[];
  //bodyData: bodyDataMenu|{}
}) {
 
  const i=0
  let plot_div_id = "plot_div_" + i;

  useEffect(() => { 
    Plotly.newPlot(plot_div_id, data, layout);
  });
 


  //const genRanHex = (size: number) => [...Array(size)].map(() => Math.floor(Math.random() * 16).toString(16));
  const data = [{

    type: 'histogram2d',
    x: fcob_data[0].data.map(Math.log10),
    y: fcob_data[1].data.map(Math.log10),

    autobinx:false,
    autobiny:false,

    xbins:{
        size:0.02
    },
    ybins:{
        size:0.02
    },

  /*  marker: {

        size: "default",


        line: {

            width: 0

        }

    },*/

    name: 'histogram2d',
    colorscale: [['0', 'rgb(255,255,255)'], ['0.25', 'rgb(10,136,186)'], ['0.5', 'rgb(242,211,56)'], ['0.75', 'rgb(242,143,56)'], ['1', 'rgb(217,30,30)']],


   

}];
  const layout = {
    xaxis: {

        type: "linear" as AxisType ,
    
        
        
      },
    
      yaxis: {
    
        type: "linear" as AxisType,
       
        
    
      },
    width: 900,
    height: 600,
    shapes:[ {
        
        type: 'line' as Partial<Shape["type"]>,
        x0: Math.max(Math.min(...fcob_data[0].data.map(Math.log10)),Math.min(...fcob_data[1].data.map(Math.log10))),
  
        y0: Math.max(Math.min(...fcob_data[0].data.map(Math.log10)),Math.min(...fcob_data[1].data.map(Math.log10))),
  
        x1: Math.min(Math.max(...fcob_data[0].data.map(Math.log10)),Math.max(...fcob_data[1].data.map(Math.log10))),
  
        y1:Math.min(Math.max(...fcob_data[0].data.map(Math.log10)),Math.max(...fcob_data[1].data.map(Math.log10))),
  
        line: {
  
          color: 'rgba(0, 0, 0, 0.3)',
  
          width: 3,
          dash: 'dashdot' as Dash
  
        }
  
      }],

    title:"log base 10"
} ;
  return <div id={plot_div_id} />;
}

