import {
  parseSearchAppConfigs,
  createSearchAppsInit,
} from "@js/oarepo_ui/search";
import ResultsListItem from "./ResultsListItem";
import { Grid } from "semantic-ui-react";
import React from "react";
import { SearchBar } from "@js/invenio_search_ui/components";
import { buildUID } from "react-searchkit";
/** NOTE: This reads configs for any search app present on a page
 *   In HTML/Jinja, a single search app instance is typically represented
@@ -14,13 +15,13 @@ import {
/** NOTE: To customize components in a specific search app instance,
 *   you need to obtain its `overridableIdPrefix` from the corresponding config first
 */
const [{ overridableIdPrefix }] = parseSearchAppConfigs();

const SearchBarContainer = () => (
  <Grid relaxed padded>
    <Grid.Row>
      <Grid.Column width={16}>
        <SearchBar buildUID={buildUID} appName={overridableIdPrefix} />
      </Grid.Column>
    </Grid.Row>
  </Grid>
);

export const componentOverrides = {
  /** NOTE: Then you can then replace any existing search ui
   * component with your own implementation, e.g.:
   */
  [`${overridableIdPrefix}.ResultsList.item`]: ResultsListItem,
  [`${overridableIdPrefix}.SearchApp.searchbarContainer`]: SearchBarContainer,
};

createSearchAppsInit({ componentOverrides });
