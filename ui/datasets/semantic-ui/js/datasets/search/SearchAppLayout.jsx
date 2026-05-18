import React, { useContext, useState, useEffect } from "react";
import PropTypes from "prop-types";
import _isEmpty from "lodash/isEmpty";
import { withState, ActiveFilters, SearchBar } from "react-searchkit";
import { GridResponsiveSidebarColumn } from "react-invenio-forms";
import {
  Container,
  Grid,
  Button,
  Icon,
  TransitionablePortal,
  Header,
} from "semantic-ui-react";
import { i18next } from "@translations/i18next";
import {
  SearchAppFacets,
  SearchAppResultsPane,
  SearchConfigurationContext,
} from "@js/invenio_search_ui/components";
import { ResultOptions } from "./ResultOptions";
import {
  ShouldActiveFiltersRender,
  ActiveFiltersCountFloatingLabel,
} from "@js/oarepo_ui/search";

const ResultOptionsWithState = withState(ResultOptions);

export const SearchAppResultsGrid = ({
  columnsAmount,
  facetsAvailable,
  config,
  appName,
  buildUID,
  resultsPaneLayout,
}) => {
  const [sidebarVisible, setSidebarVisible] = useState(false);

  const searchInputProps = {
    clearable: true,
  };

  return (
    <Grid
      columns={columnsAmount}
      relaxed
      className="search-app rel-mt-2"
      padded
    >
      {facetsAvailable && (
        <GridResponsiveSidebarColumn
          mobile={4}
          tablet={4}
          computer={4}
          largeScreen={4}
          widescreen={4}
          open={sidebarVisible}
          onHideClick={() => setSidebarVisible(false)}
        >
          <Header as="h3" className="facets-heading">
            {i18next.t("Data Catch-all Repository")}
          </Header>
          <SearchAppFacets
            aggs={config.aggs}
            appName={appName}
            buildUID={buildUID}
          />
        </GridResponsiveSidebarColumn>
      )}
      <Grid.Column {...resultsPaneLayout}>
        <Grid className="subgrid">
          <Grid.Row>
            {facetsAvailable && (
              <Grid.Column
                floated="left"
                only="mobile tablet"
                mobile={2}
                tablet={2}
                textAlign="center"
              >
                <Button
                  basic
                  onClick={() => setSidebarVisible(true)}
                  title={i18next.t("Filter results")}
                  aria-label={i18next.t("Filter results")}
                  className="facets-sidebar-open-button"
                >
                  <Icon name="filter" />
                  <ShouldActiveFiltersRender>
                    <ActiveFiltersCountFloatingLabel />
                  </ShouldActiveFiltersRender>
                </Button>
              </Grid.Column>
            )}
            <Grid.Column width={14} floated="right" only="mobile tablet">
              <SearchBar
                buildUID={buildUID}
                appName={appName}
                uiProps={searchInputProps}
              />
            </Grid.Column>
            <Grid.Column width={16} floated="right" only="computer">
              <SearchBar
                buildUID={buildUID}
                appName={appName}
                uiProps={searchInputProps}
              />
            </Grid.Column>
          </Grid.Row>
          <ShouldActiveFiltersRender>
            <Grid.Row only="computer tablet">
              <Grid.Column>
                <ActiveFilters />
              </Grid.Column>
            </Grid.Row>
          </ShouldActiveFiltersRender>
          <Grid.Row verticalAlign="middle" className="result-options pb-0">
            <ResultOptionsWithState />
          </Grid.Row>
          <Grid.Row verticalAlign="middle">
            <Grid.Column
              as="section"
              aria-label={i18next.t("Search results")}
              width={16}
            >
              <SearchAppResultsPane
                layoutOptions={config.layoutOptions}
                appName={appName}
                buildUID={buildUID}
              />
            </Grid.Column>
          </Grid.Row>
        </Grid>
      </Grid.Column>
    </Grid>
  );
};

SearchAppResultsGrid.propTypes = {
  columnsAmount: PropTypes.number.isRequired,
  facetsAvailable: PropTypes.bool.isRequired,
  config: PropTypes.shape({
    aggs: PropTypes.array.isRequired,
    layoutOptions: PropTypes.object,
  }).isRequired,
  appName: PropTypes.string.isRequired,
  buildUID: PropTypes.func.isRequired,
  resultsPaneLayout: PropTypes.object.isRequired,
};

export const SearchAppLayout = ({ config }) => {
  const { appName, buildUID } = useContext(SearchConfigurationContext);
  const facetsAvailable = !_isEmpty(config.aggs);
  let columnsAmount;
  let resultsPaneLayoutFacets;

  const [scrollToTopVisible, setScrollToTopVisible] = React.useState(false);

  useEffect(() => {
    const handleScrollButtonVisibility = () => {
      window.scrollY > 300
        ? setScrollToTopVisible(true)
        : setScrollToTopVisible(false);
    };

    window.addEventListener("scroll", handleScrollButtonVisibility);

    return () => {
      window.removeEventListener("scroll", handleScrollButtonVisibility);
    };
  }, []);

  const scrollToTop = () => {
    window.scrollTo({ top: 0, behavior: "smooth" });
  };

  if (facetsAvailable) {
    columnsAmount = 2;
    resultsPaneLayoutFacets = {
      mobile: 16,
      tablet: 16,
      computer: 12,
      largeScreen: 12,
      widescreen: 12,
      width: undefined,
    };
  } else {
    columnsAmount = 1;
    resultsPaneLayoutFacets = {
      mobile: 16,
      tablet: 16,
      computer: 16,
      largeScreen: 16,
      widescreen: 16,
      width: undefined,
    };
  }

  const resultsSortLayoutFacets = {
    mobile: 14,
    tablet: 14,
    computer: 5,
    largeScreen: 5,
    widescreen: 5,
  };

  const resultsSortLayoutNoFacets = {
    mobile: 16,
    tablet: 16,
    computer: 16,
    largeScreen: 16,
    widescreen: 16,
  };

  const resultsPaneLayoutNoFacets = resultsPaneLayoutFacets;

  const resultsPaneLayout = facetsAvailable
    ? resultsPaneLayoutFacets
    : resultsPaneLayoutNoFacets;

  const resultSortLayout = facetsAvailable
    ? resultsSortLayoutFacets
    : resultsSortLayoutNoFacets;

  return (
    <Container fluid>
      <SearchAppResultsGrid
        columnsAmount={columnsAmount}
        facetsAvailable={facetsAvailable}
        config={config}
        appName={appName}
        buildUID={buildUID}
        resultsPaneLayout={resultsPaneLayout}
      />
      <TransitionablePortal
        open={scrollToTopVisible}
        transition={{ animation: "fade up", duration: 300 }}
      >
        <Button onClick={scrollToTop} id="scroll-to-top-button" icon>
          <Icon size="large" name="chevron up" />
        </Button>
      </TransitionablePortal>
    </Container>
  );
};

SearchAppLayout.propTypes = {
  config: PropTypes.shape({
    searchApi: PropTypes.object.isRequired,
    initialQueryState: PropTypes.shape({
      queryString: PropTypes.string,
      sortBy: PropTypes.string,
      sortOrder: PropTypes.string,
      page: PropTypes.number,
      size: PropTypes.number,
      hiddenParams: PropTypes.array,
      layout: PropTypes.oneOf(["list", "grid"]),
    }),
    aggs: PropTypes.array,
  }),
};
