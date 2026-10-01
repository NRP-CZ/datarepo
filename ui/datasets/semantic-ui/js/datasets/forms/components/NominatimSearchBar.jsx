import React, { useState, useCallback } from "react";
import PropTypes from "prop-types";
import { i18next } from "@translations/i18next";
import { Search, Label } from "semantic-ui-react";
import { useFormikContext } from "formik";
import debounce from "lodash/debounce";
import { useNominatim } from "../hooks/useNominatim";

export function NominatimSearchBar({ basePath, searchValue, onSearchValueChange }) {
  const { setFieldValue } = useFormikContext();
  const { searchLocation, isLoading, error } = useNominatim();
  const [results, setResults] = useState([]);

  const searchNominatim = useCallback(
    debounce(async (query) => {
      if (!query || query.length < 2) {
        setResults([]);
        return;
      }

      const data = await searchLocation(query);

      if (!data) {
        setResults([]);
        return;
      }

      const formattedResults = data.map((item) => ({
        title: item.display_name,
        description: `Lat: ${item.lat}, Lon: ${item.lon}`,
        key: item.place_id || `${item.lat}-${item.lon}`,
        lat: item.lat,
        lon: item.lon,
        bbox: item.boundingBox,
        name: item.name ? item.name : item.display_name,
      }));

      setResults(formattedResults);
    }, 600),
    [],
  );

  const handleSearchChange = useCallback((_, { value }) => {
    onSearchValueChange(value);
    searchNominatim(value);
  }, [onSearchValueChange, searchNominatim]);

  const handleResultSelect = useCallback((_, { result }) => {
    onSearchValueChange(result.title);
    setFieldValue(`${basePath}.place`, result.name);
    setFieldValue(`${basePath}.geometry`, {
      type: "Point",
      coordinates: [parseFloat(result.lon), parseFloat(result.lat)],
    });
  }, [onSearchValueChange, setFieldValue]);

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
  basePath: PropTypes.string.isRequired,
  searchValue: PropTypes.string,
  onSearchValueChange: PropTypes.func,
};
