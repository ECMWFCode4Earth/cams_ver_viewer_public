import { availability, availableSelectionsType } from "./custom types/availability";

export async function getAvailability(availabilitydata: availability) {
    try {
      const response = await fetch("http://127.0.0.1:8000/get-available-dataset-combination-values", {
        method: "POST",
        headers: {
          "Content-Type": "application/json",
        },
        body: JSON.stringify(availabilitydata) /*,
          //let cache expire after 1 hour
          next: { revalidate: 3600 },*/,
      });
      const data: availableSelectionsType = await response.json();
      return data;
    } catch (error) {
      return { message: "Something went wrong." };
    }
  }
  