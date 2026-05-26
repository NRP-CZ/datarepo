// This file is part of InvenioRDM
// Copyright (C) 2022-2024 CERN.
// Copyright (C) 2024 KTH Royal Institute of Technology.
//
// Invenio RDM is free software; you can redistribute it and/or modify it
// under the terms of the MIT License; see LICENSE file for more details.

// Taken from InvenioAppRDM with fixes for viewLink

import { i18next } from "@translations/i18next";
import _get from "lodash/get";
import React, { useState } from "react";
import Overridable from "react-overridable";
import { SearchItemCreators } from "@js/invenio_app_rdm/utils";
import PropTypes from "prop-types";
import { Item, Label, Icon } from "semantic-ui-react";
import { buildUID } from "react-searchkit";

const MAX_CREATIBUTORS = 6;
const MAX_DESCRIPTION_LENGTH = 300;

function getDescription(result) {
  const additionalDescriptions = _get(
    result,
    "metadata.additional_descriptions",
    [],
  );
  if (additionalDescriptions.length === 0) {
    return "";
  }
  // TODO: hack until we resolve https://linear.app/ducesnet/issue/FE-523/three-letter-language-code-to-search-app-context

  const selectedLanguage = i18next.language === "cs" ? "CES" : "ENG";
  // Try to find description matching current language
  const matchByLang = additionalDescriptions.find(
    (d) => d?.lang?.id?.toLowerCase() === selectedLanguage.toLowerCase(),
  );
  if (matchByLang) return matchByLang.description;

  // Fallback to English
  const matchByEng = additionalDescriptions.find(
    (d) => d?.lang?.id?.toLowerCase() === "eng",
  );
  if (matchByEng) return matchByEng.description;

  // Fallback to first available
  return additionalDescriptions[0].description || "";
}

const ExpandableDescription = ({ description }) => {
  const [expanded, setExpanded] = useState(false);

  if (!description) return null;

  const needsTruncation = description.length > MAX_DESCRIPTION_LENGTH;

  if (!needsTruncation) {
    return <Item.Description>{description}</Item.Description>;
  }

  const displayText = expanded
    ? description
    : description.substring(0, MAX_DESCRIPTION_LENGTH) + "...";

  const toggleExpanded = () => setExpanded((prev) => !prev);

  return (
    <Item.Description className="rel-mb-1 text size small">
      {displayText}
      <button
        type="button"
        className="expand-toggle"
        aria-expanded={expanded}
        aria-label={expanded ? i18next.t("Show less") : i18next.t("Show more")}
        onClick={toggleExpanded}
      >
        <Icon name={expanded ? "chevron up" : "chevron right"} />
      </button>
    </Item.Description>
  );
};

ExpandableDescription.propTypes = {
  description: PropTypes.string,
};

ExpandableDescription.defaultProps = {
  description: "",
};

const ResultsListItem = ({ result, appName }) => {
  const creators = _get(result, "ui.creators.creators", []);
  const contributors = _get(result, "ui.contributors.contributors", []);
  const allCreatibutors = [...creators, ...contributors];
  const displayedCreatibutors = allCreatibutors.slice(0, MAX_CREATIBUTORS);
  const totalCreatibutors = allCreatibutors.length;
  const subjects = _get(result, "metadata.subjects", []);
  const title = _get(result, "metadata.title", i18next.t("No title"));
  const description = getDescription(result);

  const publicationDate = _get(result, "ui.publication_date_l10n_long", "");
  const version = _get(result, "ui.version", null);
  const publisher = _get(result, "metadata.publisher", "");
  const languages = _get(result, "ui.languages", []);
  const accessStatusId = _get(result, "ui.access_status.id", "open");
  const accessStatus = _get(result, "ui.access_status.title_l10n", "Open");
  const accessStatusIcon = _get(result, "ui.access_status.icon", "unlock");
  const isDraft = _get(result, "is_draft", false);

  const viewLink = result?.links?.self_html;
  return (
    <Overridable
      id={buildUID("RecordsResultsListItem.layout", "", appName)}
      result={result}
      key={result.id}
    >
      <Item key={result.id} className="search-result-item">
        <Item.Content>
          {isDraft && (
            <Label className="right floated" horizontal>
              {i18next.t("Draft")}
            </Label>
          )}
          <Item.Header as="h2" className="results-list-item-header rel-mb-1">
            <a href={viewLink}>{title}</a>
          </Item.Header>

          <Item className="creatibutors rel-mb-1">
            <SearchItemCreators
              creators={displayedCreatibutors}
              othersLink={viewLink}
            />
            {totalCreatibutors > MAX_CREATIBUTORS && (
              <span className="ml-5">...</span>
            )}
          </Item>

          {subjects.length > 0 && (
            <Item.Extra className="subjects rel-mb-1">
              {subjects.map((subject) => (
                <Label key={subject.subject} size="small">
                  {subject.subject}
                </Label>
              ))}
            </Item.Extra>
          )}

          <ExpandableDescription description={description} />

          <Item.Extra className="search-result-meta">
            <small>
              {publicationDate && (
                <span>
                  {i18next.t("Published")}: {publicationDate}
                  {version && ` (${i18next.t("Version")} ${version})`}
                </span>
              )}
              {publisher && (
                <span>
                  {" "}
                  | {i18next.t("Publisher")}: {publisher}
                </span>
              )}
              {languages.length > 0 && (
                <span>
                  {" "}
                  | {i18next.t("Language")}:{" "}
                  {languages.map((l) => l.title_l10n).join(", ")}
                </span>
              )}
              {accessStatus && (
                <span>
                  {" "}
                  |{" "}
                  <span className={`access-status ${accessStatusId}`}>
                    {accessStatus}{" "}
                    {accessStatusIcon && <Icon name={accessStatusIcon} />}
                  </span>
                </span>
              )}
            </small>
          </Item.Extra>
        </Item.Content>
      </Item>
    </Overridable>
  );
};

ResultsListItem.propTypes = {
  result: PropTypes.object.isRequired,
  appName: PropTypes.string,
};

ResultsListItem.defaultProps = {
  appName: "",
};

export default Overridable.component("ResultsListItem", ResultsListItem);
