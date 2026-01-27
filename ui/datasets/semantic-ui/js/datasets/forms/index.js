import { DepositFormApp, parseFormAppConfig } from "@js/oarepo_ui/forms";
import React from "react";
import ReactDOM from "react-dom";
import { OARepoDepositSerializer } from "@js/oarepo_ui/api";
import FormFieldsContainer from "./FormFieldsContainer";
import FormActionsContainer from "./FormActionsContainer";

const recordSerializer = new OARepoDepositSerializer(
  ["errors", "expanded"],
  ["__key"]
);

const { rootEl, config, ...rest } = parseFormAppConfig();

const overridableIdPrefix = config.overridableIdPrefix;

export const componentOverrides = {
  [`${overridableIdPrefix}.FormFields.container`]: FormFieldsContainer,
  [`${overridableIdPrefix}.FormActions.container`]: FormActionsContainer,
};

ReactDOM.render(
  <DepositFormApp
    config={config}
    {...rest}
    // recordSerializer={recordSerializer}
    componentOverrides={componentOverrides}
  />,
  rootEl
);
