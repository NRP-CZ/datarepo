import React, { useCallback, useState } from "react";
import PropTypes from "prop-types";
import { i18next } from "@translations/i18next";
import { FieldLabel } from "react-invenio-forms";
import { useFormikContext, getIn } from "formik";
import {
  GridRow,
  GridColumn,
  Grid,
  TabPane,
  Menu,
  Button,
  Icon,
} from "semantic-ui-react";
import { GeolocationInputFieldDetail } from "./GeolocationInputFieldDetail";
import { GeolocationInteractiveMap } from "./GeolocationInteractiveMap";
import debounce from "lodash/debounce";
import { useUpdateLocationName } from "../hooks/useUpdateLocationName";
import { useNominatim } from "../hooks/useNominatim";

function GeolocationInputFieldBody({ fieldPath, label, icon, children }) {
  return (
    <div>
      <FieldLabel htmlFor={fieldPath} label={label} icon={icon} />
      <label className="helptext">
        {i18next.t(
          "Add geolocations for your record. You can use the interactive map or search for the place.",
        )}
      </label>
      <div className="rel-pt-1">{children}</div>
    </div>
  );
}

GeolocationInputFieldBody.propTypes = {
  fieldPath: PropTypes.string.isRequired,
  label: PropTypes.string.isRequired,
  icon: PropTypes.string.isRequired,
};

export function GeolocationsInputField({
  fieldPath,
  label,
  icon,
  identifiersScheme,
}) {
  const { reverseLocation, isLoading: isReverseLoading } = useNominatim();
  const { updateLocationName } = useUpdateLocationName();

  const [searchValue, setSearchValue] = useState("");
  const [activeTabIndex, setActiveTabIndex] = useState(0);

  const { values, setFieldValue } = useFormikContext();
  const currentLocations = getIn(values, `${fieldPath}.features`, []);

  const updateLocationGeometry = useCallback(
    (geometry) => {
      setFieldValue(
        `${fieldPath}.features.${activeTabIndex}.geometry`,
        geometry,
      );
    },
    [fieldPath, activeTabIndex, setFieldValue],
  );

  const activeGeometry = currentLocations[activeTabIndex]?.geometry ?? null;

  const performReverseSearch = useCallback(
    debounce(async (lat, lon) => {
      if (lat && lon && !isNaN(lat) && !isNaN(lon)) {
        const result = await reverseLocation(lat, lon);
        if (result && result.display_name) {
          const placeName = result.name ? result.name : result.display_name;
          updateLocationName(fieldPath, activeTabIndex, placeName);
          setSearchValue(result.display_name);
        }
      }
    }, 600),
    [reverseLocation, setFieldValue, setSearchValue, fieldPath, activeTabIndex],
  );

  const handleAddLocation = useCallback(() => {
    setFieldValue(fieldPath, { features: [...currentLocations, {}] });
    setActiveTabIndex(currentLocations.length);
  }, [currentLocations, setFieldValue, fieldPath]);

  const handleRemoveLocation = useCallback(
    (indexToRemove) => {
      const updatedLocations = currentLocations.filter(
        (_, index) => index !== indexToRemove,
      );
      if (updatedLocations.length == 0) {
        setFieldValue(fieldPath, null);
      } else {
        setFieldValue(fieldPath, { features: updatedLocations });
      }
      setActiveTabIndex(0);
    },
    [currentLocations, setFieldValue, fieldPath],
  );

  const handleTabChange = useCallback(
    (_, { activeIndex: clickedIndex }) => {
      if (clickedIndex === currentLocations.length) {
        handleAddLocation();
      } else {
        setActiveTabIndex(clickedIndex);
      }
      setSearchValue("");
    },
    [currentLocations, handleAddLocation, setActiveTabIndex, setSearchValue],
  );

  const onGeometryChangeHandler = useCallback(
    (geometry) => {
      updateLocationGeometry(geometry);
      if (!geometry) {
        updateLocationName(fieldPath, activeTabIndex, "");
        setSearchValue("");
      } else if (geometry?.type === "Point") {
        const [lon, lat] = geometry.coordinates;
        performReverseSearch(lat, lon);
      } else {
        setSearchValue("");
      }
    },
    [
      fieldPath,
      activeTabIndex,
      setFieldValue,
      performReverseSearch,
      setSearchValue,
    ],
  );

  if (currentLocations.length === 0) {
    return (
      <GeolocationInputFieldBody
        fieldPath={fieldPath}
        label={label}
        icon={icon}
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

  return (
    <GeolocationInputFieldBody fieldPath={fieldPath} label={label} icon={icon}>
      <Menu
        secondary
        pointing
        style={{
          paddingBottom: "10px",
          display: "flex",
          flexWrap: "nowrap",
          overflowX: "auto",
          overflowY: "hidden",
        }}
      >
        {currentLocations.map((location, index) => (
          <Menu.Item
            key={index}
            active={activeTabIndex === index}
            onClick={(e) => handleTabChange(e, { activeIndex: index })}
          >
            <span
              style={{
                maxWidth: "170px",
                whiteSpace: "nowrap",
                overflow: "hidden",
                textOverflow: "ellipsis",
              }}
            >
              {location.place || `${i18next.t("Location")} ${index + 1}`}
            </span>
          </Menu.Item>
        ))}
        <Menu.Item
          key="add"
          active={activeTabIndex === currentLocations.length}
          onClick={(e) =>
            handleTabChange(e, { activeIndex: currentLocations.length })
          }
        >
          +
        </Menu.Item>
      </Menu>

      <Grid columns="two" divided>
        <GridRow>
          <GridColumn>
            {currentLocations[activeTabIndex] && (
              <TabPane>
                <GeolocationInputFieldDetail
                  key={`${fieldPath}.features.${activeTabIndex}`}
                  fieldPath={fieldPath}
                  basePath={`${fieldPath}.features.${activeTabIndex}`}
                  activeTabIndex={activeTabIndex}
                  handleRemove={() => handleRemoveLocation(activeTabIndex)}
                  identifiersScheme={identifiersScheme}
                  searchValue={searchValue}
                  onSearchValueChange={setSearchValue}
                  performReverseSearch={performReverseSearch}
                  isReverseLoading={isReverseLoading}
                />
              </TabPane>
            )}
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
  identifiersScheme: PropTypes.object,
};
