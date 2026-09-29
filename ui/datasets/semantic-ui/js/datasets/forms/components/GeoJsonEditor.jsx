import React, { useState, useEffect } from "react";
import PropTypes from "prop-types";
import { useFormikContext, getIn } from "formik";
import { Form, Label } from "semantic-ui-react";
import { i18next } from "@translations/ccmm_invenio";
import PropTypes from "prop-types";

export function GeoJSsonEditor(props) {
  const { values, setFieldValue } = useFormikContext();
  const geometryPath = `${props.basePath}.geometry`;
  const geometry = getIn(values, geometryPath, null);

  const [textValue, setTextValue] = useState("");
  const [error, setError] = useState(null);

  useEffect(() => {
    if (geometry && typeof geometry === "object") {
      setTextValue(JSON.stringify(geometry, null, 2));
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

      setFieldValue(geometryPath, parsedObj);
      setError(null);
      setTextValue(JSON.stringify(parsedObj, null, 2));
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
    <Form.Field className="invenio-text-area-field" error={!!error}>
      <Form.TextArea
        onChange={handleChange}
        onBlur={handleBlur}
        value={textValue}
        placeholder={i18next.t(
          'Enter the location manually using GeoJSON format. E.g.:\n\n{\n  "type": "Point",\n  "coordinates": [0, 0]\n}',
        )}
        rows={7}
      />
      {error && <Label pointing prompt color="red" content={error} />}
    </Form.Field>
  );
}

GeoJSsonEditor.propTypes = {
  basePath: PropTypes.string.isRequired,
};
