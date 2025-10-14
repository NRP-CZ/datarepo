import React from "react";
import { Card, Grid } from "semantic-ui-react";
import {
  PreviewButton,
  SaveButton,
  DeleteButton,
  useSanitizeInput,
} from "@js/oarepo_ui";
import { ClipboardCopyButton } from "@js/oarepo_ui/components/ClipboardCopyButton";
import { i18next } from "@translations/i18next";
import { useFormikContext } from "formik";
import { save, setErrors } from "@js/oarepo_ui/forms/state/deposit/actions";
import { connect } from "react-redux";

const FormActionsContainerComponent = ({ saveAction, setErrorsAction }) => {
  const { values } = useFormikContext();

  const { sanitizeInput } = useSanitizeInput();

  let repositoryAssignedDoi = values?.pids?.doi?.identifier;
  // UI serialization is not passed to the form, so I think this is OK, as it is the only
  // thing we need here currently - maybe in the future we could send the UI seiralization
  // of record to form config
  if (repositoryAssignedDoi && !repositoryAssignedDoi.startsWith("https")) {
    repositoryAssignedDoi = `https://doi.org/${repositoryAssignedDoi}`;
  }

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
            <DeleteButton />
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
  setErrorsAction: (errors, formFeedbackMessage) =>
    dispatch(setErrors(errors, formFeedbackMessage)),
});

export default connect(null, mapDispatchToProps)(FormActionsContainerComponent);
