import React, { useRef, useEffect } from "react";
import PropTypes from "prop-types";
import L from "leaflet";
import { i18next } from "@translations/i18next";
import sanitizeHtml from "sanitize-html";
import "../../../less/components/locations-map.less";

function handleIdentifiersValue(value) {
  if (!Array.isArray(value)) {
    return "";
  }

  return value
    .map((entry) => {
      return entry.identifier;
    })
    .filter(Boolean)
    .join(", ");
}

function buildFormattedValue(key, value) {
  // Special cases.
  if (key === "identifiers") {
    return handleIdentifiersValue(value);
  }

  let formattedValue = String(value);

  if (Array.isArray(value)) {
    formattedValue = value
      .map((item) => item)
      .filter(Boolean)
      .join(", ");
  }

  if (typeof value === "object") {
    formattedValue = Object.values(value)
      .map((val) => buildFormattedValue(undefined, val))
      .filter(Boolean)
      .join(", ");
  }

  return formattedValue;
}

function buildFomattedKey(key) {
  let formattedKey = key.charAt(0).toUpperCase() + key.slice(1);

  if (formattedKey === "Identifiers") {
    formattedKey = i18next.t("Identifiers");
  } else if (formattedKey === "Description") {
    formattedKey = i18next.t("Description");
  }

  return formattedKey;
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
      const formattedKey = buildFomattedKey(key);
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

function LocationsMap({
  locationEntries,
  layersManager,
  flyToId,
  onLocationsClick,
  onPopupClose,
}) {
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

    const resizeObserver = new ResizeObserver(() => {
      if (mapInstanceRef.current) {
        mapInstanceRef.current.invalidateSize();
      }
    });

    resizeObserver.observe(mapContainerRef.current);

    if (!locationEntries) {
      showGlobalMapPopUp(map, i18next.t("No valid locations were found!"));
      return;
    }

    if (locationEntries.length === 0) {
      showGlobalMapPopUp(map, i18next.t("No locations were found!"));
      return;
    }

    const featureGroup = L.featureGroup().addTo(map);

    locationEntries.forEach(({ id, location, geometry }) => {
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

      layer.on("click", (_) => {
        if (onLocationsClick) {
          onLocationsClick({ id, location, geometry });
        }
      });

      layer.on("popupclose", () => {
        if (onPopupClose) {
          onPopupClose(id);
        }
      });

      featureGroup.addLayer(layer);
      layersManager[id] = layer;
    });

    if (featureGroup.getLayers().length > 0) {
      map.fitBounds(featureGroup.getBounds(), { padding: [10, 10] });
    } else {
      map.setView([0, 0], 13);
    }

    return () => {
      resizeObserver.disconnect();
      map.remove();
      mapInstanceRef.current = null;
    };
  }, [locationEntries]);

  useEffect(() => {
    const map = mapInstanceRef.current;

    if (!map || !flyToId) return;

    const targetLayer = layersManager[flyToId];

    if (targetLayer) {
      map.flyToBounds(targetLayer.getBounds(), { maxZoom: 10, duration: 1.0 });

      map.once("moveend", () => {
        targetLayer.openPopup();
      });
    }
  }, [flyToId, layersManager]);

  return <div ref={mapContainerRef} className="locations-map"></div>;
}

LocationsMap.propTypes = {
  locationEntries: PropTypes.arrayOf(
    PropTypes.shape({
      id: PropTypes.string.isRequired,
      location: PropTypes.object.isRequired,
      geometry: PropTypes.object.isRequired,
    }),
  ),
  layersManager: PropTypes.object.isRequired,
  flyToId: PropTypes.string,
  onLocationsClick: PropTypes.func,
  onPopupClose: PropTypes.func,
};

export default LocationsMap;
