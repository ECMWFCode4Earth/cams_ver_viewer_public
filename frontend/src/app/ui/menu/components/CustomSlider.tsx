import { sliderdata } from "@/app/lib/custom types/sliderdata";
import { FormLabel, Slider } from "@mui/material";
export function CustomSlider({
  onChange,
  value,
  label,
  sliderdata,
  marks
}: {
  onChange: ((event: Event, newValue: number | number[], activeThumb:number) => void) | undefined;
  value: number | number[];
  label: string;
  sliderdata: sliderdata;
  marks?: boolean;
}) {
  return (
    <>
      <FormLabel
        id="demo-radio-buttons-group-label"
        sx={{ color: "white", textShadow: "1px 1px 5px brown" }}
      >
        {label}
      </FormLabel>
      <Slider
        marks={marks}
        defaultValue={sliderdata.default_val}
        max={sliderdata.max}
        min={sliderdata.min}
        step={sliderdata.step}
        aria-labelledby="pre-averaging"
        valueLabelDisplay="auto"
        value={value}
        onChange={onChange}
      />
    </>
  );
}
