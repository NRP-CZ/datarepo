import React from "react";
import PropTypes from "prop-types";
import AutoScrollList from "./AutoScrollList";
import LocationListItemContent from "./LocationListItemContent";

export function LocationsList({
  locationEntries,
  activeLocationId,
  onItemClick,
}) {
  return (
    <AutoScrollList
      items={locationEntries}
      scrollToId={activeLocationId}
      renderItem={(locationEntry) => (
        <LocationListItemContent
          locationEntry={locationEntry}
          active={locationEntry.id === activeLocationId}
          onClick={onItemClick}
        />
      )}
    ></AutoScrollList>
  );
}

LocationsList.propTypes = {
  locationEntries: PropTypes.arrayOf(
    PropTypes.shape({
      id: PropTypes.string.isRequired,
      location: PropTypes.object.isRequired,
      geometry: PropTypes.object.isRequired,
    }).isRequired,
  ),
  activeLocationId: PropTypes.string,
  onItemClick: PropTypes.func,
};

export default LocationsList;
