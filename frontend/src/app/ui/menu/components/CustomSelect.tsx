import {
  Box,
  FormControl,
  InputLabel,
  MenuItem,
  MenuItemClasses,
  Select,
  SelectChangeEvent,
} from "@mui/material";
import {
  ReactNode,
  ReactElement,
  JSXElementConstructor,
  ReactPortal,
  AwaitedReactNode,
} from "react";
export function CustomSelect({
  onChange,
  options,
  value,
  label,
  multiple,
  extraOption,
}: {
  onChange:
    | ((event: SelectChangeEvent<any>, child?: ReactNode) => void)
    | undefined;
  options:ReactNode
  value:string | string[]|null;
  label: string;
  multiple?: boolean;
  extraOption?:ReactNode;
}) {
  return (
    <FormControl sx={{ m: 1, minWidth: 1 }}>
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
        <InputLabel id="demo-simple-select-">{label}</InputLabel>
        <Select
          multiple={multiple}
          sx={{ minWidth: 175, maxWidth: 200 }}
          labelId="demo-simple-select-"
          id="demo-simple-"
          value={value}
          label="observation_source"
          onChange={onChange}
        >
          {extraOption}
          {options}
        </Select>
      </Box>
    </FormControl>
  );
}
