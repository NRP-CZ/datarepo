import React, { useRef, useState, useEffect } from "react";
import PropTypes from "prop-types";
import { i18next } from "@translations/i18next";
import { TextField, GroupField } from "react-invenio-forms";
import { useFormikContext, getIn } from "formik";
import {
  validateCoordinate,
  LAT_BOUNDS,
  LON_BOUNDS,
} from "@js/datasets/locationHelpers/coordinateValidator";

export function LongitudeAndLatitudeGroupField({
  basePath,
  onReverseSearch,
  isLoading,
}) {
  const { values, setFieldValue } = useFormikContext();

  const focusedCoords = useRef({ lon: null, lat: null });

  const geometry = getIn(values, `${basePath}.geometry`);
  const currentLon = getIn(values, `${basePath}.geometry.coordinates.0`);
  const currentLat = getIn(values, `${basePath}.geometry.coordinates.1`);

  const [resetKey, setResetKey] = useState(0);

  // Updates the reset only key when the map sets geometry to exactly `null`.
  const isGeometryNull = geometry === null;
  useEffect(() => {
    if (isGeometryNull) {
      setResetKey((prev) => prev + 1);
    }
  }, [isGeometryNull]);

  const hasLat = currentLat !== "" && currentLat != null;
  const hasLon = currentLon !== "" && currentLon != null;

  const parsedLat = parseFloat(currentLat);
  const parsedLon = parseFloat(currentLon);

  const isLatValid = !hasLat || validateCoordinate(parsedLat, LAT_BOUNDS);
  const isLonValid = !hasLon || validateCoordinate(parsedLon, LON_BOUNDS);

  const handleFocus = () => {
    focusedCoords.current = {
      lon: currentLon,
      lat: currentLat,
    };
  };

  const handleCoordinatesBlur = async () => {
    if (
      currentLat === focusedCoords.current.lat &&
      currentLon === focusedCoords.current.lon
    ) {
      return;
    }

    if (hasLat && hasLon && isLatValid && isLonValid) {
      setFieldValue(`${basePath}.geometry`, {
        type: "Point",
        coordinates: [parsedLon, parsedLat],
      });
      if (onReverseSearch) {
        await onReverseSearch(parsedLat, parsedLon); // Reverse search only on blur, not for single change.
      }
    }
  };

  return (
    <GroupField widths="equal" key={resetKey}>
      <TextField
        fieldPath={`${basePath}.geometry.coordinates.1`}
        placeholder={i18next.t("Latitude")}
        label={i18next.t("Latitude")}
        onFocus={handleFocus}
        onBlur={handleCoordinatesBlur}
        loading={isLoading}
        error={
          !isLatValid
            ? i18next.t("Must be a valid number between -90 and 90.")
            : undefined
        }
      />
      <TextField
        fieldPath={`${basePath}.geometry.coordinates.0`}
        placeholder={i18next.t("Longitude")}
        label={i18next.t("Longitude")}
        onFocus={handleFocus}
        onBlur={handleCoordinatesBlur}
        loading={isLoading}
        error={
          !isLonValid
            ? i18next.t("Must be a valid number between -180 and 180.")
            : undefined
        }
      />
    </GroupField>
  );
}

LongitudeAndLatitudeGroupField.propTypes = {
  basePath: PropTypes.string.isRequired,
  onReverseSearch: PropTypes.func,
  isLoading: PropTypes.bool,
};
