import PropTypes from "prop-types";
import React from "react";
import _groupBy from "lodash/groupBy";
import _map from "lodash/map";
import { Label, Icon } from "semantic-ui-react";
import { withState } from "react-searchkit";
import { ClearFiltersButton } from "@js/oarepo_ui";
import { useActiveSearchFilters } from "@js/oarepo_ui/search/hooks";
import { i18next } from "@translations/invenio_app_rdm/i18next";

const getLabel = (filter, aggregations, additionalFilterLabels) => {
  const aggName = filter[0];
  const value = filter[1];

  const aggLabel =
    aggregations[aggName]?.label ||
    additionalFilterLabels[aggName]?.label ||
    aggName;

  const _getValueLabel = (aggs) =>
    aggs[aggName]?.buckets?.find((b) => b.key === value)?.label;

  const valueLabel =
    _getValueLabel(aggregations) ||
    _getValueLabel(additionalFilterLabels) ||
    value;

  let currentFilter = [aggName, value];
  const hasChild = filter.length === 3;
  if (hasChild) {
    const { activeFilter } = getLabel(
      filter[2],
      aggregations,
      additionalFilterLabels,
    );
    currentFilter.push(activeFilter);
  }
  return {
    label: `${aggLabel}: ${valueLabel}`,
    activeFilter: currentFilter,
  };
};
const ActiveFiltersElementComponent = ({
  filters,
  removeActiveFilter,
  currentResultsState: {
    data: { aggregations },
  },
}) => {
  const { activeSearchFilters, additionalFilterLabels } =
    useActiveSearchFilters(filters);
  const groupedData = _groupBy(activeSearchFilters, 0);
  return (
    <>
      <ClearFiltersButton
        content={i18next.t("Delete All")}
        icon={null}
        labelPosition={null}
        size="tiny"
        compact
      />
      {_map(groupedData, (filters, key) =>
        filters.map((filter, index) => {
          const { label, activeFilter } = getLabel(
            filter,
            aggregations,
            additionalFilterLabels,
          );
          return (
            <Label
              className="active-filter-label"
              key={activeFilter}
              onClick={() => removeActiveFilter(activeFilter)}
              type="button"
              tabIndex="0"
              aria-label={`Remove filter ${label}`}
              onKeyPress={(e) => {
                if (e.key === "Enter" || e.key === " ") {
                  removeActiveFilter(activeFilter);
                }
              }}
            >
              {label || filter[1]}
              <Icon name="delete" aria-hidden="true" />
            </Label>
          );
        }),
      )}
    </>
  );
};

export const ActiveFiltersElement = withState(ActiveFiltersElementComponent);

ActiveFiltersElementComponent.propTypes = {
  filters: PropTypes.array,
  removeActiveFilter: PropTypes.func.isRequired,
  currentResultsState: PropTypes.shape({
    data: PropTypes.shape({
      aggregations: PropTypes.object,
    }).isRequired,
  }).isRequired,
};
