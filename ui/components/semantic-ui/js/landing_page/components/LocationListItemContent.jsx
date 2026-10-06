import React from "react";
import PropTypes from "prop-types";
import { i18next } from "@translations/i18next";
import { Icon } from "semantic-ui-react";

export function LocationListItemContent({ locationEntry, active, onClick }) {
  const { id, location, geometry } = locationEntry || {};

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
    <>
      <span
        onClick={() => {
          if (onClick) onClick(id);
        }}
        style={{ cursor: "pointer" }}
      >
        {active ? <b>{location.place}</b> : location.place}
      </span>
      {isPoint && (
        <span style={{ marginLeft: "4px" }}>
          <a
            href={`https://google.com/maps/place/${lat},${lon}`}
            style={{ color: "#2f6fa7" }}
            target="_blank"
            rel="noopener noreferrer"
            onClick={(e) => e.stopPropagation()}
          >
            {lat}, {lon} <i className="external alternate icon"></i>
          </a>
          <Icon
            name="copy"
            color="yellow"
            style={{ cursor: "copy" }}
            onClick={() => {
              navigator.clipboard.writeText(`${lat}, ${lon}`);
              alert(
                i18next.t("Copied the latitude and longitude") +
                  ": " +
                  `${lat}, ${lon}` +
                  ".",
              );
            }}
          />
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
