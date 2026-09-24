import React, { useState } from "react";
import PropTypes from "prop-types";
import { i18next } from "@translations/ccmm_invenio";
import { FieldLabel } from "react-invenio-forms";
import { useFormikContext, getIn } from "formik";
import {
  GridRow,
  GridColumn,
  Grid,
  TabPane,
  Tab,
  Button,
  Icon,
} from "semantic-ui-react";
import { GeolocationInputFieldDetail } from "./GeolocationInputFieldDetail";

function GeolocationInputFieldBody(props) {
  return (
    <div className="geolocations-form-section">
      <FieldLabel
        htmlFor={props.fieldPath}
        label={props.label}
        icon={props.icon}
      />
      <label className="helptext">
        {i18next.t(
          "Add geolocations for your record. You can use the interactive map or search for the place.",
        )}
      </label>
      <div style={{ paddingTop: "16px" }}>{props.children}</div>
    </div>
  );
}

GeolocationInputFieldBody.propTypes = {
  fieldPath: PropTypes.string.isRequired,
  label: PropTypes.string.isRequired,
  icon: PropTypes.string.isRequired,
};

export function GeolocationsInputField(props) {
  const { values, setFieldValue } = useFormikContext();
  const currentLocations = getIn(values, props.fieldPath, []);
  const [activeIndex, setActiveIndex] = useState(0);

  const handleAddLocation = () => {
    const newLocationObject = {};
    setFieldValue(props.fieldPath, [...currentLocations, newLocationObject]);
    setActiveIndex(currentLocations.length);
  };

  const handleRemoveLocation = (indexToRemove) => {
    const updatedLocations = currentLocations.filter(
      (_, index) => index !== indexToRemove,
    );
    setFieldValue(props.fieldPath, updatedLocations);
    setActiveIndex(0);
  };

  const handleTabChange = (_, { activeIndex: clickedIndex }) => {
    if (clickedIndex === currentLocations.length) {
      handleAddLocation();
    } else {
      setActiveIndex(clickedIndex);
    }
  };

  if (currentLocations.length === 0) {
    return (
      <GeolocationInputFieldBody
        fieldPath={props.fieldPath}
        label={props.label}
        icon={props.icon}
      >
        <Button
          type="button"
          primary
          icon
          labelPosition="left"
          onClick={handleAddLocation}
        >
          <Icon name="add" />
          {i18next.t("Add location")}
        </Button>
      </GeolocationInputFieldBody>
    );
  }

  const panes = currentLocations.map((location, index) => ({
    menuItem: location.place || i18next.t(`Location ${index + 1}`),
    render: () => (
      <TabPane>
        <GeolocationInputFieldDetail
          key={`${props.fieldPath}.${index}`}
          basePath={`${props.fieldPath}.${index}`}
          handleRemove={() => handleRemoveLocation(index)}
        />
      </TabPane>
    ),
  }));

  panes.push({
    menuItem: "+",
    render: () => <TabPane />,
  });

  return (
    <GeolocationInputFieldBody
      fieldPath={props.fieldPath}
      label={props.label}
      icon={props.icon}
    >
      <Grid columns="two" divided>
        <GridRow>
          <GridColumn>
            <Tab
              panes={panes}
              activeIndex={activeIndex}
              onTabChange={handleTabChange}
              menu={{
                secondary: true,
                pointing: true,
                style: {
                  display: "flex",
                  flexWrap: "nowrap",
                  overflowX: "auto",
                  overflowY: "hidden",
                },
              }}
            />
          </GridColumn>
          <GridColumn>
            <div
              style={{
                border: "blue solid 1px",
                height: "100%",
                minHeight: "500px",
              }}
            ></div>
          </GridColumn>
        </GridRow>
      </Grid>
    </GeolocationInputFieldBody>
  );
}

GeolocationsInputField.propTypes = {
  fieldPath: PropTypes.string.isRequired,
  label: PropTypes.string.isRequired,
  icon: PropTypes.string.isRequired,
};
