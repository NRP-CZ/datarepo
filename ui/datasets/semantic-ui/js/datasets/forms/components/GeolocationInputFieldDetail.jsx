import React, { useState, useRef } from "react";
import PropTypes from "prop-types";
import {
  TextField,
  TextAreaField,
  FieldLabel,
  GroupField,
} from "react-invenio-forms";
import { useFormikContext, getIn } from "formik";
import {
  Button,
  Icon,
  Accordion,
  AccordionTitle,
  AccordionContent,
  Divider,
  Tab,
  TabPane,
  Form,
  Label,
} from "semantic-ui-react";
import { i18next } from "@translations/ccmm_invenio";
import { IdentifiersField } from "@js/invenio_rdm_records";
import { NominatimSearchBar } from "./NominatimSearchBar";
import { useNominatim } from "../hooks/useNominatim";

function renderGeometryTextAreaEditor(type, geoJsonValue, onChange) {
  if (type === "wkt") {
    return (
      <Form.Field className="invenio-text-area-field">
        <Form.TextArea
          onChange={onChange} // TODO: convert
          onBlur={onChange} // TODO: convert
          value={geoJsonValue} // TODO: convert
          placeholder={i18next.t("Enter WKT string...")}
        />
      </Form.Field>
    );
  } else {
    return (
      <Form.Field className="invenio-text-area-field">
        <Form.TextArea
          onChange={onChange}
          onBlur={onChange}
          value={geoJsonValue}
          placeholder={i18next.t("Enter GeoJSON string...")}
        />
      </Form.Field>
    );
  }
}

export function GeolocationInputFieldDetail({
  basePath,
  handleRemove,
  vocabularies,
}) {
  const { values, setFieldValue } = useFormikContext();
  const { reverseLocation, isLoading } = useNominatim();
  const [searchValue, setSearchValue] = useState("");

  const currentGeometryType = getIn(values, `${basePath}.geometry.type`, null);
  const isLocationPoint = currentGeometryType
    ? currentGeometryType === "Point"
    : true;

  const lastSearchedCoords = useRef({
    lat: getIn(values, `${basePath}.geometry.coordinates.1`),
    lon: getIn(values, `${basePath}.geometry.coordinates.0`),
  });

  const [isAdvancedOpen, setIsAdvancedOpen] = useState(() => {
    if (currentGeometryType && !isLocationPoint) {
      return true;
    }
    return false;
  });

  const handleCoordinatesBlur = async () => {
    const lat = getIn(values, `${basePath}.geometry.coordinates.1`);
    const lon = getIn(values, `${basePath}.geometry.coordinates.0`);

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
          `${basePath}.place`,
          result.name ? result.name : result.display_name
        );
        setSearchValue(result.display_name);
      }
    }
  };

  const panes = [
    {
      menuItem: "GeoJSON",
      render: () => (
        <TabPane attached={false} style={{ border: "none", boxShadow: "none" }}>
          {renderGeometryTextAreaEditor("geojson")}
        </TabPane>
      ),
    },
    {
      menuItem: "WKT",
      render: () => (
        <TabPane attached={false} style={{ border: "none", boxShadow: "none" }}>
          {renderGeometryTextAreaEditor("wkt")}
        </TabPane>
      ),
    },
  ];

  return (
    <div className="geolocation-detail">
      <TextField
        fieldPath={`${basePath}.place`}
        label={i18next.t("Name")}
        placeholder={i18next.t("Use map, search bar or advanced editor...")}
      />

      <TextAreaField
        fieldPath={`${basePath}.description`}
        label={i18next.t("Description")}
        placeholder={i18next.t("Additional details about this location...")}
      />

      <IdentifiersField
        fieldPath={`${basePath}.identifiers`}
        label={i18next.t("Identifiers")}
        labelIcon={""}
        schemeOptions={vocabularies?.identifiers?.scheme}
        showEmptyValue
      />

      <Form.Field>
        <FieldLabel
          htmlFor={`${basePath}.search`}
          label={i18next.t("Location")}
        />
        <NominatimSearchBar basePath={basePath} searchValue={searchValue} />
      </Form.Field>

      {isLocationPoint && (
        <GroupField widths="equal">
          <TextField
            fieldPath={`${basePath}.geometry.coordinates.1`}
            placeholder="Latitude"
            label="Latitude"
            onBlur={handleCoordinatesBlur}
            loading={isLoading}
          />
          <TextField
            fieldPath={`${basePath}.geometry.coordinates.0`}
            placeholder="Longitude"
            label="Longitude"
            onBlur={handleCoordinatesBlur}
            loading={isLoading}
          />
        </GroupField>
      )}

      <Accordion>
        <AccordionTitle
          style={{ fontSize: "0.875em", fontWeight: "bold" }}
          active={isAdvancedOpen}
          onClick={() => {
            setIsAdvancedOpen((prev) => !prev);
          }}
        >
          <Icon name="dropdown" />
          Advanced
        </AccordionTitle>
        <AccordionContent active={isAdvancedOpen}>
          <Tab menu={{ secondary: true, pointing: true }} panes={panes} />
        </AccordionContent>
      </Accordion>

      {!isAdvancedOpen && <Divider />}

      <Button
        type="button"
        color="red"
        icon
        labelPosition="left"
        onClick={handleRemove}
      >
        <Icon name="trash alternate" />
        {i18next.t("Remove location")}
      </Button>
    </div>
  );
}

GeolocationInputFieldDetail.propTypes = {
  basePath: PropTypes.string.isRequired,
  handleRemove: PropTypes.func.isRequired,
  vocabularies: PropTypes.object,
};