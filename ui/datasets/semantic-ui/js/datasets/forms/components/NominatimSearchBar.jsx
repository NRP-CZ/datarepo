import React, { useState } from "react";
import PropTypes from "prop-types";
import { i18next } from "@translations/ccmm_invenio";
import { Search } from "semantic-ui-react";
import { useFormikContext } from "formik";

export function NominatimSearchBar({ basePath }) {
  const { setFieldValue } = useFormikContext();
  const [results, setResults] = useState([]);
  const [isLoading, setIsLoading] = useState(false);

  const handleSearchChange = async (e, { value }) => {
    setIsLoading(true);
    // TODO: call nominatim-client here with the `value` as:
    // const nominatimData = await myNominatimClient.search(value);

    const formattedResults = nominatimData.map((item) => ({
      title: item.display_name,
      description: `Lat: ${item.lat}, Lon: ${item.lon}`,
      locationData: item,
    }));

    setResults(formattedResults);
    setIsLoading(false);
  };

  const handleResultSelect = (e, { result }) => {
    setFieldValue(`${basePath}.place`, result.title);
    setFieldValue(`${basePath}.geometry`, {
      type: "Point",
      coordinates: [
        parseFloat(result.locationData.lon),
        parseFloat(result.locationData.lat),
      ],
    });
  };

  return (
    <Search
      loading={isLoading}
      onResultSelect={handleResultSelect}
      onSearchChange={handleSearchChange}
      results={results}
      placeholder={i18next.t("Search for a location...")}
    />
  );
}

NominatimSearchBar.propTypes = {
  basePath: PropTypes.string.isRequired,
};
