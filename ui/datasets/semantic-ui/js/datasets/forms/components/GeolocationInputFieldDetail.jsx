import React, { useState } from "react";
import PropTypes from "prop-types";
import { TextAreaField, FieldLabel } from "react-invenio-forms";
import { TextField } from "@js/oarepo_ui/forms";
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
import { WktEditor } from "./WktEditor";

export function GeolocationInputFieldDetail({
  basePath,
  handleRemove,
  vocabularies,
  searchValue,
  onSearchValueChange,
  performReverseSearch,
  isReverseLoading,
}) {
  const { values } = useFormikContext();

  const currentGeometryType = getIn(values, `${basePath}.geometry.type`, null);
  const isLocationPoint = currentGeometryType
    ? currentGeometryType === "Point"
    : true;

  const [isManuallyOpened, setIsManuallyOpened] = useState(false);
  const isAdvancedOpen = !isLocationPoint || isManuallyOpened;

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
    <div>
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
        <NominatimSearchBar
          basePath={basePath}
          searchValue={searchValue}
          onSearchValueChange={onSearchValueChange}
        />
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
            setIsManuallyOpened((prev) => !prev);
          }}
        >
          <Icon name="dropdown" />
          {i18next.t("Advanced")}
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
        <Icon name="trash alternate outline" />
        {i18next.t("Remove location")}
      </Button>
    </div>
  );
}

GeolocationInputFieldDetail.propTypes = {
  basePath: PropTypes.string.isRequired,
  handleRemove: PropTypes.func.isRequired,
  vocabularies: PropTypes.object,
  searchValue: PropTypes.string,
  onSearchValueChange: PropTypes.func,
  performReverseSearch: PropTypes.func,
  isReverseLoading: PropTypes.bool,
};
