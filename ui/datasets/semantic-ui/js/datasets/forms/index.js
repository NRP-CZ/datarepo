import { createFormAppInit, parseFormAppConfig } from "@js/oarepo_ui/forms";
import FormActionsContainer from "./FormActionsContainer";
import FormFieldsContainer from "./FormFieldsContainer";

/** NOTE: This reads configuration for a form app present on a page
 *   In HTML/Jinja, represented by an element with a specific id
 *   (defaults to "form-app").
 *
 *   <div id="form-app" />
 */
const { formConfig } = parseFormAppConfig();

/** NOTE: To customize components in a specific form app instance,
 *   you need to obtain its `overridableIdPrefix` from the corresponding config first
 */
const { overridableIdPrefix } = formConfig;

export const componentOverrides = {
  /** NOTE: Then you can then replace any existing ui
   * component with your own implementation, e.g.:
   */
  [`${overridableIdPrefix}.FormActions.container`]: FormActionsContainer,
  [`${overridableIdPrefix}.FormFields.container`]: FormFieldsContainer,
};

createFormAppInit({ componentOverrides });