import React, { useState, useCallback } from "react";
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
import { i18next } from "@translations/i18next";
import { IdentifiersField } from "@js/invenio_rdm_records";
import { NominatimSearchBar } from "./NominatimSearchBar";
import { GeoJsonEditor } from "./GeoJsonEditor";
import { LongitudeAndLatitudeGroupField } from "./LongitudeAndLatitudeGroupField";
import { WktEditor } from "./WktEditor";
import { useUpdateLocationName } from "../hooks/useUpdateLocationName";

export function GeolocationInputFieldDetail({
  fieldPath,
  basePath,
  activeTabIndex,
  handleRemove,
  identifiersScheme,
  searchValue,
  onSearchValueChange,
  performReverseSearch,
  isReverseLoading,
}) {
  const { values, setFieldValue } = useFormikContext();
  const { updateLocationName } = useUpdateLocationName();

  const [description, setDescription] = useState(
    getIn(values, `${basePath}.description`, null),
  );

  const currentGeometryType = getIn(values, `${basePath}.geometry.type`, null);
  const isLocationPoint = currentGeometryType
    ? currentGeometryType === "Point"
    : true;

  // Value `null` signals the initial state, and therefore, the value of `isAdvancedOpen` is derived only from the fact if geometry type is Point or not.
  const [isManuallyOpened, setIsManuallyOpened] = useState(null);
  const isAdvancedOpen = isManuallyOpened ?? !isLocationPoint;

  const handleNameBlur = useCallback(
    (e) => {
      const typedName = e.target.value;
      if (typedName) {
        updateLocationName(fieldPath, activeTabIndex, typedName);
      }
    },
    [updateLocationName],
  );

  const handleDescriptionChange = useCallback(
    (e) => {
      const typedDescription = e.target.value;
      if (typedDescription) {
        setDescription(typedDescription);
      }
    },
    [setDescription],
  );

  const handleDescriptionBlur = useCallback(
    (e) => {
      const typedDescription = e.target.value;
      if (typedDescription) {
        setFieldValue(`${basePath}.description`, typedDescription);
      }
    },
    [setFieldValue],
  );

  const panes = [
    {
      menuItem: "GeoJSON",
      render: () => (
        <TabPane attached={false} style={{ border: "none", boxShadow: "none" }}>
          <GeoJsonEditor
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
        onBlur={handleNameBlur}
      />

      <TextAreaField
        label={i18next.t("Description")}
        placeholder={i18next.t("Additional details about this location...")}
        onChange={handleDescriptionChange}
        onBlur={handleDescriptionBlur}
        value={description ?? ""}
        rows={5}
      />

      <IdentifiersField
        fieldPath={`${basePath}.identifiers`}
        label={i18next.t("Identifiers")}
        labelIcon={""}
        schemeOptions={identifiersScheme}
        showEmptyValue
      />

      <Form.Field>
        <FieldLabel
          htmlFor={`${basePath}.search`}
          label={i18next.t("Location")}
        />
        <NominatimSearchBar
          fieldPath={fieldPath}
          basePath={basePath}
          activetabIndex={activeTabIndex}
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
            setIsManuallyOpened(!isAdvancedOpen);
          }}
        >
          <Icon
            name={isAdvancedOpen ? "caret down" : "caret right"}
            style={{ transform: "none" }}
          />
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
  fieldPath: PropTypes.string.isRequired,
  basePath: PropTypes.string.isRequired,
  activeTabIndex: PropTypes.number.isRequired,
  handleRemove: PropTypes.func.isRequired,
  identifiersScheme: PropTypes.object,
  searchValue: PropTypes.string,
  onSearchValueChange: PropTypes.func,
  performReverseSearch: PropTypes.func,
  isReverseLoading: PropTypes.bool,
};
