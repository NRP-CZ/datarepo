import { useContext } from "react";
import { Sort, ResultsPerPage } from "react-searchkit";
import { Grid } from "semantic-ui-react";
import { SearchConfigurationContext } from "@js/invenio_search_ui/components";
import { i18next } from "@translations/invenio_app_rdm/i18next";
import PropTypes from "prop-types";
import React from "react";

const ResultsPerPageLabel = (cmp) => (
  <>
    <span className="rel-mr-1">{i18next.t("Results per page:")}</span> {cmp}
  </>
);

const SortLabel = (cmp) => (
  <>
    <span className="rel-mr-1">{i18next.t("Sort:")}</span> {cmp}
  </>
);

export const ResultOptions = ({ currentResultsState = {} }) => {
  const { total } = currentResultsState.data;
  const { sortOptions, paginationOptions, sortOrderDisabled } = useContext(
    SearchConfigurationContext,
  );
  if (!total) return null;

  return (
    <>
      <Grid.Column
        textAlign="left"
        mobile={16}
        tablet={3}
        computer={3}
        largeScreen={3}
        widescreen={3}
      >
        <p>
          {i18next.t("Results: ")}
          <strong>{total}</strong>
        </p>
      </Grid.Column>
      <Grid.Column
        textAlign="right"
        mobile={16}
        tablet={13}
        computer={13}
        largeScreen={13}
        widescreen={13}
        floated="right"
      >
        {sortOptions && (
          <Sort
            sortOrderDisabled={sortOrderDisabled || false}
            values={sortOptions}
            ariaLabel={i18next.t("Sort")}
            label={SortLabel}
          />
        )}
        <span className="rel-mr-1" />
        <ResultsPerPage
          values={paginationOptions.resultsPerPage}
          label={ResultsPerPageLabel}
        />
      </Grid.Column>
    </>
  );
};

ResultOptions.propTypes = {
  currentResultsState: PropTypes.object,
};
