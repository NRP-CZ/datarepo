import React, { useState, useRef, useMemo } from "react";
import PropTypes from "prop-types";
import { i18next } from "@translations/i18next";
import LocationsList from "./LocationsList";
import LocationsMap from "./LocationsMap";
import { ErrorElement } from "@js/oarepo_ui/search";

function Locations({ locations }) {
  const locationEntries = useMemo(() => {
    if (!locations) return null;
    if (locations.length === 0) return [];

    return locations
      .map((location) => {
        if (!location.geometry || typeof location.geometry !== "object") {
          return null;
        }

        const geometry = location.geometry;
        return { id: crypto.randomUUID(), location, geometry };
      })
      .filter(Boolean);
  }, [locations]);

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
      <ErrorElement
        error={new Error(i18next.t("No valid locations were found!"))}
      />
    );
  }
  if (locationEntries.length === 0) {
    return (
      <ErrorElement error={new Error(i18next.t("No locations were found!"))} />
    );
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
  locations: PropTypes.array.isRequired,
};

export default Locations;
