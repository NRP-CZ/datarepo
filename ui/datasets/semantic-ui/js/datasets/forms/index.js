import { DepositFormApp, parseFormAppConfig } from "@js/oarepo_ui/forms";
import React from "react";
import ReactDOM from "react-dom";
import FormFieldsContainer from "./FormFieldsContainer";
import { EDTFSingleDatePicker } from "@js/oarepo_ui/forms";
import { parametrize } from "react-overridable";

import { SchemaField } from "@js/invenio_rdm_records/src/deposit/serializers";
import { RDMDepositRecordSerializer } from "@js/invenio_rdm_records/src/deposit/api/DepositRecordSerializer";
import { RelatedResourceSchema } from "./RelatedResourceField/RelatedResourceSchema";

class CCMMDepositRecordSerializer extends RDMDepositRecordSerializer {
  get depositRecordSchema() {
    return {
      ...super.depositRecordSchema,
      related_resources: new SchemaField({
        fieldpath: "metadata.related_resources",
        schema: RelatedResourceSchema,
      }),
    };
  }
}

const { rootEl, config, ...rest } = parseFormAppConfig();
const recordSerializer = new CCMMDepositRecordSerializer(
  config.default_locale,
  config.custom_fields.vocabularies,
);
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
    recordSerializer={recordSerializer}
    componentOverrides={componentOverrides}
  />,
  rootEl,
);
