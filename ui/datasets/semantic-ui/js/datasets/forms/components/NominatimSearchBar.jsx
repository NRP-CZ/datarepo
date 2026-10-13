import React, {
  useState,
  useCallback,
  useMemo,
  useEffect,
  useRef,
} from "react";
import PropTypes from "prop-types";
import { i18next } from "@translations/i18next";
import { Search, Label } from "semantic-ui-react";
import { useFormikContext } from "formik";
import debounce from "lodash/debounce";
import { useUpdateLocationName } from "../hooks/useUpdateLocationName";
import { useNominatim } from "../hooks/useNominatim";

export function NominatimSearchBar({
  fieldPath,
  basePath,
  activeTabIndex,
  searchValue,
  onSearchValueChange,
}) {
  const { setFieldValue } = useFormikContext();
  const { searchLocation, isLoading, error } = useNominatim();
  const { getUniqueLocationName } = useUpdateLocationName();

  const [results, setResults] = useState([]);

  // Create a reference to track if this specific tab's search bar is still on the screen.
  const isMounted = useRef(true);

  // Mark `isMounted` flag as false on unmount.
  useEffect(() => {
    isMounted.current = true;
    return () => {
      isMounted.current = false;
    };
  }, []);

  const searchNominatim = useMemo(
    () =>
      debounce(async (query, currentFieldPath, currentTabIndex) => {
        if (!query || query.length < 2) {
          if (isMounted.current) {
            setResults([]);
          }
          return;
        }

        const data = await searchLocation(query);

        if (!isMounted.current) return;

        if (!data) {
          setResults([]);
          return;
        }

        const formattedResults = data.map((item) => {
          const uniqueName = getUniqueLocationName(
            currentFieldPath,
            currentTabIndex,
            item.name ? item.name : item.display_name,
          );

          const uniqueDisplayName = getUniqueLocationName(
            currentFieldPath,
            currentTabIndex,
            item.display_name,
          );

          return {
            title: uniqueDisplayName,
            description: `Lat: ${item.lat}, Lon: ${item.lon}`,
            key: item.place_id || `${item.lat}-${item.lon}`,
            lat: item.lat,
            lon: item.lon,
            name: uniqueName,
          };
        });

        if (isMounted.current) {
          setResults(formattedResults);
        }
      }, 600),
    [searchLocation, getUniqueLocationName],
  );

  // Throw away any pending invocation of the debounced search function.
  useEffect(() => {
    return () => {
      searchNominatim.cancel();
    };
  }, [searchNominatim]);

  const handleSearchChange = useCallback(
    (_, { value }) => {
      onSearchValueChange(value);
      searchNominatim(value, fieldPath, activeTabIndex);
    },
    [onSearchValueChange, searchNominatim, fieldPath, activeTabIndex],
  );

  const handleResultSelect = useCallback(
    (_, { result }) => {
      onSearchValueChange(result.title);
      setFieldValue(`${basePath}.place`, result.name);
      setFieldValue(`${basePath}.geometry`, {
        type: "Point",
        coordinates: [parseFloat(result.lon), parseFloat(result.lat)],
      });
    },
    [onSearchValueChange, setFieldValue, basePath],
  );

  return (
    <>
      <Search
        loading={isLoading}
        onResultSelect={handleResultSelect}
        onSearchChange={handleSearchChange}
        results={results}
        value={searchValue ?? ""}
        placeholder={i18next.t("Search for a location...")}
        noResultsMessage={i18next.t("No location found.")}
      />
      {error && <Label pointing prompt content={error} />}
    </>
  );
}

NominatimSearchBar.propTypes = {
  fieldPath: PropTypes.string.isRequired,
  basePath: PropTypes.string.isRequired,
  activeTabIndex: PropTypes.number.isRequired,
  searchValue: PropTypes.string,
  onSearchValueChange: PropTypes.func,
};
