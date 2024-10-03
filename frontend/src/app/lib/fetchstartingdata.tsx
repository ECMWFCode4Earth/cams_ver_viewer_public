export async function getStartingData() {
  try {
    const response = await fetch("http://127.0.0.1:8000/get-starting-data", {
      method: "GET",
      //let cache expire after 1 hour
      next: { revalidate: 10 },
    });
    const data = await response.json();

    return data;
  } catch (error) {
    return { message: "Something went wrong." };
  }
}
