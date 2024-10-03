import { autocompleteClasses, Box } from "@mui/material";
import { alpha, createTheme } from "@mui/material/styles";

export const menuTheme = (theme: any) =>
  createTheme({
    ...theme,
    components: {
      MuiAutocomplete: {
        defaultProps: {
          renderOption: (props, option, state, ownerState) => {
            const { key, ...optionProps } = props;
            return (
              <Box
                key={key}
                sx={{
                  borderRadius: "8px",
                  margin: "5px",
                  [`&.${autocompleteClasses.option}`]: {
                    padding: "8px",
                  },
                }}
                component="li"
                {...optionProps}
              >
                {ownerState.getOptionLabel(option)}
              </Box>
            );
          },
        },
      },
      MuiDateCalendar: {
        styleOverrides: {
          root: {
            //color: "#f8bbd0",
            borderRadius: "1px",
            borderWidth: "2px",
            borderColor: "#2a69a2",
            border: "1px solid",
            // backgroundColor: "#880e4f",
          },
        },
      },
      MuiSlider: {
        styleOverrides: {
          root: { color: "#acbbd7" },
        },
      },
      MuiFormControl: {
        styleOverrides: {
          root: {
            borderRadius: "3px",
          },
        },
      },
      MuiSwitch: {
        styleOverrides: {
          root: {
            "& .MuiSwitch-switchBase.Mui-checked": {
              color: "#acbbd7",
              "&:hover": {
                backgroundColor: alpha("#acbbd7", 0.25),
              },
            },
            "& .MuiSwitch-switchBase.Mui-checked + .MuiSwitch-track": {
              backgroundColor: "#acbbd7",
            },
          },
        },
      },
      MuiFormControlLabel: {
        styleOverrides: {
          root: {
            color: "white",
            textShadow: "1px 1px 5px brown",
          },
        },
      },
      MuiRadio: {
        styleOverrides: {
          root: {
            color: "#acbbd7",
            "&.Mui-checked": {
              color: "#acbbd7",
            },
          },
        },
      },
      MuiButton: {
        styleOverrides: {
          root: {
            color: "#000",
            backgroundColor: "#acbbd7",
            "&:hover": {
              backgroundColor: "#acbbd7",
            },
          },
        },
      },
      /*MuiSelect: {
        styleOverrides: {
          outlined: {
            margin: "-10px",
            padding: "20px",
            backgroundColor: "white",
          },
        },
      },*/
    },
  });
