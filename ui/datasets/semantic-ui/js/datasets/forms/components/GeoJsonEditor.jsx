import React, { useState, useEffect } from "react";
import PropTypes from "prop-types";
import { useFormikContext, getIn } from "formik";
import { TextAreaField } from "react-invenio-forms";
import { i18next } from "@translations/i18next";
import { SUPPORTED_GEOMETRY_TYPES } from "@js/datasets/locationHelpers/supportedGeometryTypes";

export function GeoJsonEditor({ basePath, onReverseSearch }) {
  const { values, setFieldValue } = useFormikContext();

  const geometryPath = `${basePath}.geometry`;
  const geometry = getIn(values, geometryPath, null);

  const [textValue, setTextValue] = useState("");
  const [error, setError] = useState(null);

  useEffect(() => {
    if (geometry && typeof geometry === "object") {
      try {
        setTextValue(JSON.stringify(geometry, null, 2));
      } catch (e) {
        console.error(
          `There seems to be application error as received geometry is invalid! Details: <${e}>.`,
        );
        setError(i18next.t("Invalid JSON!"));
      }
    } else {
      setTextValue("");
    }
  }, [geometry]);

  const handleChange = (_, { value }) => {
    setTextValue(value);
    if (error) setError(null);
  };

  const handleBlur = () => {
    if (!textValue.trim()) {
      setFieldValue(geometryPath, null);
      setError(null);
      return;
    }

    try {
      const parsedObj = JSON.parse(textValue);

      if (!parsedObj.type) {
        throw new Error(
          i18next.t("Missing 'type' property (e.g., 'Point', 'Polygon')"),
        );
      }

      if (!SUPPORTED_GEOMETRY_TYPES.includes(parsedObj.type)) {
        throw new Error(
          i18next.t("Unsupported geometry type") +
            " '" +
            parsedObj.type +
            "'." +
            i18next.t(
              "We currently support only 'Point', 'MultiPoint' and 'Polygon'.",
            ),
        );
      }

      setFieldValue(geometryPath, parsedObj);
      setError(null);

      if (parsedObj.type === "Point" && parsedObj.coordinates?.length >= 2) {
        const lon = parsedObj.coordinates[0];
        const lat = parsedObj.coordinates[1];
        if (onReverseSearch) {
          onReverseSearch(lat, lon);
        }
      }
    } catch (err) {
      setError(
        i18next.t(`Invalid JSON!`) +
          ` ` +
          i18next.t(`Details`) +
          `: <` +
          `${err.message}` +
          ">.",
      );
    }
  };

  return (
    <TextAreaField
      onChange={handleChange}
      onBlur={handleBlur}
      value={textValue}
      placeholder={i18next.t(
        'Enter the location manually using GeoJSON format. E.g.:\n\n{\n  "type": "Point",\n  "coordinates": [0, 0]\n}',
      )}
      rows={7}
      error={error}
    />
  );
}

GeoJsonEditor.propTypes = {
  basePath: PropTypes.string.isRequired,
  onReverseSearch: PropTypes.func,
};
