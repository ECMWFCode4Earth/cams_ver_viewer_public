"use client";
import { bodyDataMenu } from "@/app/lib/custom types/bodydata";
import Plotly, { Data } from "plotly.js-dist";
import { useEffect } from "react";
export default function SimPlot({
  plotData,
  data,
  i
}: {
  plotData: bodyDataMenu;
  data: Data[];
  i: number;
}) {
  useEffect(() => {
    Plotly.newPlot(plot_div_id, data, layout);
  },);
  let plot_div_id = "plot_div_" + i;

  const layout = {
    /*selections: [
      {
        line: {
          color:,
        },
      },
    ],*/
    width: 800,
    height: 600,
    autosize: true,
    title: ` [${
      plotData.parameter.name
    }] from Models [${plotData.models.map((e)=>e.name
    )}] <br> with Axes [${
      plotData.axes.map((e)=>e.name)
    }] from <br> [${plotData.dates.startDate?.name}] to [${
      plotData.dates.endDate?.name
    }] <br> with index [${
      plotData.index.name
    }] \n location: [${plotData.site_list===null? "": plotData.site_list}]`,
    xaxis: { title: `${plotData.index.name}` },
    yaxis: { title: `${plotData.parameter.name} ` },
  };
  return <div id={plot_div_id} />;
}

function writemodels(item: any) {
  return item.name;
}
