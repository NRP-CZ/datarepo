import React, { useRef } from "react";
import PropTypes from "prop-types";
import { TextField, GroupField } from "react-invenio-forms";
import { useFormikContext, getIn } from "formik";
import { useNominatim } from "../hooks/useNominatim";

export function LongitudeAndLatitudeGroupField(props) {
  const { values, setFieldValue } = useFormikContext();
  const { reverseLocation, isLoading } = useNominatim();

  const lastSearchedCoords = useRef({
    lon: getIn(values, `${props.basePath}.geometry.coordinates.0`),
    lat: getIn(values, `${props.basePath}.geometry.coordinates.1`),
  });

  const handleCoordinatesBlur = async () => {
    const lon = getIn(values, `${props.basePath}.geometry.coordinates.0`);
    const lat = getIn(values, `${props.basePath}.geometry.coordinates.1`);

    if (
      lat === lastSearchedCoords.current.lat &&
      lon === lastSearchedCoords.current.lon
    ) {
      return;
    }

    if (lat && lon && !isNaN(lat) && !isNaN(lon)) {
      const result = await reverseLocation(lat, lon);

      lastSearchedCoords.current = { lat, lon };

      if (result && result.display_name) {
        setFieldValue(
          `${props.basePath}.place`,
          result.name ? result.name : result.display_name,
        );
        props.onCoordinatesBlur(result);
      }
    }
  };

  return (
    <GroupField widths="equal">
      <TextField
        fieldPath={`${props.basePath}.geometry.coordinates.0`}
        placeholder="Latitude"
        label="Latitude"
        onBlur={handleCoordinatesBlur}
        loading={isLoading}
      />
      <TextField
        fieldPath={`${props.basePath}.geometry.coordinates.1`}
        placeholder="Longitude"
        label="Longitude"
        onBlur={handleCoordinatesBlur}
        loading={isLoading}
      />
    </GroupField>
  );
}

LongitudeAndLatitudeGroupField.propTypes = {
  basePath: PropTypes.string.isRequired,
  onCoordinatesBlur: PropTypes.func,
};
