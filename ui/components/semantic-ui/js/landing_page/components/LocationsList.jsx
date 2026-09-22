import React from "react";
import PropTypes from "prop-types";
import { List } from "semantic-ui-react";
import AutoScrollList from "./AutoScrollList";
import LocationListItem from "./LocationListItem";

export function LocationsList(props) {
  return (
    <List as="ul">
      <AutoScrollList
        list={props.locationEntries}
        activeIndex={0}
        renderItem={(locationEntry, _) => {
          return (
            <LocationListItem locationEntry={locationEntry}></LocationListItem>
          );
        }}
      ></AutoScrollList>
    </List>
  );
}

LocationsList.propTypes = {
  locationEntries: PropTypes.array,
};

export default LocationsList;
