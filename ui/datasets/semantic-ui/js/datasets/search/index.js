import React from "react";
import PropTypes from "prop-types";
import {
  parseSearchAppConfigs,
  createSearchAppsInit,
  SearchAppFacets,
} from "@js/oarepo_ui/search";
import ResultsListItem from "./ResultsListItem";
import { parametrize } from "react-overridable";
import { i18next } from "@translations/i18next";

const [{ overridableIdPrefix }] = parseSearchAppConfigs();

const SearchAppFacetsWithTitle = parametrize(SearchAppFacets, {
  title: i18next.t("Data Catch-all Repository"),
});

export const componentOverrides = {
  [`${overridableIdPrefix}.ResultsList.item`]: ResultsListItem,
  [`${overridableIdPrefix}.SearchApp.facets`]: SearchAppFacetsWithTitle,
};

createSearchAppsInit({ componentOverrides });
