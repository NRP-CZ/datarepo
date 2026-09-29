import React, { useState, useEffect } from "react";
import PropTypes from "prop-types";
import { useFormikContext, getIn } from "formik";
import { Form, Label } from "semantic-ui-react";
import { i18next } from "@translations/ccmm_invenio";
import PropTypes from "prop-types";
import { wktToGeoJSON, geojsonToWKT } from "@terraformer/wkt"

export function WktEditor(props) {
  const { values, setFieldValue } = useFormikContext();
  const geometryPath = `${props.basePath}.geometry`;
  const geometry = getIn(values, geometryPath, null);

  const [textValue, setTextValue] = useState("");
  const [error, setError] = useState(null);

  useEffect(() => {
    if (geometry && typeof geometry === "object") {
      const wktString = geojsonToWKT(geometry);
      setTextValue(wktString);
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
      const geoJson = wktToGeoJSON(textValue);

      if (!geoJson.type) {
        throw new Error(
          i18next.t("Missing 'type' property (e.g., 'Point', 'Polygon')"),
        );
      }

      setFieldValue(geometryPath, geoJson);
      setError(null);

      if (geoJson.type === "Point" && geoJson.coordinates?.length >= 2) {
        const lon = geoJson.coordinates[0];
        const lat = geoJson.coordinates[1];
        if (props.onReverseSearch) {
          props.onReverseSearch(lat, lon);
        }
      }
    } catch (err) {
      setError(
        i18next.t(`Invalid WKT!`) +
          ` ` +
          i18next.t(`Details`) +
          `: <` +
          `${err.message}` +
          ">.",
      );
    }
  };

  return (
    <Form.Field className="invenio-text-area-field" error={!!error}>
      <Form.TextArea
        onChange={handleChange}
        onBlur={handleBlur}
        value={textValue}
        placeholder={i18next.t(
          'Enter the location manually using WKT format. E.g.:\n\nPOINT(0 0)\n',
        )}
        rows={7}
      />
      {error && <Label pointing prompt color="red" content={error} />}
    </Form.Field>
  );
}

WktEditor.propTypes = {
  basePath: PropTypes.string.isRequired,
  onReverseSearch: PropTypes.func,
};
