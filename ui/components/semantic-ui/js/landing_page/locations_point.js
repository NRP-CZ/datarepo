import { wktToGeoJSON } from "@terraformer/wkt";

function parseWKT2GeoJSON(wktString) {
  return wktToGeoJSON(wktString);
}

document.addEventListener("DOMContentLoaded", function () {
  const containers = document.querySelectorAll(
    ".record-locations-point-reference",
  );

  containers.forEach((container) => {
    const locationAsString = container.getAttribute("data-location");
    if (!locationAsString) return;

    let location;
    try {
      location = JSON.parse(locationAsString);
    } catch (err) {
      console.error("Failed to parse location JSON:", err);
      return;
    }

    let geometry = undefined;
    if (typeof location.geometry === "object" && location.geometry !== null) {
      geometry = location.geometry;
    } else if (typeof location.geometry === "string") {
      try {
        geometry = parseWKT2GeoJSON(location.geometry);
      } catch (error) {
        console.error("Failed to parse WKT:", error);
      }
    }

    if (
      !geometry ||
      geometry.type !== "Point" ||
      !Array.isArray(geometry.coordinates) ||
      geometry.coordinates.length !== 2
    ) {
      return;
    }

    const [lon, lat] = geometry.coordinates;
    const link = `https://google.com/maps/place/${lat},${lon}`;

    container.innerHTML = `
      (<a href="${link}" style="color: #2f6fa7;" target="_blank"rel="noopener noreferrer">${lat}, ${lon} <i class="external alternate icon"></i></a>)
    `;
  });
});
