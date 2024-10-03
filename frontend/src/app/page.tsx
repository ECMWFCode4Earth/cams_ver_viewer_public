import Menu from "@/app/ui/menu/menu";
import AllPlots from "@/app/plot/allplots";
import { getStartingData } from "@/app/lib/fetchstartingdata";
import { startingdata } from "./lib/custom types/startingdata";
import React from "react";
import { Client } from "./client/client";

export default async function Home({
  searchParams,
}: {
  searchParams?: {
    [key: string]: string | string[] | number | undefined;
    NoP: number;
  };
}) {
  const bodydata = PlotJsons(searchParams);
  const startingData: startingdata | string = await getStartingData();
  if (typeof startingData == "string") {
    return <p>{startingData} </p>;
  }
  return (
    <>
      <main className="flex min-h-screen flex-col items-center justify-between p-24">
       <Client startingData={startingData} searchParams={searchParams} />
      </main>
    </>
  );
}
function PlotJsons(
  searchParams:
    | {
        [key: string]: string | string[] | number | undefined;
        NoP: number;
      }
    | undefined
) {
  if (searchParams === undefined) {
    return undefined;
  } else {
    const bodydata = JSON.parse(
      `{${JSON.stringify(searchParams)
        .split(`,"|":[${`'',`.repeat(searchParams.NoP - 1).slice(0, -1)}],`)[0]
        .replace("{", "")
        .replace("}", "")}}`
    );

    return bodydata;
  }
}
