import { bodydata } from "./custom types/bodydata";
import { FCOB, graphdata } from "./custom types/graphdata";

export async function getModelPlottingData(bodydata: bodydata) {
  
    const response = await fetch("http://127.0.0.1:8000/get-model-plotting-data", {
      method: "POST",
      headers: {
        "Content-Type": "application/json",
      },
      body: JSON.stringify(bodydata) ,
        //let cache expire after 1 hour
       // next: { revalidate: 3600 },
    });
    const data: graphdata|FCOB = await response.json();
    return data;
  
}
