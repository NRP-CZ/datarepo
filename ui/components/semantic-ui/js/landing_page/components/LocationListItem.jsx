import React from "react";
import PropTypes from "prop-types";

export function LocationListItem(props) {
  const { location, geometry } = props.locationEntry || {};

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
    <li>
      {props.active ? <b>{location.place}</b> : location.place}
      {isPoint && (
        <a
          href={`https://google.com/maps/place/${lat},${lon}`}
          style={{ color: "#2f6fa7", marginLeft: "8px" }}
          target="_blank"
          rel="noopener noreferrer"
        >
          {lat}, {lon} <i className="external alternate icon"></i>
        </a>
      )}
    </li>
  );
}

LocationListItem.propTypes = {
  locationEntry: PropTypes.shape({
    id: PropTypes.string.isRequired,
    location: PropTypes.object.isRequired,
    geometry: PropTypes.object.isRequired,
  }),
  active: PropTypes.bool,
};

export default LocationListItem;
