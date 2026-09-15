import { wktToGeoJSON } from "@terraformer/wkt";

/**
 * Retrieves from `location` object `geometry` property and parses it to GeoJSON object.
 * @param location location
 * @returns geometry inside location as GeoJSON object, if no geometry or parsing error, returns undefined
 */
export function getGeometryAsGeoJSONObject(location) {
  let geometry = undefined;

  if (typeof location.geometry === "object" && location.geometry !== null) {
    geometry = location.geometry;
  } else if (typeof location.geometry === "string") {
    try {
      geometry = wktToGeoJSON(location.geometry);
    } catch (error) {
      console.error("Failed to parse WKT:", error);
    }
  }

  return geometry;
}
