import { DepositFormApp, parseFormAppConfig } from "@js/oarepo_ui/forms";
import React from "react";
import ReactDOM from "react-dom";
import FormFieldsContainer from "./FormFieldsContainer";
import { EDTFSingleDatePicker } from "@js/oarepo_ui/forms";
import { parametrize } from "react-overridable";

const { rootEl, config, ...rest } = parseFormAppConfig();

const overridableIdPrefix = config.overridableIdPrefix;

const parametrizeEDTFSingleDatePicker = parametrize(EDTFSingleDatePicker, {
  customInputProps: { width: 16 },
});

export const componentOverrides = {
  [`${overridableIdPrefix}.FormFields.container`]: FormFieldsContainer,
  "InvenioRdmRecords.DepositForm.DatesField.DateField":
    parametrizeEDTFSingleDatePicker,
};

ReactDOM.render(
  <DepositFormApp
    config={config}
    {...rest}
    componentOverrides={componentOverrides}
  />,
  rootEl,
);
