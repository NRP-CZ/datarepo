import React from "react";
import PropTypes from "prop-types";
import { List } from "semantic-ui-react";
import AutoScrollList from "./AutoScrollList";
import LocationListItem from "./LocationListItem";
import withSemanticUIForwardDOMRef from "./withSemanticUIForwardDOMRef";

const WrappedLocationListItem = withSemanticUIForwardDOMRef(LocationListItem);

function findActiveIndex(id, locationEntries) {
  if (!id) return undefined;
  const index = locationEntries.findIndex((entry) => entry.id === id);
  return index === -1 ? undefined : index;
}

export function LocationsList({
  locationEntries,
  activeLocationId,
  onListItemClick,
}) {
  return (
    <div style={{ maxHeight: "250px", overflowY: "auto" }}>
      <List bulleted relaxed>
        <AutoScrollList
          list={locationEntries}
          activeIndex={findActiveIndex(
            activeLocationId,
            locationEntries,
          )}
          getKey={(locationEntry, _) => {
            return locationEntry.id;
          }}
          renderItem={(locationEntry, _) => {
            return (
              <WrappedLocationListItem
                active={locationEntry.id === activeLocationId}
                locationEntry={locationEntry}
                onClick={onListItemClick}
              ></WrappedLocationListItem>
            );
          }}
        ></AutoScrollList>
      </List>
    </div>
  );
}

LocationsList.propTypes = {
  locationEntries: PropTypes.arrayOf(
    PropTypes.shape({
      id: PropTypes.string.isRequired,
      location: PropTypes.object.isRequired,
      geometry: PropTypes.object.isRequired,
    }),
  ),
  activeLocationId: PropTypes.string,
  onListItemClick: PropTypes.func,
};

export default LocationsList;
