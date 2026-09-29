import React, { useState } from "react";
import PropTypes from "prop-types";
import {
  TextField,
  TextAreaField,
  FieldLabel,
  GroupField,
} from "react-invenio-forms";
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
} from "semantic-ui-react";
import { i18next } from "@translations/ccmm_invenio";
import { IdentifiersField } from "@js/invenio_rdm_records";
import { NominatimSearchBar } from "./NominatimSearchBar";

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
        {/* TODO: If any grammar error, render error message here. */}
        {/* <Label pointing prompt content={""} /> */}
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
        {/* TODO: If any grammar error, render error message here. */}
        {/* <Label pointing prompt content={""} /> */}
      </Form.Field>
    );
  }
}

export function GeolocationInputFieldDetail({
  basePath,
  handleRemove,
  vocabularies,
}) {
  const [isAdvancedOpen, setIsAdvancedOpen] = useState(false);

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

  const isLocationPoint = true;

  return (
    <div className="geolocation-detail">
      <TextField
        fieldPath={`${basePath}.place`}
        label={i18next.t("Name")}
        placeholder={i18next.t("e.g. Prague, Czechia")}
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
        <NominatimSearchBar basePath={basePath} />
      </Form.Field>

      {isLocationPoint && (
        <GroupField widths="equal">
          <TextField
            fieldPath={`${basePath}.place`}
            placeholder="Latitude"
            label="Latitude"
          />
          <TextField
            fieldPath={`${basePath}.country`}
            placeholder="Longitude"
            label="Longitude"
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
