import { DepositFormApp, parseFormAppConfig } from "@js/oarepo_ui/forms";
import React from "react";
import ReactDOM from "react-dom";
import { EDTFSingleDatePicker } from "@js/oarepo_ui/forms";
import { parametrize } from "react-overridable";
import {
  CCMMDepositRecordSerializer,
  CCMMSections,
} from "@js/ccmm_invenio/forms";

const { rootEl, config, ...rest } = parseFormAppConfig();
const recordSerializer = new CCMMDepositRecordSerializer(
  config.default_locale,
  config.custom_fields.vocabularies,
);

const parametrizeEDTFSingleDatePicker = parametrize(EDTFSingleDatePicker, {
  customInputProps: { width: 16 },
});

export const componentOverrides = {
  "InvenioRdmRecords.DepositForm.DatesField.DateField":
    parametrizeEDTFSingleDatePicker,
};

ReactDOM.render(
  <DepositFormApp
    config={config}
    {...rest}
    sections={CCMMSections}
    recordSerializer={recordSerializer}
    componentOverrides={componentOverrides}
    useWizardForm
  />,
  rootEl,
);
