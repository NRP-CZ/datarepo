import React from "react";
import PropTypes from "prop-types";
import { List } from "semantic-ui-react";
import AutoScrollList from "./AutoScrollList";
import LocationListItem from "./LocationListItem";

// map.flyToBounds(targetLayer.getBounds(), { maxZoom: 15, duration: 1.5 });

//     // 2. Open the popup
//     // We wait for the flyTo animation to finish using 'moveend',
//     // otherwise the popup might open at the old screen coordinates and glitch.
//     map.once('moveend', () => {
//       targetLayer.openPopup();
//     });

function findActiveIndex(id, locationEntries) {
  const index = locationEntries.findIndex((entry) => {
    return entry.id === id;
  });

  return index === -1 ? 0 : index;
}

export function LocationsList(props) {
  return (
    <List as="ul">
      <AutoScrollList
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
            ></LocationListItem>
          );
        }}
      ></AutoScrollList>
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
};

export default LocationsList;
