import React from "react";
import PropTypes from "prop-types";
import { i18next } from "@translations/i18next";
import { getGeometryAsGeoJSONObject } from "../locations_geometry";
import LocationsList from "./LocationsList";
import LocationsMap from "./LocationsMap";
import ErrorMessage from "./ErrorMessage";

function Locations(props) {
  const locationsAsString = props.locations;
  if (!locationsAsString) {
    return (
      <ErrorMessage message={i18next.t("No valid locations were found!")} />
    );
  }

  let locations;
  try {
    locations = JSON.parse(locationsAsString);
  } catch (err) {
    console.error("Failed to parse locations JSON:", err);
    return (
      <ErrorMessage message={i18next.t("No valid locations were found!")} />
    );
  }

  if (locations.length === 0) {
    return <ErrorMessage message={i18next.t("No locations were found!")} />;
  }

  const locationEntries = locations
    .map((location) => {
      if (!location.geometry) {
        console.warn(
          `Skipping location because it does not contain any geometry!`,
        );
        return null;
      }

      const geometry = getGeometryAsGeoJSONObject(location);

      if (!geometry) {
        console.warn(
          `Skipping location because it contains unknown type of geometry!`,
        );
        return null;
      }

      return { id: crypto.randomUUID(), location, geometry };
    })
    .filter(Boolean);

  return (
    <>
      <LocationsMap
        locationEntries={locationEntries.sort((a, b) => {
          const aIsPoint = a.geometry.type === "Point";
          const bIsPoint = b.geometry.type === "Point";

          // Sort locations so 'Point' based location's layers are rendered as the last ones.
          if (aIsPoint && !bIsPoint) return 1;
          if (!aIsPoint && bIsPoint) return -1;

          return 0;
        })}
      />
      <LocationsList locationEntries={locationEntries} />
    </>
  );
}

Locations.propTypes = {
  locations: PropTypes.string,
};

export default Locations;
