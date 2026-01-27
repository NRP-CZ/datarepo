import React from "react";
import { Card, Grid } from "semantic-ui-react";
import {
  PreviewButton,
  SaveButton,
  DeleteButton,
  AccessRightField,
  useFormConfig,
  useSanitizeInput,
} from "@js/oarepo_ui";
import { ClipboardCopyButton } from "@js/oarepo_ui/components/ClipboardCopyButton";
import { i18next } from "@translations/i18next";
import { RecordRequests } from "@js/oarepo_requests/components";
import { useFormikContext } from "formik";
import {
  REQUEST_TYPE,
  beforeActionFormErrorPlugin,
} from "@js/oarepo_requests_common";
import { connect } from "react-redux";
import { useDepositFormAction } from "@js/oarepo_ui/forms/hooks";
import { save } from "@js/oarepo_ui/forms/state/deposit/actions";

const FormActionsContainerComponent = ({ saveAction }) => {
  const { values, setErrors } = useFormikContext();
  const {
    config: {
      permissions,
      allowRecordRestriction,
      recordRestrictionGracePeriod,
    },
  } = useFormConfig();

  const { sanitizeInput } = useSanitizeInput();
  const { handleAction: handleSave, isSubmitting } = useDepositFormAction({
    action: saveAction,
  });
  let repositoryAssignedDoi = values?.pids?.doi?.identifier;
  // UI serialization is not passed to the form, so I think this is OK, as it is the only
  // thing we need here currently - maybe in the future we could send the UI seiralization
  // of record to form config
  if (repositoryAssignedDoi && !repositoryAssignedDoi.startsWith("https")) {
    repositoryAssignedDoi = `https://doi.org/${repositoryAssignedDoi}`;
  }

  const onBeforeAction = async ({ action, requestOrRequestType }) => {
    const response = await handleSave();
    console.log(response, "responseresponse");
    if (!response || response?.errors) {
      return false;
    }
    return true;
  };
  return (
    <Card fluid>
      {/* <Card.Content>
            <DepositStatusBox />
          </Card.Content> */}
      <Card.Content>
        <Grid>
          <Grid.Column width={16}>
            <div className="flex">
              <SaveButton fluid className="mb-10" />
              <PreviewButton fluid className="mb-10" />
            </div>
            <RecordRequests
              record={values}
              // onErrorPlugins={[beforeActionFormErrorPlugin]}
              // actionExtraContext={{ setErrors }}
              onBeforeAction={onBeforeAction}
            />
            <DeleteButton redirectUrl="/me/records" />
          </Grid.Column>

          {repositoryAssignedDoi && (
            <Grid.Column width={16} className="pt-10">
              <p>{i18next.t("Assigned DOI:")}</p>
              <a
                href={sanitizeInput(repositoryAssignedDoi)}
                target="_blank"
                rel="noreferrer noopener"
              >
                {repositoryAssignedDoi}
              </a>{" "}
              <ClipboardCopyButton copyText={repositoryAssignedDoi} />
            </Grid.Column>
          )}
        </Grid>
      </Card.Content>
    </Card>
  );
};

const mapDispatchToProps = (dispatch) => ({
  saveAction: (values, params) => dispatch(save(values, params)),
});

const mapStateToProps = (state) => ({
  actionState: state.deposit.actionState,
});

export const FormActionsContainer = connect(
  mapStateToProps,
  mapDispatchToProps
)(FormActionsContainerComponent);
export default FormActionsContainer;
