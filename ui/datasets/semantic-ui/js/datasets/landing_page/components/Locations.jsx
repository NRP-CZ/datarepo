import React, { useState, useMemo, useCallback } from "react";
import PropTypes from "prop-types";
import LocationsList from "./LocationsList";
import LocationsMap from "./LocationsMap";

function Locations({ locationEntries }) {
  const sortedLocationEntries = useMemo(() => {
    return [...locationEntries].sort((a, b) => {
      const aIsPoint = a.geometry.type === "Point";
      const bIsPoint = b.geometry.type === "Point";
      if (aIsPoint && !bIsPoint) return 1;
      if (!aIsPoint && bIsPoint) return -1;
      return 0;
    });
  }, [locationEntries]);

  const [activeLocationId, setActiveLocationId] = useState(null);

  const onLocationClick = useCallback(
    (locationData) => {
      setActiveLocationId(locationData.id);
    },
    [setActiveLocationId],
  );

  const onPopupClose = useCallback(
    (closedId) => {
      setActiveLocationId((currentActiveId) =>
        currentActiveId === closedId ? null : currentActiveId,
      );
    },
    [setActiveLocationId],
  );

  return (
    <>
      <LocationsMap
        locationEntries={sortedLocationEntries}
        flyToId={activeLocationId}
        onLocationClick={onLocationClick}
        onPopupClose={onPopupClose}
      />
      <LocationsList
        locationEntries={locationEntries}
        activeLocationId={activeLocationId}
        onItemClick={onLocationClick}
      />
    </>
  );
}

Locations.propTypes = {
  locationEntries: PropTypes.arrayOf(
    PropTypes.shape({
      id: PropTypes.string.isRequired,
      location: PropTypes.object.isRequired,
      geometry: PropTypes.object.isRequired,
    }),
  ).isRequired,
};

export default Locations;
