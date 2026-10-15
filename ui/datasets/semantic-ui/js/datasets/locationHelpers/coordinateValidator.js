/**
 * @param value value of cordinate
 * @param bounds object with `min` and `max` properties representing maximal available range for the `value`
 * @returns true if `value` is a plain finite number within `bounds`, otherwise false.
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