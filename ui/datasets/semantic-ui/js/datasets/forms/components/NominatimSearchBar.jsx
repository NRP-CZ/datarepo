import React, { useState, useCallback, useEffect } from "react";
import PropTypes from "prop-types";
import { i18next } from "@translations/ccmm_invenio";
import { Search, Label } from "semantic-ui-react";
import { useFormikContext } from "formik";
import debounce from "lodash/debounce";
import { useNominatim } from "../hooks/useNominatim";

export function NominatimSearchBar(props) {
  const { setFieldValue } = useFormikContext();
  const { searchLocation, isLoading, error } = useNominatim();
  const [results, setResults] = useState([]);
  const [searchValue, setSearchValue] = useState(props.searchValue ?? "");

  useEffect(() => {
    setSearchValue(props.searchValue ?? "");
  }, [props.searchValue]);

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

  const handleSearchChange = (_, { value }) => {
    setSearchValue(value);
    searchNominatim(value);
  };

  const handleResultSelect = (_, { result }) => {
    setSearchValue(result.title);
    setFieldValue(`${props.basePath}.place`, result.name);
    setFieldValue(`${props.basePath}.geometry`, {
      type: "Point",
      coordinates: [parseFloat(result.lon), parseFloat(result.lat)],
    });
  };

  return (
    <>
      <Search
        loading={isLoading}
        onResultSelect={handleResultSelect}
        onSearchChange={handleSearchChange}
        results={results}
        value={searchValue}
        placeholder={i18next.t("Search for a location...")}
      />
      {error && <Label pointing prompt content={error} />}
    </>
  );
}

NominatimSearchBar.propTypes = {
  basePath: PropTypes.string.isRequired,
  searchValue: PropTypes.string,
};
