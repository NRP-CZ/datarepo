// SPDX-FileCopyrightText: 2026 CESNET z.s.p.o.
// SPDX-License-Identifier: MIT

import {
  parseSearchAppConfigs,
  createSearchAppsInit,
  SearchAppFacets,
  SearchAppLayout,
} from "@js/oarepo_ui/search";
import React from "react";
import { Icon } from "semantic-ui-react";
import ResultsListItem from "./ResultsListItem";
import { parametrize } from "react-overridable";
import { i18next } from "@translations/i18next";

const [{ overridableIdPrefix }] = parseSearchAppConfigs();

const SearchAppFacetsWithTitle = parametrize(SearchAppFacets, {
  title: i18next.t("Data Catch-all Repository"),
});

const searchBarTipContent = (
  <>
    {i18next.t(
      "TIP: Most of the content is in English. You will get more results by using English terms."
    )}{" "}
    <a
      className="search-guide-link"
      href="/help/search"
      target="_blank"
      rel="noopener noreferrer"
      title={i18next.t("Search guide")}
    >
      <Icon name="question circle outline" />
      {i18next.t("Search guide")}
    </a>
  </>
);

const SearchAppLayoutWithTip = parametrize(SearchAppLayout, {
  searchBarTip: searchBarTipContent,
});

export const componentOverrides = {
  [`${overridableIdPrefix}.ResultsList.item`]: ResultsListItem,
  [`${overridableIdPrefix}.SearchApp.facets`]: SearchAppFacetsWithTitle,
  [`${overridableIdPrefix}.SearchApp.layout`]: SearchAppLayoutWithTip,
};

createSearchAppsInit({ componentOverrides });
