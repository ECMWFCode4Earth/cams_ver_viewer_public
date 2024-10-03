"use client";
import {Box,FormControl,FormControlLabel,FormHelperText,Grid,MenuItem,Radio,SelectChangeEvent,Slider,Stack,Switch,TextField,ThemeProvider,} from "@mui/material";
import React, { Dispatch, SetStateAction, useEffect } from "react";
import { metadata, model_dict,  nameString,  startingdata } from "@/app/lib/custom types/startingdata";
import { CustomSelect } from "./components/CustomSelect";
import { CustomSlider } from "./components/CustomSlider";
import { CustomRadio } from "./components/CustomRadio";
import { CustomAutoComplete } from "./components/CustomAutoComplete";
import { menuTheme } from "../theme";
import { bodyDataMenu } from "@/app/lib/custom types/bodydata";
import dayjs from "dayjs";
import { CustomButtonGroup } from "./components/Buttons";
import { getAvailability } from "@/app/lib/fetchavailability";
import { availability } from "@/app/lib/custom types/availability";
import { getValueFromKeyValPair } from "@/app/lib/util/getValueFromKeyValPair";
import { getSmallestMaxLead } from "@/app/lib/util/getsmallestmaxlead";
import { isAvailableSelections } from "@/app/lib/util/isAvailableSelections";
import {ConsistentDimensionsExistingAcross} from "./components/ConsistentDimensionsEA"
export default function Menu({
  startingData,
  bodyData,
  setBodyData,
}: {
  startingData: startingdata;
  bodyData: (bodyDataMenu|{})[];
  setBodyData: Dispatch<SetStateAction<(bodyDataMenu|{})[]>>
}) {
// selectable lists
  const [selectableMonthList,setSelectableMonthList] = React.useState(getValueFromKeyValPair(startingData.dataset.month_dict));
  const [selectableParameterList, setSelectableParameterList]= React.useState<nameString[]>(getValueFromKeyValPair(startingData.dataset.parameter_dict));
 const [selectableObservationSourceNameList, setSelectableObservationSourceNameList]= React.useState(Object.entries(startingData.dataset.observation_source_dict).map(([key, value], index)=> optionsItemSelect(value, index)));
 const [selectableModelList, setSelectableModelList]= React.useState<model_dict[]>(getValueFromKeyValPair(startingData.dataset.space_model_dict))

  const [model, setModel] = React.useState<string[]>([]);
  const [showFcObPairs, setSetShowFcObPairs] = React.useState(false);
  const [selectedPlot, setSelectedPlot]= React.useState("0")

  const [matchModels, setMatchModels] = React.useState<number|number[]>(1);
  const [consistentDimensions, setConsistentDimensions]= React.useState<nameString[]>([])
  let preavg = { default_val: 3, min: 3, max: 24, step: 3 };
  const [selectableLeadTime, setSelectableLeadTime] = React.useState<{default_val: number, min:number,max:number,step:number}>({ default_val: 0, min: 0, max: getSmallestMaxLead(getValueFromKeyValPair(startingData.dataset.space_model_dict))+1, step: 1 });
  const [preAveraging, setPreAveraging] = React.useState<number>(1);
  const [obSrc, setObSrc] = React.useState<string>("");
  const [startDate, setStartDate] = React.useState<{name: string} | null>(null);

  //const [startDateDay, setStartDateDay] = React.useState<Dayjs | null>();
  const [endDate, setEndDate] = React.useState<{name: string} | null>(null);
  //const [endDateDay, setEndDateDay] = React.useState<Dayjs | null>();
  //endDateParam
  const [showFCOBpairsas, setShowFCOBpairsas] = React.useState<string>(
    "2d_histogram"
    //asAFunctionOfParam
  );
  const showFCOBpairsasoptions: nameString[] =[{name:"2d_histogram"}]
  const [parameter, setParameter] = React.useState<string>("");

  const [selectedLeadTime, setSelectedLeadTime] = React.useState<number[]>([
    selectableLeadTime.min,
    selectableLeadTime.max,
  ]);

  /*const [plotType, setPlotType] = React.useState(
   startingData.plot_type.default_val
  );*/
  const [indexes, setIndexes] = React.useState<string>(
    startingData.processing.index_list[0].name
  );
  const axesArray = startingData.processing.comparative_axis_list.concat(startingData.processing.singular_axis_list)
  const [axes, setAxes]= React.useState<string[]>([axesArray[0].name])
 
  const [availabilityData, setAvailabilityData]= React.useState<availability>(
    
    {
      observation_source: null,
      parameter: null,
      space_model_list: null
    }
    

  )
  const [existingAcross, setExistingAcross]= React.useState<{name:string, existingAcross:number}[]>([{name:startingData.processing.consistent_dimension_list[0].name, existingAcross:0}])
 /*const [modelandSiteData, setModelandSiteData]= React.useState<fetchModelandSite>({
    
    space_model_dataset_selection: {
      base_model_dataset_selection: {
        month_selection: {
          month_range: [null,null],
          month_list: null
        },
        observation_source_without_site_list: {
          name: null,
          metadata: null
        },
        parameter: null,
        space_model_list: [
          {
            name: null,
            base_name: null,
            base_hour_name_list:null,
            max_lead_hour_int: null,
            step_hour_int: null,
            metadata: null
          }
        ]
      },
      pre_processing_selection: {
        match_models_selection: {
          tolerance_float: null
        },
        consistent_across_selection: {
          dimension_name: null,
          tolerance_float: null
        }
      }
    }
  

})*/

 /* useEffect( ()=>{
    const fetchMnSData = async(modelandSiteData: fetchModelandSite)=> {
        const availableSelections = await fet(availabilityData)
         if(isAvailableSelections(availableSelections)){
         
      setSelectableMonthList(availableSelections.month_list)
      setSelectableParameterList(availableSelections.parameter_list)
      setSelectableObservationSourceNameList(availableSelections.observation_source_name_list.map(optionsSelect))
      setSelectableModelList(availableSelections.space_model_list)
     }
      }
      fetchMnSData(modelandSiteData)
    }, [availabilityData])*/
 
 /*useEffect( ()=>{
 const fetchAvalData = async(availabilityData: availability)=> { //THE DATA SENT FROM THE BACKEND MUST HAVE THE SAME FORMATTING AS STARTINGDATA
     const availableSelections = await getAvailability(availabilityData)
     console.log(availabilityData)
      console.log(availableSelections)
      console.log(isAvailableSelections(availableSelections))
      if(isAvailableSelections(availableSelections)){
      
   setSelectableMonthList(availableSelections.response.month_list)
   setSelectableParameterList(availableSelections.response.parameter_list)
   setSelectableObservationSourceNameList(availableSelections.response.observation_source_without_site_list.map(optionsItemSelect))
   setSelectableModelList(availableSelections.response.space_model_list)
  }
   }
   fetchAvalData(availabilityData)
   console.log()
 }, [availabilityData])*/
  return (
    <>
      <ThemeProvider theme={menuTheme}>
        <FormControl>
          <Box
            sx={{
              backgroundColor: "#2a69a2",
              boxShadow: "10px 10px 5px #bababa ",
              padding: "12px",
              paddingRight: "36px",
              borderRadius: 3,
            }}
          >
            <Grid container>
              <Grid item sm={3.5}>
                <CustomSelect
                  onChange={handleChangeObservationSource}
                  options={selectableObservationSourceNameList}
                  extraOption={<MenuItem value="">
                    <em>None</em>
                  </MenuItem>}
                  value={obSrc}
                  label="Obs Source"
                />
              </Grid>
              <Grid item sm={0.75} />
              <Grid item sm={3.5}>
                <CustomSelect
                  onChange={handleChangeModel}
                  options={selectableModelList.map(optionsItemSelect)}
                  value={model}
                  label="Model"
                  multiple={true}
                />
              </Grid>
              <Grid item sm={0.75} />
              <Grid item sm={3.5}>
                <CustomSelect
                  onChange={handleChangeParameter}
                  options={selectableParameterList.map(optionsItemSelect)}
                  extraOption={<MenuItem value="">
                    <em>None</em>
                  </MenuItem>}
                  value={parameter}
                  label="Parameters"
                  multiple={false}
                />
              </Grid>
            </Grid>
              <Grid container>
                <Grid item sm={3.5} sx={{ marginLeft: 1 }}>
                  <CustomAutoComplete
                    boxSx={{
                      padding: "5px",
                      paddingRight: 22.5,
                      bgcolor: "white",
                      borderRadius: "5px",
                    }}
                    label="Start Month"
                    value={startDate}
                    onChange={(event: any, newValue: nameString[]|{name: string} | null) => {
                      setStartDate(Array.isArray(newValue)? newValue[0]: newValue )
                    }}
                    options={selectableMonthList}
                  />
                </Grid>
                <Grid item sm={4.8} />
                <Grid
                  item
                  sm={3.5}
                  sx={{ marginLeft: 54.5, position: "absolute" }}
                >
                  <CustomAutoComplete
                    boxSx={{
                      padding: "5px",
                      paddingRight: 0.5,
                      bgcolor: "white",
                      borderRadius: "5px",
                    }}
                    onChange={(event: any, newValue:nameString[]| nameString | null) => {
                      setEndDate(Array.isArray(newValue)? newValue[0]: newValue)}}
                    label="End Month"
                    value={endDate}
                    options={selectableMonthList}
                  />
                </Grid>
              </Grid>

            <Grid container>
              <Grid item sm={3}>
                <FormControl sx={{ paddingLeft: 3, minWidth: 1 }}>
                  <Box>
                  <Box
        boxShadow={"0px 0px 15px #2a69a2 inset "}
        display={"-ms-flexbox"}
        justifyContent={"stretch"}
        sx={{
          padding: "5px",
          bgcolor: "white",
          borderRadius: "5px",
        }}
      >
                    <TextField id="preaveraging" label="Pre Averaging:" value={preAveraging} onChange={handleChangePreAveraging}/>
                    </Box>     
                    <FormHelperText> Enter a number greater than or equal to 1 </FormHelperText>
                                  <CustomSlider
                    marks={true}
                      onChange={handleChangeLeadTime}
                      value={selectedLeadTime}
                      sliderdata={selectableLeadTime}
                      label="Lead Time:"
                    />
                  </Box>
                </FormControl>
              </Grid>

              <Grid item sm={2.25} />
              <Grid item sm={2.25}>
                    <Stack>
                    <CustomSlider
                    marks={true}
                    onChange={(e:Event,newValue: number|number[])=>setMatchModels(newValue)}
                    value={matchModels}
                    sliderdata={{default_val:0, min:0, max:100, step:1}}
                    label="Match Models tolerance %"
                    />


                   
                  </Stack>  
              </Grid>
              <Grid item sm={1.5} />
              <Grid item sm={3}>
                <Stack>
                <CustomRadio
                  sx={{ color: "white", textShadow: "1px 1px 5px brown" }}
                  onChange={handleChangeIndexes}
                  value={indexes}
                  label="Indexes"
                  options={startingData.processing.index_list.map((e) => optionsRadio(e.name))}
                />
                
                <Box sx={{alignSelf:"center"}}>
                  <CustomSelect
                    multiple={true}
                    onChange={handleChangeAxes}
                    value={axes}
                    label="Axes"
                    options={axesArray.map(optionsItemSelect)}
                  />
                </Box>
                </Stack>
              </Grid>
            </Grid>
            <Grid container sx={{ justify: "center", alignItems: "center" }}>
              <Grid
                item
                sm={4}
                sx={{ marginLeft: "auto", marginRight: "auto" }}
              >
               <CustomRadio disabled={!showFcObPairs} row={true} options={showFCOBpairsasoptions.map((e)=>optionsRadio(e.name))} value={showFCOBpairsas} onChange={handleChangeShowFCOBpairsas} label="Show FC-OB pairs as"/>
              </Grid>
              <Grid item sm={4}>
                <Stack>
                  <CustomAutoComplete filterSelectedOptions={true} multiple={true} boxSx={{padding: "5px",paddingRight: 0.5,bgcolor: "white",borderRadius: "5px",}} label="Consistent Dimensions" onChange={handleChangeConsistentDimensions} value={consistentDimensions} options={startingData.processing.consistent_dimension_list}/>
                 {<ConsistentDimensionsExistingAcross consistentDimensions={consistentDimensions} dimension={existingAcross} setDimension={setExistingAcross}/> }
                </Stack>
              </Grid>
            </Grid>

            <FormControlLabel
              control={<Switch checked={showFcObPairs} onChange={handleChangeSimp} />}
              label="Show FC"
            />
            <CustomButtonGroup label1="Refresh" onClick1={handleClick} label2="Add Plot" onClick2={handleClickAddPlot} disabled2={(JSON.stringify(bodyData[0])==="{}")} label3={`update plot `} onClick3={handleChangePlotClick} selectedPlot={selectedPlot} setSelectedPlot={setSelectedPlot} options={[...Array(bodyData.length).keys()].map(optionsSelect)}/>
            
          </Box>
        </FormControl>
      </ThemeProvider>
    </>
  );
  
  function optionsSelect(item: string|number) {
    return <MenuItem key={item} value={item}>{`${item}`}</MenuItem>;
  }
  function optionsItemSelect(value: {
    name: string;
    sites?: {
      name: string;
      latitude: number;
      longitude: number;
    }[];
    max_lead_hour?: number;
    base_hours?: string[];
    step_hour?: number;
    metadata?:metadata;
  }, index:number) {
    if (value.metadata === undefined) {
      return optionsSelect(value.name);
    } else
      return (
        <MenuItem
          key={value.name}
          value={JSON.stringify(value)}
        >{`${value.metadata.alias_list[0].name}`}</MenuItem>
      );
  }
  function optionsRadio(item: string) {
    return (
      <FormControlLabel
        key={item}
        value={item}
        control={<Radio />}
        label={item}
      />
    );
  }



  function handleChangeObservationSource(event: SelectChangeEvent) {
    setObSrc(event.target.value as string);
    setAvailabilityData({
    observation_source: event.target.value as string === "" ? null: {
      name: JSON.parse(event.target.value as string).name,
      metadata: JSON.parse(event.target.value as string).metadata
    },
    parameter: availabilityData.parameter,
    space_model_list: availabilityData.space_model_list})
  }
  function handleChangeIndexes(event: React.ChangeEvent<HTMLInputElement>) {
    setIndexes((event.target as HTMLInputElement).value);
  }
  function handleChangeShowFCOBpairsas(event: React.ChangeEvent<HTMLInputElement>) {
    setIndexes((event.target as HTMLInputElement).value);
  }
  function handleChangeConsistentDimensions(event: any, newValue: nameString| nameString[] | null) {
    setConsistentDimensions(Array.isArray(newValue)?newValue: Array(0));
    setExistingAcross((Array.isArray(newValue)?newValue: [{name:""}] ).map((e,i)=>{return {name:e.name,existingAcross:0}}))
  }
  function handleChangeAxes(event: SelectChangeEvent<typeof axes>) {
    const {target: { value },} = event;
    setAxes(typeof value === "string" ? value.split(",") : value);
  }
   function handleChangeModel(event: SelectChangeEvent<typeof model>) {
    
    let {target: { value },} = event;
    value=typeof value === "string" ? value.split(",") : value
    setModel(value);// On autofill we get a stringified value.
    if (JSON.stringify(value) == "[]") {setSelectableLeadTime({default_val: selectableLeadTime.default_val, min:selectableLeadTime.min, max:getSmallestMaxLead(getValueFromKeyValPair(startingData.dataset.space_model_dict))+1, step:1})//not working
    
  }else{ setSelectableLeadTime({default_val: selectableLeadTime.default_val, min:selectableLeadTime.min, max:getSmallestMaxLead(getValueFromKeyValPair(value.map((e)=>JSON.parse(e)))), step:1})
    setAvailabilityData({
    observation_source: availabilityData.observation_source,
    parameter: availabilityData.parameter,
    space_model_list: value.map((item)=>JSON.parse(item))})}
  }
  function handleChangePreAveraging(event: React.ChangeEvent<HTMLInputElement>) {
    setPreAveraging(event.target.value as unknown as number);
  } 
  function handleChangeParameter(event: SelectChangeEvent<typeof parameter>) {
    setParameter(event.target.value as string);
    setAvailabilityData({
    observation_source: availabilityData.observation_source,
    parameter: event.target.value as string === "" ? null : {name: event.target.value as string},
    space_model_list: availabilityData.space_model_list})
  }
  function handleChangeSimp(event: React.ChangeEvent<HTMLInputElement>) {
    setSetShowFcObPairs(event.target.checked);
  }
  function handleChangeLeadTime(event: Event, newValue: number | number[], activeThumb: number,) {
    if (!Array.isArray(newValue)) {
      return;
    }
    const maxDistance =24 
    
    if (activeThumb === 0) {
      if(newValue[0]<selectedLeadTime[1]-maxDistance){
        setSelectedLeadTime([newValue[0], newValue[0]+maxDistance])
      }else{
      setSelectedLeadTime([Math.max(newValue[0], selectedLeadTime[1] - maxDistance), selectedLeadTime[1]]);}
    } else {
      if(selectedLeadTime[0]+maxDistance< newValue[1]){setSelectedLeadTime([newValue[1]-maxDistance,newValue[1]])}
      else{setSelectedLeadTime([selectedLeadTime[0], Math.min(newValue[1], selectedLeadTime[0] + maxDistance)]);}
    }
  }

  async function handleChangePlotClick() {
    if (obSrc === "" || model.length===0|| parameter ===""|| startDate===null||endDate===null|| preAveraging<1 || axes.length===0) {
      throw new Error("All fields must be filled accordingly");
    } else {
    const nextBodyData: (bodyDataMenu|{})[] = bodyData.map((item:bodyDataMenu|{}, i) => {
      console.log(i)
      if (i === Number(selectedPlot) ) { //Number constructor is used to make the if statement typesafe, would still work
        item={
          observationSource: obSrc,
          models:model.map((e)=>JSON.parse(e)),
          parameter: parameter === "" ? null : {name: parameter},
          dates:{
              startDate: startDate,
              endDate: endDate ,
          },
          preAveraging: preAveraging,
          leadTime:selectedLeadTime,
          matchModels:matchModels as number,
          ShowFCOBpairs: showFcObPairs,
          ShowFCOBpairsas: showFCOBpairsas,
          index: {name:indexes},
          axes: axes.map((e)=>{return {name: e}}),
          site_list:"all",
          existingAcross:existingAcross
       }
        return item;
      } else {
        // The rest haven't changed
        return item;
      }
    });
    setBodyData(nextBodyData);
  }}
    
  
  async function handleClickAddPlot() {
    if (obSrc === "" || model.length===0|| parameter ===""|| startDate===null||endDate===null|| preAveraging<1 || axes.length===0) {
      throw new Error("All fields must be filled accordingly");
    } else {
    setBodyData([...bodyData,{
      observationSource: obSrc,
      models:model.map((e)=>JSON.parse(e)),
      parameter: parameter === "" ? null : {name: parameter},
      dates:{
          startDate: startDate,
          endDate: endDate,
      },
      preAveraging: preAveraging,
      leadTime:selectedLeadTime,
      matchModels:matchModels as number,
      ShowFCOBpairs: showFcObPairs,
      ShowFCOBpairsas: showFCOBpairsas,
      index: {name:indexes},
      axes: axes.map((e)=>{return {name: e}}),
      site_list:"all",
      existingAcross:existingAcross
   }])

    
  }}
  async function handleClick() {
     if (obSrc === "" || model.length===0|| parameter ===""|| startDate===null||endDate===null|| preAveraging<1 || axes.length===0) {
      throw new Error("All fields must be filled accordingly");
    } else {
      console.log(existingAcross)
    setBodyData([{
      observationSource: obSrc,
      models:model.map((e)=>JSON.parse(e)),
      parameter:{name: parameter},
      dates:{
          startDate: startDate,
          endDate: endDate,
      },
      preAveraging: preAveraging,
      leadTime:selectedLeadTime,
      matchModels:matchModels as number,
      ShowFCOBpairs: showFcObPairs,
      ShowFCOBpairsas: showFCOBpairsas,
      index: {name:indexes},
      axes: axes.map((e)=>{return {name: e}}),
      site_list:"all",
      existingAcross:existingAcross

   }])
  }}
  //const formattedStartDate = await formatDate(startDate);
  //const formattedEndDate = await formatDate(endDate);

  async function formatDate(date: any) {
    const Year = dayjs(date).year();
    let Month: any = dayjs(date).month() + 1;
    if (Month < 10) {
      Month = "0" + Month;
    }

    /* let Day: any = dayjs(date).date();
    if (Day < 10) {
      Day = "0" + Day;
    }*/
    return `${Year}-${Month}` /*-${Day}*/;
  }

  
}



