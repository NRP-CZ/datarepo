export const LAT_BOUNDS = { min: -90, max: 90 };
export const LON_BOUNDS = { min: -180, max: 180 };

/**
 * Returns true if `value` is a plain finite number within `bounds`, otherwise false.
 */
export function validateCoordinate(value, bounds) {
  if (typeof value !== "number" || !Number.isFinite(value)) {
    return false;
  }
  if (value < bounds.min || value > bounds.max) {
    return false;
  }
  return true;
}