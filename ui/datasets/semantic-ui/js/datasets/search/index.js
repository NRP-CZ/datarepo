import {
  parseSearchAppConfigs,
  createSearchAppsInit,
  SearchAppFacets,
  SearchAppLayout,
} from "@js/oarepo_ui/search";
import ResultsListItem from "./ResultsListItem";
import { parametrize } from "react-overridable";
import { i18next } from "@translations/i18next";

const [{ overridableIdPrefix }] = parseSearchAppConfigs();

const SearchAppFacetsWithTitle = parametrize(SearchAppFacets, {
  title: i18next.t("Data Catch-all Repository"),
});

const SearchAppLayoutWithTip = parametrize(SearchAppLayout, {
  searchBarTip: i18next.t(
    "TIP: Most of the content is in English. You will get more results by using English terms.",
  ),
});

export const componentOverrides = {
  [`${overridableIdPrefix}.ResultsList.item`]: ResultsListItem,
  [`${overridableIdPrefix}.SearchApp.facets`]: SearchAppFacetsWithTitle,
  [`${overridableIdPrefix}.SearchApp.layout`]: SearchAppLayoutWithTip,
};

createSearchAppsInit({ componentOverrides });
