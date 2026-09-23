import React from "react";
import PropTypes from "prop-types";
import { ListItem } from "semantic-ui-react";

export function LocationListItem(props) {
  const { id, location, geometry } = props.locationEntry || {};

  if (!location || !location.place || !geometry) {
    console.warn(`Skipping invalid location!`);
    return null;
  }

  const isPoint =
    geometry.type === "Point" && Array.isArray(geometry.coordinates);

  let lat, lon;
  if (isPoint) {
    [lon, lat] = geometry.coordinates;
  }

  return (
    <ListItem
      onClick={() => {
        if (props.onClick) props.onClick(id);
      }}
      style={{ cursor: "pointer" }}
    >
      {props.active ? <b>{location.place}</b> : location.place}
      {isPoint && (
        <a
          href={`https://google.com/maps/place/${lat},${lon}`}
          style={{ color: "#2f6fa7", marginLeft: "8px" }}
          target="_blank"
          rel="noopener noreferrer"
          onClick={(e) => e.stopPropagation()}
        >
          {lat}, {lon} <i className="external alternate icon"></i>
        </a>
      )}
    </ListItem>
  );
}

LocationListItem.propTypes = {
  locationEntry: PropTypes.shape({
    id: PropTypes.string.isRequired,
    location: PropTypes.object.isRequired,
    geometry: PropTypes.object.isRequired,
  }),
  active: PropTypes.bool,
  onClick: PropTypes.func,
};

export default LocationListItem;
