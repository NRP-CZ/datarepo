import L from "leaflet";
import "leaflet/dist/leaflet.css";
import sanitizeHtml from "sanitize-html";
import { wktToGeoJSON } from "@terraformer/wkt";

function parseWKT2GeoJSON(wktString) {
  return wktToGeoJSON(wktString);
}

function buildPopUp(location) {
  let popupHtml = `<div text-align: center;>`;

  if (location.place) {
    popupHtml += `
      <div>
        <h6 class="ui horizontal fitted divider header">Place</h6>
        ${sanitizeHtml(location.place)}
      </div>`;
  }

  for (const [key, value] of Object.entries(location)) {
    if (key !== "geometry" && key !== "place" && key !== "type" && value) {
      const formattedKey = key.charAt(0).toUpperCase() + key.slice(1);
      popupHtml += `
        <div style="margin-top: 1em;">
          <h6 class="ui horizontal fitted divider header">${sanitizeHtml(formattedKey)}</h6>
          <span>${sanitizeHtml(String(value))}</span>
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

document.addEventListener("DOMContentLoaded", function () {
  const mapContainer = document.getElementById("record-locations-map");

  if (!mapContainer) {
    return;
  }

  const map = L.map("record-locations-map").setView([0, 0], 0);

  L.tileLayer("https://tile.openstreetmap.org/{z}/{x}/{y}.png", {
    attribution:
      '&copy; <a href="http://www.openstreetmap.org/copyright">OpenStreetMap</a>',
  }).addTo(map);

  const locationsAsString = mapContainer.getAttribute("data-locations");
  if (!locationsAsString) {
    showGlobalMapPopUp(map, "No valid locations were found!");
    return;
  }

  let locations;
  try {
    locations = JSON.parse(locationsAsString);
  } catch (err) {
    console.error("Failed to parse locations JSON:", err);
    return;
  }

  if (locations.length === 0) {
    showGlobalMapPopUp(map, "No locations were found!");
    return;
  }

  const featureGroup = L.featureGroup().addTo(map);

  locations.forEach((location) => {
    if (!location.geometry) {
      console.warn(
        `Skipping location because it does not contain any geometry!`,
      );
      return;
    }

    let geometry = undefined;
    if (typeof location.geometry === "object") {
      geometry = location.geometry;
    } else if (typeof location.geometry === "string") {
      try {
        geometry = parseWKT2GeoJSON(location.geometry);
      } catch (error) {
        console.error(error);
      }
    }

    if (!geometry) {
      console.warn(
        `Skipping location because it contains unknown type of geometry!`,
      );
      return;
    }

    const layer = L.geoJSON(geometry, {
      style: {
        color: "#3399ff",
        weight: 2,
        opacity: 0.8,
      },
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
});
