import React, { useRef } from "react";
import PropTypes from "prop-types";
import { i18next } from "@translations/ccmm_invenio";
import { TextField, GroupField } from "react-invenio-forms";
import { useFormikContext, getIn } from "formik";

export function LongitudeAndLatitudeGroupField({
  basePath,
  onReverseSearch,
  isLoading,
}) {
  const { values, setFieldValue } = useFormikContext();

  const focusedCoords = useRef({ lon: null, lat: null });

  const handleFocus = () => {
    focusedCoords.current = {
      lon: getIn(values, `${basePath}.geometry.coordinates.0`),
      lat: getIn(values, `${basePath}.geometry.coordinates.1`),
    };
  };

  const handleCoordinatesBlur = async () => {
    const currentLon = getIn(values, `${basePath}.geometry.coordinates.0`);
    const currentLat = getIn(values, `${basePath}.geometry.coordinates.1`);

    if (
      currentLat === focusedCoords.current.lat &&
      currentLon === focusedCoords.current.lon
    ) {
      return;
    }

    if (currentLat && currentLon && !isNaN(currentLat) && !isNaN(currentLon)) {
      setFieldValue(`${basePath}.geometry`, {
        type: "Point",
        coordinates: [parseFloat(currentLon), parseFloat(currentLat)],
      });
      if (onReverseSearch) {
        await onReverseSearch(currentLat, currentLon);
      }
    }
  };

  return (
    <GroupField widths="equal">
      <TextField
        fieldPath={`${basePath}.geometry.coordinates.1`}
        placeholder={i18next.t("Latitude")}
        label={i18next.t("Latitude")}
        onFocus={handleFocus}
        onBlur={handleCoordinatesBlur}
        loading={isLoading}
      />
      <TextField
        fieldPath={`${basePath}.geometry.coordinates.0`}
        placeholder={i18next.t("Longitude")}
        label={i18next.t("Longitude")}
        onFocus={handleFocus}
        onBlur={handleCoordinatesBlur}
        loading={isLoading}
      />
    </GroupField>
  );
}

LongitudeAndLatitudeGroupField.propTypes = {
  basePath: PropTypes.string.isRequired,
  onReverseSearch: PropTypes.func,
  isLoading: PropTypes.bool,
};
