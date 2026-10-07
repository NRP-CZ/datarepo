import React from "react";
import PropTypes from "prop-types";
import { ClipboardCopyButton } from "@js/oarepo_ui/components/ClipboardCopyButton";

const LAT_BOUNDS = { min: -90, max: 90 };
const LON_BOUNDS = { min: -180, max: 180 };

/**
 * Returns true if `value` is a plain finite number within `bounds`, otherwise false.
 */
function validateCoordinate(value, bounds) {
  if (typeof value !== "number" || !Number.isFinite(value)) {
    return false;
  }
  if (value < bounds.min || value > bounds.max) {
    return false;
  }
  return true;
}

/**
 * Extracts and validates a [lat, lon] pair from a GeoJSON Point geometry.
 */
function getValidPointCoordinates(geometry) {
  if (
    !geometry ||
    geometry.type !== "Point" ||
    !Array.isArray(geometry.coordinates) ||
    geometry.coordinates.length !== 2
  ) {
    return undefined;
  }

  const [lon, lat] = geometry.coordinates;
  if (
    !(
      validateCoordinate(lat, LAT_BOUNDS) && validateCoordinate(lon, LON_BOUNDS)
    )
  ) {
    return undefined;
  }

  return { lat, lon };
}

export function LocationListItemContent({ locationEntry, active, onClick }) {
  const { id, location, geometry } = locationEntry || {};

  if (!location || !location.place || !geometry) {
    console.warn(`Skipping invalid location: `, location);
    return null;
  }

  const point = getValidPointCoordinates(geometry);

  return (
    <>
      <span
        onClick={() => {
          if (onClick) onClick(id);
        }}
        style={{ cursor: "pointer" }}
      >
        {active ? <b>{location.place}</b> : location.place}
      </span>
      {point && (
        <span className="ml-5 location-list-item-content-actions">
          <a
            href={`https://google.com/maps/place/${point.lat},${point.lon}`}
            target="_blank"
            rel="noopener noreferrer"
            onClick={(e) => e.stopPropagation()}
          >
            {point.lat}, {point.lon} <i className="external alternate icon"></i>
          </a>
          <ClipboardCopyButton copyText={`${point.lat}, ${point.lon}`} />
        </span>
      )}
    </>
  );
}

LocationListItemContent.propTypes = {
  locationEntry: PropTypes.shape({
    id: PropTypes.string.isRequired,
    location: PropTypes.object.isRequired,
    geometry: PropTypes.object.isRequired,
  }),
  active: PropTypes.bool,
  onClick: PropTypes.func,
};

export default LocationListItemContent;
