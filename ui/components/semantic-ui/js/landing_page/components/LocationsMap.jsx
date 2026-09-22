import React, { useRef, useEffect } from "react";
import PropTypes from "prop-types";
import L from "leaflet";
import "leaflet/dist/leaflet.css";
import { i18next } from "@translations/i18next";
import sanitizeHtml from "sanitize-html";

function buildFormattedValue(key, value) {
  let formattedValue = String(value);
  if (key === "identifiers" && Array.isArray(value)) {
    formattedValue = value
      .map((item) => item.identifier)
      .filter(Boolean)
      .join(", ");
  }
  return formattedValue;
}

function buildPopUp(location) {
  let popupHtml = `<div text-align: center;>`;

  if (location.place) {
    popupHtml += `
      <div>
        <h6 class="ui horizontal fitted divider header">${i18next.t("Place")}</h6>
        ${sanitizeHtml(location.place)}
      </div>`;
  }

  for (const [key, value] of Object.entries(location)) {
    if (key !== "geometry" && key !== "place" && key !== "type" && value) {
      const formattedKey = key.charAt(0).toUpperCase() + key.slice(1);
      const formattedValue = buildFormattedValue(key, value);
      popupHtml += `
        <div style="margin-top: 1em;">
          <h6 class="ui horizontal fitted divider header">${sanitizeHtml(formattedKey)}</h6>
          <span>${sanitizeHtml(formattedValue)}</span>
        </div>`;
    }
  }
  popupHtml += `</div>`;

  return popupHtml;
}

function showGlobalMapPopUp(map, message) {
  map.setView([0, 0], 1);
  L.popup({
    closeButton: true,
    autoClose: false,
  })
    .setLatLng(map.getCenter())
    .setContent(`<b>${message}</b>`)
    .openOn(map);
}

function LocationsMap(props) {
  const mapContainerRef = useRef(null);
  const mapInstanceRef = useRef(null);

  useEffect(() => {
    if (!mapContainerRef.current) return;

    if (mapInstanceRef.current) {
      mapInstanceRef.current.remove();
    }

    const map = L.map(mapContainerRef.current).setView([0, 0], 0);
    mapInstanceRef.current = map;

    L.tileLayer("https://tile.openstreetmap.org/{z}/{x}/{y}.png", {
      attribution:
        '&copy; <a href="http://www.openstreetmap.org/copyright">OpenStreetMap</a>',
    }).addTo(map);

    if (!props.locationEntries) {
      showGlobalMapPopUp(map, i18next.t("No valid locations were found!"));
      return;
    }

    if (props.locationEntries.length === 0) {
      showGlobalMapPopUp(map, i18next.t("No locations were found!"));
      return;
    }

    const featureGroup = L.featureGroup().addTo(map);

    props.locationEntries.forEach(({ location, geometry }) => {
      const layer = L.geoJSON(geometry, {
        style: { color: "#3399ff", weight: 2, opacity: 0.8 },
        pointToLayer: (_feature, latlng) => {
          return L.circleMarker(latlng, {
            radius: 6,
            fillColor: "#3399ff",
            color: "#3399ff",
            weight: 2,
            opacity: 1,
            fillOpacity: 0.8,
          });
        },
      });

      layer.bindPopup(buildPopUp(location));
      featureGroup.addLayer(layer);
    });

    if (featureGroup.getLayers().length > 0) {
      map.fitBounds(featureGroup.getBounds(), { padding: [10, 10] });
    } else {
      map.setView([0, 0], 13);
    }

    return () => {
      map.remove();
      mapInstanceRef.current = null;
    };
  }, [props.locationEntries]);

  return (
    <div
      ref={mapContainerRef}
      style={{
        height: "260px",
        maxHeight: "40vw",
        width: "100%",
        marginBottom: "1em",
      }}
    ></div>
  );
}

LocationsMap.propTypes = {
  locationEntries: PropTypes.array,
};

export default LocationsMap;
