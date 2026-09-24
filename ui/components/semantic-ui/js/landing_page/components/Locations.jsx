import React, { useState, useRef, useMemo } from "react";
import PropTypes from "prop-types";
import { i18next } from "@translations/i18next";
import { getGeometryAsGeoJSONObject } from "../locations_geometry";
import LocationsList from "./LocationsList";
import LocationsMap from "./LocationsMap";
import ErrorMessage from "./ErrorMessage";

function Locations(props) {
  const locationEntries = useMemo(() => {
    const locationsAsString = props.locations;
    if (!locationsAsString) return null;

    let parsedLocations;
    try {
      parsedLocations = JSON.parse(locationsAsString);
    } catch (err) {
      console.error("Failed to parse locations JSON:", err);
      return null;
    }

    if (parsedLocations.length === 0) return [];

    return parsedLocations
      .map((location) => {
        if (!location.geometry) return null;
        const geometry = getGeometryAsGeoJSONObject(location);
        if (!geometry) return null;

        return { id: crypto.randomUUID(), location, geometry };
      })
      .filter(Boolean);
  }, [props.locations]);

  const sortedLocationEntries = useMemo(() => {
    return [...locationEntries].sort((a, b) => {
      const aIsPoint = a.geometry.type === "Point";
      const bIsPoint = b.geometry.type === "Point";
      if (aIsPoint && !bIsPoint) return 1;
      if (!aIsPoint && bIsPoint) return -1;
      return 0;
    });
  }, [locationEntries]);

  const layersManagerRef = useRef({});
  const [activeLocationId, setActiveLocationId] = useState(null);
  const [flyToId, setFlyToId] = useState(null);

  if (locationEntries === null) {
    return (
      <ErrorMessage message={i18next.t("No valid locations were found!")} />
    );
  }
  if (locationEntries.length === 0) {
    return <ErrorMessage message={i18next.t("No locations were found!")} />;
  }

  return (
    <>
      <LocationsMap
        locationEntries={sortedLocationEntries}
        layersManager={layersManagerRef.current}
        flyToId={flyToId}
        onLocationsClick={(locationData) => {
          setActiveLocationId(locationData.id);
          setFlyToId(null);
        }}
        onPopupClose={(closedId) => {
          setActiveLocationId((currentActiveId) =>
            currentActiveId === closedId ? null : currentActiveId,
          );
          setFlyToId((currentFlyId) =>
            currentFlyId === closedId ? null : currentFlyId,
          );
        }}
      />
      <LocationsList
        locationEntries={locationEntries}
        activeLocationId={activeLocationId}
        onListItemClick={(id) => {
          setActiveLocationId(id);
          setFlyToId(id);
        }}
      />
    </>
  );
}

Locations.propTypes = {
  locations: PropTypes.string,
};

export default Locations;
