import React, { useCallback, useState } from "react";
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
import { GeolocationInteractiveMap } from "./GeolocationInteractiveMap";
import { useNominatim } from "../hooks/useNominatim";

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
  const { fieldPath } = props;
  const { reverseLocation, isLoading: isReverseLoading } = useNominatim();

  const [searchValue, setSearchValue] = useState("");
  const [activeIndex, setActiveIndex] = useState(0);

  const { values, setFieldValue } = useFormikContext();
  const currentLocations = getIn(values, fieldPath, []);
  const activeGeometry = currentLocations[activeIndex]?.geometry ?? null;

  const performReverseSearch = useCallback(
    async (lat, lon) => {
      if (lat && lon && !isNaN(lat) && !isNaN(lon)) {
        const result = await reverseLocation(lat, lon);
        if (result && result.display_name) {
          const placeName = result.name ? result.name : result.display_name;
          setFieldValue(`${fieldPath}.${activeIndex}.place`, placeName);
          setSearchValue(result.display_name);
        }
      }
    },
    [reverseLocation, setFieldValue, setSearchValue, fieldPath, activeIndex],
  );

  const handleAddLocation = useCallback(() => {
    setFieldValue(fieldPath, [...currentLocations, {}]);
    setActiveIndex(currentLocations.length);
  }, [currentLocations, setFieldValue, fieldPath]);

  const handleRemoveLocation = useCallback(
    (indexToRemove) => {
      const updatedLocations = currentLocations.filter(
        (_, index) => index !== indexToRemove,
      );
      setFieldValue(fieldPath, updatedLocations);
      setActiveIndex(0);
    },
    [currentLocations, setFieldValue, fieldPath],
  );

  const handleTabChange = useCallback(
    (_, { activeIndex: clickedIndex }) => {
      if (clickedIndex === currentLocations.length) {
        handleAddLocation();
      } else {
        setActiveIndex(clickedIndex);
      }
      setSearchValue("");
    },
    [currentLocations, handleAddLocation],
  );

  const onGeometryChangeHandler = useCallback(
    (geometry) => {
      setFieldValue(`${fieldPath}.${activeIndex}.geometry`, geometry);
      if (geometry?.type === "Point") {
        const [lon, lat] = geometry.coordinates;
        performReverseSearch(lat, lon);
      } else {
        setSearchValue("");
      }
    },
    [fieldPath, activeIndex, setFieldValue, performReverseSearch],
  );

  if (currentLocations.length === 0) {
    return (
      <GeolocationInputFieldBody
        fieldPath={fieldPath}
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
          key={`${fieldPath}.${index}`}
          basePath={`${fieldPath}.${index}`}
          handleRemove={() => handleRemoveLocation(index)}
          vocabularies={props.vocabularies}
          searchValue={searchValue}
          onSearchValueChange={setSearchValue}
          performReverseSearch={performReverseSearch}
          isReverseLoading={isReverseLoading}
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
      fieldPath={fieldPath}
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
                  paddingBottom: "10px",
                  display: "flex",
                  flexWrap: "nowrap",
                  overflowX: "auto",
                  overflowY: "hidden",
                },
              }}
            />
          </GridColumn>
          <GridColumn>
            <GeolocationInteractiveMap
              initialMapSettings={{ center: [50, 14], zoom: 4 }}
              geometry={activeGeometry}
              onGeometryChange={onGeometryChangeHandler}
            />
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
  vocabularies: PropTypes.object,
};
