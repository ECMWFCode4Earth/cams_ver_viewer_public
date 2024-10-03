import {
  FormControl,
  FormLabel,
  RadioGroup,
  SxProps,
} from "@mui/material";
import {
  ReactNode,
  ReactElement,
  JSXElementConstructor,
  ReactPortal,
  AwaitedReactNode,
} from "react";
export function CustomRadio({
  onChange,
  options,
  value,
  label,
  row,
  sx,
  disabled
}: {
  onChange: ((event: React.ChangeEvent<HTMLInputElement>) => void) | undefined;
  options:
    | string
    | number
    | bigint
    | boolean
    | ReactElement<any, string | JSXElementConstructor<any>>
    | Iterable<ReactNode>
    | ReactPortal
    | Promise<AwaitedReactNode>
    | null
    | undefined;
  value: string | null;
  label: string;
  row?: boolean;
  sx?: SxProps;
  disabled?: boolean;
}) {
  return (
    <FormControl sx={sx} disabled={disabled}>
      
      <FormLabel id="demo-row-radio-buttons-group-label" sx={sx}>
        {label}
      </FormLabel>

      <RadioGroup
        
        row={row}
        aria-labelledby="demo-row-radio-buttons-group-label"
        name="row-radio-buttons-group"
        value={value}
        onChange={onChange}
      >
        {options}
      </RadioGroup>
    </FormControl>
  );
}
