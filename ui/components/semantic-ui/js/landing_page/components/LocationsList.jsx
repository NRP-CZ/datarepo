import React from "react";
import PropTypes from "prop-types";
import AutoScrollList from "./AutoScrollList";
import LocationListItemContent from "./LocationListItemContent";

export function LocationsList({
  locationEntries,
  activeLocationId,
  onItemClick,
}) {
  const items = locationEntries.map((locationEntry) => ({
    id: locationEntry.id,
    component: (
      <LocationListItemContent
        locationEntry={locationEntry}
        active={locationEntry.id === activeLocationId}
        onClick={() => {
          onItemClick(locationEntry);
        }}
      />
    ),
  }));

  return <AutoScrollList items={items} scrollToId={activeLocationId} />;
}

LocationsList.propTypes = {
  locationEntries: PropTypes.arrayOf(
    PropTypes.shape({
      id: PropTypes.string.isRequired,
      location: PropTypes.object.isRequired,
      geometry: PropTypes.object.isRequired,
    }),
  ).isRequired,
  activeLocationId: PropTypes.string,
  onItemClick: PropTypes.func,
};

export default LocationsList;
