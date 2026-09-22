import React from "react";
import PropTypes from "prop-types";
import { List } from "semantic-ui-react";
// import AutoScrollList from "./AutoScrollList";
import LocationListItem from "./LocationListItem";

// function findActiveIndex(id, locationEntries) {
//   if (!id) return undefined;
//   const index = locationEntries.findIndex((entry) => entry.id === id);
//   return index === -1 ? undefined : index;
// }

export function LocationsList(props) {
  return (
    <List as="ul">
      {/* <AutoScrollList
        list={props.locationEntries}
        activeIndex={findActiveIndex(
          props.activeLocationId,
          props.locationEntries,
        )}
        renderItem={(locationEntry, _) => {
          return (
            <LocationListItem
              active={locationEntry.id === props.activeLocationId}
              locationEntry={locationEntry}
              onClick={props.onListItemClick}
            ></LocationListItem>
          );
        }}
      ></AutoScrollList> */}
      {props.locationEntries.map((locationEntry) => {
        return (
          <LocationListItem
            key={locationEntry.id}
            active={locationEntry.id === props.activeLocationId}
            locationEntry={locationEntry}
            onClick={props.onListItemClick}
          ></LocationListItem>
        );
      })}
    </List>
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
  layersManager: PropTypes.object.isRequired,
  activeLocationId: PropTypes.string,
  onListItemClick: PropTypes.func,
};

export default LocationsList;
