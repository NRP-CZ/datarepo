import React, { useState } from "react";
import PropTypes from "prop-types";
import { TextField, TextAreaField, FieldLabel } from "react-invenio-forms";
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
} from "semantic-ui-react";
import { i18next } from "@translations/ccmm_invenio";
import { IdentifiersField } from "@js/invenio_rdm_records";
import { NominatimSearchBar } from "./NominatimSearchBar";
import { GeoJSsonEditor } from "./GeoJsonEditor";
import { LongitudeAndLatitudeGroupField } from "./LongitudeAndLatitudeGroupField";
import { useNominatim } from "../hooks/useNominatim";
import { WktEditor } from "./WktEditor";

export function GeolocationInputFieldDetail({
  basePath,
  handleRemove,
  vocabularies,
}) {
  const { values, setFieldValue } = useFormikContext();
  const { reverseLocation, isLoading: isReverseLoading } = useNominatim();
  const [searchValue, setSearchValue] = useState("");

  const currentGeometryType = getIn(values, `${basePath}.geometry.type`, null);
  const isLocationPoint = currentGeometryType
    ? currentGeometryType === "Point"
    : true;

  const [isAdvancedOpen, setIsAdvancedOpen] = useState(() => {
    if (currentGeometryType && !isLocationPoint) {
      return true;
    }
    return false;
  });

  const performReverseSearch = async (lat, lon) => {
    if (lat && lon && !isNaN(lat) && !isNaN(lon)) {
      const result = await reverseLocation(lat, lon);
      if (result && result.display_name) {
        const placeName = result.name ? result.name : result.display_name;
        setFieldValue(`${basePath}.place`, placeName);
        setSearchValue(result.display_name);
      }
    }
  };

  const panes = [
    {
      menuItem: "GeoJSON",
      render: () => (
        <TabPane attached={false} style={{ border: "none", boxShadow: "none" }}>
          <GeoJSsonEditor
            basePath={basePath}
            onReverseSearch={performReverseSearch}
          />
        </TabPane>
      ),
    },
    {
      menuItem: "WKT",
      render: () => (
        <TabPane attached={false} style={{ border: "none", boxShadow: "none" }}>
          <WktEditor
            basePath={basePath}
            onReverseSearch={performReverseSearch}
          ></WktEditor>
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
        <LongitudeAndLatitudeGroupField
          basePath={basePath}
          isLoading={isReverseLoading}
          onReverseSearch={performReverseSearch}
        />
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
