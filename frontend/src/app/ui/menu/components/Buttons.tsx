import { Box, Button, ButtonGroup, Select, SelectChangeEvent, } from "@mui/material";
import React, { AwaitedReactNode, Dispatch, JSXElementConstructor, ReactElement, ReactNode, ReactPortal, SetStateAction } from "react";
export function CustomButtonGroup({
  onClick1,
  label1,
  onClick2,
  label2,
  disabled2,
  onClick3,
  label3,
  options,
  selectedPlot,
  setSelectedPlot,
}: {
    onClick1: (e: React.MouseEvent<HTMLButtonElement>) => void;
    label1: string;
    onClick2: (e: React.MouseEvent<HTMLButtonElement>) => void;
    label2: string;
    disabled2: boolean;
    onClick3: (e: React.MouseEvent<HTMLButtonElement>) => void;
    label3: any;
    options:
    string
    | number
    | bigint
    | boolean
    | ReactElement<any, string | JSXElementConstructor<any>>
    | Iterable<ReactNode>
    | ReactPortal
    | Promise<AwaitedReactNode>
    | null
    | undefined;
    selectedPlot: string;
    setSelectedPlot: Dispatch<SetStateAction<string>>;
}) {
  return (
    
      <Box>
              <ButtonGroup>
                <Button variant="contained" onClick={onClick1}>
                  {label1}
                </Button>
                <Button disabled={disabled2} variant="contained" onClick={onClick2}>
                
                  {label2}
                </Button>
                
                <Button variant="contained" onClick={onClick3}>
                  {label3} 
                 
                </Button>
                <Box boxShadow={"0px 0px 5px #acbbd7 inset "}
        sx={{
          minWidth: 0, maxWidth: 40,
          padding: "5px", 
          bgcolor: "#acbbd7",
          borderRadius: "5px",
          borderTopLeftRadius: 0,
          borderBottomLeftRadius: 0,
        }} >
            <Select
          sx={{ minWidth: 0, maxWidth: 30 }}
          labelId="demo-simple-select-"
          id="demo-simple-"
          value={selectedPlot}
          label="observation_source"
          onChange={(e: SelectChangeEvent)=>{setSelectedPlot(e.target.value as string)}}
        >
          {options}
        </Select>
        </Box>
              </ButtonGroup>
            </Box>
    
  );
}
