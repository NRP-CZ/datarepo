import React from "react";
import Overridable from "react-overridable";
import { buildUID } from "react-searchkit";
import { i18next } from "@translations/i18next";
import { GeolocationsInputField } from "./components/GeolocationsInputField";

export const CCMMGeolocations = {
  key: "geolocations",
  label: i18next.t("Geolocations"),

  component: (tabConfig) => {
    const { record, formConfig } = tabConfig;
    const { overridableIdPrefix } = formConfig;
    const { vocabularies } = formConfig.config;

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
          vocabularies={vocabularies}
        />
      </Overridable>
    );
  },

  includesPaths: ["metadata.locations"],
};
