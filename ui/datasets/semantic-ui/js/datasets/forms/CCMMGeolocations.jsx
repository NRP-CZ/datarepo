import React from "react";
import { i18next } from "@translations/ccmm_invenio";
import Overridable from "react-overridable";
import { buildUID } from "react-searchkit";
import { GeolocationsInputField } from "./components/GeolocationsInputField";

export const CCMMGeolocations = {
  key: "geolocations",
  label: i18next.t("Geolocations"),

  component: (tabConfig) => {
    const { record, formConfig } = tabConfig;
    const { overridableIdPrefix } = formConfig;

    return (
      <Overridable
        id={buildUID(overridableIdPrefix, "Geolocations")}
        {...tabConfig}
      >
        <GeolocationsInputField
          fieldPath="metadata.locations"
          label={i18next.t("Geolocations")}
          icon="map marker alternate"
          relatedResourceUI={record.ui?.locations}
        />
      </Overridable>
    );
  },

  includesPaths: ["metadata.locations"],
};
