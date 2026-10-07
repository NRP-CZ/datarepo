import React from "react";
import ReactDOM from "react-dom";
import { i18next } from "@translations/i18next";
import { ErrorElement } from "@js/oarepo_ui/search";
import Locations from "./components/Locations";

function renderLocations() {
  const recordLocationsContainer = document.getElementById("record-locations");

  if (recordLocationsContainer) {
    const locations = JSON.parse(
      recordLocationsContainer.getAttribute("data-locations"),
    );

    if (!locations || !Array.isArray(locations)) {
      ReactDOM.render(
        <ErrorElement
          error={new Error(i18next.t("No valid locations were found!"))}
        />,
        recordLocationsContainer,
      );
      return;
    }

    if (locations.length <= 0) {
      ReactDOM.render(
        <ErrorElement
          error={new Error(i18next.t("No locations were found!"))}
        />,
        recordLocationsContainer,
      );
      return;
    }

    const locationEntries = locations
      .map((location) => {
        if (
          !location ||
          !location.geometry ||
          typeof location.geometry !== "object"
        ) {
          return null;
        }

        const geometry = location.geometry;
        return { id: crypto.randomUUID(), location, geometry };
      })
      .filter(Boolean);

    if (locationEntries.length <= 0) {
      ReactDOM.render(
        <ErrorElement
          error={new Error(i18next.t("No valid locations were found!"))}
        />,
        recordLocationsContainer,
      );
      return;
    }

    ReactDOM.render(
      <Locations locationEntries={locationEntries} />,
      recordLocationsContainer,
    );
  }
}

renderLocations();
