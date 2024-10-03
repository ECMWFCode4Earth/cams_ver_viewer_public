"use client";
import Plotly, { Data } from "plotly.js-dist";
import { useEffect } from "react";
export default function NewPlot({
  plotData,
  graphData,
  i,
  a,
  y,
}: {
  plotData: any;
  graphData: any;
  i: number;
  a: number;
  y: number[];
}) {
  useEffect(() => {
    Plotly.newPlot(plot_div_id, data, layout);
  });
  let plot_div_id = "plot_div_" + i;

  const data: Data[] = [
    {
      connectgaps: false,
      x: graphData.valid_time,
      y: y,
      type: "scatter",
      mode: "lines+markers",
      line: {
        color: "blue",

        width: 2,
      },
    },
    //{ type: "scatter", x: [1, 2, 3], y: [2, 5, 3] },
  ];
  const layout = {
    selections: [
      {
        line: {
          color: "blue",
        },
      },
    ],
    width: 800,
    height: 600,
    autosize: true,
    title: ` [${
      plotData.dataset_selection.parameter[0]
    }] from Model [${Object.values(
      plotData.dataset_selection.models[a]
    )}] <br> with Method [${
      plotData.processing_selection.score_type
    }] from <br> [${plotData.dataset_selection.dates_for_months[0]}] to [${
      plotData.dataset_selection.dates_for_months[1]
    }] <br> as a function of [${
      plotData.processing_selection.request_type.axis_names
    }]`,
    xaxis: { title: plotData.processing_selection.request_type.axis_names },
    yaxis: { title: `${plotData.dataset_selection.parameter[a]} rate` },
  };
  return <div id={plot_div_id} />;
}
