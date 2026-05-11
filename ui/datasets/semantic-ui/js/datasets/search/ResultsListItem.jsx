// This file is part of InvenioRDM
// Copyright (C) 2022-2024 CERN.
// Copyright (C) 2024 KTH Royal Institute of Technology.
//
// Invenio RDM is free software; you can redistribute it and/or modify it
// under the terms of the MIT License; see LICENSE file for more details.

// Taken from InvenioAppRDM with fixes for viewLink

import { i18next } from "@translations/invenio_app_rdm/i18next";
import _get from "lodash/get";
import React, { Component } from "react";
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

  const currentLang = i18next.language;

  // Try to find description matching current language
  const matchByLang = additionalDescriptions.find(
    (d) =>
      d.lang &&
      d.lang.id &&
      d.lang.id.toLowerCase() === currentLang.toLowerCase(),
  );
  if (matchByLang) return matchByLang.description;

  // Fallback to English
  const matchByEng = additionalDescriptions.find(
    (d) => d.lang && d.lang.id && d.lang.id.toLowerCase() === "eng",
  );
  if (matchByEng) return matchByEng.description;

  // Fallback to first available
  return additionalDescriptions[0].description || "";
}

class ExpandableDescription extends Component {
  constructor(props) {
    super(props);
    this.state = { expanded: false };
  }

  render() {
    const { description } = this.props;
    const { expanded } = this.state;

    if (!description) return null;

    const needsTruncation = description.length > MAX_DESCRIPTION_LENGTH;

    if (!needsTruncation) {
      return <Item.Description>{description}</Item.Description>;
    }

    const displayText = expanded
      ? description
      : description.substring(0, MAX_DESCRIPTION_LENGTH) + "...";

    return (
      <Item.Description className="rel-mb-1 text size small">
        {displayText}
        <span
          role="button"
          tabIndex={0}
          style={{ cursor: "pointer", marginLeft: "0.25em" }}
          onClick={() => this.setState({ expanded: !expanded })}
          onKeyDown={(e) => {
            if (e.key === "Enter" || e.key === " ") {
              this.setState({ expanded: !expanded });
            }
          }}
        >
          <Icon name={expanded ? "chevron up" : "chevron right"} />
        </span>
      </Item.Description>
    );
  }
}

ExpandableDescription.propTypes = {
  description: PropTypes.string,
};

ExpandableDescription.defaultProps = {
  description: "",
};

class ResultsListItem extends Component {
  render() {
    const { currentQueryState, result, key, appName } = this.props;

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

    const viewLink = result.links.self_html;
    return (
      <Overridable
        id={buildUID("RecordsResultsListItem.layout", "", appName)}
        result={result}
        key={key}
      >
        <Item key={key ?? result.id} className="search-result-item">
          <Item.Content>
            <Item.Header as="h2" className="theme-primary-text rel-mb-1">
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
                    {i18next.t("Publikováno")}: {publicationDate}
                    {version && ` (${i18next.t("verze")}. ${version})`}
                  </span>
                )}
                {publisher && (
                  <span>
                    {" "}
                    | {i18next.t("Vydavatel")}: {publisher}
                  </span>
                )}
                {languages.length > 0 && (
                  <span>
                    {" "}
                    | {i18next.t("Jazyk")}:{" "}
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
  }
}

ResultsListItem.propTypes = {
  currentQueryState: PropTypes.object,
  result: PropTypes.object.isRequired,
  key: PropTypes.string,
  appName: PropTypes.string,
};

ResultsListItem.defaultProps = {
  key: null,
  currentQueryState: null,
  appName: "",
};

export default Overridable.component("ResultsListItem", ResultsListItem);
