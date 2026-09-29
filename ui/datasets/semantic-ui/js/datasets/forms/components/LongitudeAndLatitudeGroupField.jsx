import React, { useRef } from "react";
import PropTypes from "prop-types";
import { TextField, GroupField } from "react-invenio-forms";
import { useFormikContext, getIn } from "formik";

export function LongitudeAndLatitudeGroupField(props) {
  const { values, setFieldValue } = useFormikContext();

  const focusedCoords = useRef({ lon: null, lat: null });

  const handleFocus = () => {
    focusedCoords.current = {
      lon: getIn(values, `${props.basePath}.geometry.coordinates.0`),
      lat: getIn(values, `${props.basePath}.geometry.coordinates.1`),
    };
  };

  const handleCoordinatesBlur = async () => {
    const currentLon = getIn(
      values,
      `${props.basePath}.geometry.coordinates.0`,
    );
    const currentLat = getIn(
      values,
      `${props.basePath}.geometry.coordinates.1`,
    );

    if (
      currentLat === focusedCoords.current.lat &&
      currentLon === focusedCoords.current.lon
    ) {
      return;
    }

    if (currentLat && currentLon && !isNaN(currentLat) && !isNaN(currentLon)) {
      setFieldValue(`${props.basePath}.geometry`, {
        type: "Point",
        coordinates: [parseFloat(currentLon), parseFloat(currentLat)],
      });
      if (props.onReverseSearch) {
        await props.onReverseSearch(currentLat, currentLon);
      }
    }
  };

  return (
    <GroupField widths="equal">
      <TextField
        fieldPath={`${props.basePath}.geometry.coordinates.1`}
        placeholder="Latitude"
        label="Latitude"
        onFocus={handleFocus}
        onBlur={handleCoordinatesBlur}
        loading={props.isLoading}
      />
      <TextField
        fieldPath={`${props.basePath}.geometry.coordinates.0`}
        placeholder="Longitude"
        label="Longitude"
        onFocus={handleFocus}
        onBlur={handleCoordinatesBlur}
        loading={props.isLoading}
      />
    </GroupField>
  );
}

LongitudeAndLatitudeGroupField.propTypes = {
  basePath: PropTypes.string.isRequired,
  onReverseSearch: PropTypes.func,
  isLoading: PropTypes.bool,
};
