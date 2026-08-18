import React from "react";
import ReactDOM from "react-dom";
import { GetAccessButton } from "@js/oarepo_requests/get_access";
import { i18next } from "@translations/i18next";

const domContainer = document.getElementById("standalone_submitter_application");
if (domContainer) {
  ReactDOM.render(
    <GetAccessButton groupId="submitters" groupName={i18next.t("Submitters")} />,
    domContainer
  );
}
