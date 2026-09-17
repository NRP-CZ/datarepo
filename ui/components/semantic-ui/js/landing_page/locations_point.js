import { getGeometryAsGeoJSONObject } from "./locations_geometry";

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

    if (!location.geometry) {
      console.warn(
        `Skipping location because it does not contain any geometry!`,
      );
      return;
    }

    const geometry = getGeometryAsGeoJSONObject(location);

    if (!geometry || geometry.type !== "Point") {
      console.warn(`Skipping location because it is not Point!`);
      return;
    }

    if (
      !Array.isArray(geometry.coordinates) ||
      geometry.coordinates.length !== 2
    ) {
      console.warn(
        `Skipping location because it does not contain expected point's longitude and latitude!`,
      );
      return;
    }

    const [lon, lat] = geometry.coordinates;
    const link = `https://google.com/maps/place/${lat},${lon}`;

    container.innerHTML = `
      (<a href="${link}" style="color: #2f6fa7;" target="_blank"rel="noopener noreferrer">${lat}, ${lon} <i class="external alternate icon"></i></a>)
    `;
  });
});
