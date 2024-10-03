import { fetchModelandSite } from "./custom types/modelandsite";

export async function getDateandSite(fetchingdata: fetchModelandSite) {
    try {
      const response = await fetch("http://127.0.0.1:8000/get-available-model-dates-and-sites", {
        method: "POST",
        headers: {
          "Content-Type": "application/json",
        },
        body: JSON.stringify(fetchingdata) /*,
          //let cache expire after 1 hour
          next: { revalidate: 3600 },*/,
      });
      const data= await response.json();
      return data;
    } catch (error) {
      return { message: "Something went wrong." };
    }
  }
  