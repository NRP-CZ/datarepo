import { useFormikContext, getIn } from "formik";
import { useCallback } from "react";
import escapeRegExp from "lodash/escapeRegExp";

/** Matches a place name followed by an optional `" (N)"` suffix. Captures the number `N`. */
const PLACE_NAME_PATTERN = (placeName) =>
  new RegExp(`^${escapeRegExp(placeName)}(?: \\((\\d+)\\))?$`);

export function useUpdateLocationName() {
  const { values, setFieldValue } = useFormikContext();

  const getUniqueLocationName = useCallback(
    (fieldPath, activeTabIndex, placeName) => {
      if (!placeName) {
        return placeName;
      }
      
      const currentLocations = getIn(values, `${fieldPath}.features`, []);

      const pattern = PLACE_NAME_PATTERN(placeName);
      let maxNumber = -1;
      let hasMatch = false;

      currentLocations.forEach((location, index) => {
        if (index !== activeTabIndex && typeof location?.place === "string") {
          const match = location.place.match(pattern);

          if (match) {
            hasMatch = true;

            if (match[1]) {
              const num = parseInt(match[1], 10);
              if (num > maxNumber) {
                maxNumber = num;
              }
            } else if (maxNumber < 0) {
              maxNumber = 0;
            }
          }
        }
      });

      const suffix = hasMatch ? ` (${Math.max(0, maxNumber) + 1})` : "";

      return `${placeName}${suffix}`;
    },
    [values],
  );

  const updateLocationName = useCallback(
    (fieldPath, activeTabIndex, placeName) => {
      const uniqueName = getUniqueLocationName(
        fieldPath,
        activeTabIndex,
        placeName,
      );

      setFieldValue(
        `${fieldPath}.features.${activeTabIndex}.place`,
        uniqueName,
      );
    },
    [getUniqueLocationName, setFieldValue],
  );

  return { getUniqueLocationName, updateLocationName };
}
