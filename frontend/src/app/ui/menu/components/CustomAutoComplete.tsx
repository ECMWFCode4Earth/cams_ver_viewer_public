"use client";
import { nameString } from "@/app/lib/custom types/startingdata";
import {
  Autocomplete,
  AutocompleteChangeDetails,
  AutocompleteChangeReason,
  Box,
  FormControl,
  SxProps,
  TextField,
} from "@mui/material";
import React from "react";

export function CustomAutoComplete({
  options,
  onChange,
  value,
  filterSelectedOptions,
  label,
  boxSx,
  multiple,
}: {
  options: {
    name: string
  }[];
  onChange: (
    event: React.SyntheticEvent,
    newValue: nameString[]|nameString| null,
    reason: AutocompleteChangeReason,
    details?: AutocompleteChangeDetails<nameString>
  ) => void;
  value: nameString[]|nameString| null;
  filterSelectedOptions?:boolean;
  label: string;
  boxSx: SxProps;
  multiple?:boolean;
}) {

  
  const [inputValue, setInputValue] = React.useState("");
  return (
    <Box boxShadow={"0px 0px 15px #2a69a2 inset "} sx={boxSx}>
      <Autocomplete
      multiple={multiple}
      filterSelectedOptions={filterSelectedOptions}
        sx={{ minWidth: 175, maxWidth: 200 }}
        value={value}
        inputValue={inputValue}
        options={options}
        getOptionLabel={(option) => option.name}
        onChange={onChange}
        onInputChange={(event, newInputValue) => {
          setInputValue(newInputValue);
        }}
        renderInput={(params) => <TextField {...params} label={label} />}
      ></Autocomplete>
    </Box>
  );

}
