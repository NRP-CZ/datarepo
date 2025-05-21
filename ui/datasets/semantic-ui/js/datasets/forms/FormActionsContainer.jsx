import React from "react";
import { Card, Grid } from "semantic-ui-react";
import {
    PreviewButton,
    SaveButton,
    DeleteButton,
    useDepositApiClient,
    AccessRightField,
    useFormConfig,
    useSanitizeInput,
} from "@js/oarepo_ui";
import { ClipboardCopyButton } from "@js/oarepo_ui/components/ClipboardCopyButton";
import { i18next } from "@translations/i18next";
import { SelectedCommunity } from "@js/communities_components/CommunitySelector/SelectedCommunity";
import { RecordRequests } from "@js/oarepo_requests/components";
import { useFormikContext } from "formik";
import {
    REQUEST_TYPE,
    beforeActionFormErrorPlugin,
} from "@js/oarepo_requests_common";

const FormActionsContainer = () => {
    const { values, setErrors } = useFormikContext();
    const { save } = useDepositApiClient();
    const {
        formConfig: {
            permissions,
            allowRecordRestriction,
            recordRestrictionGracePeriod,
        },
    } = useFormConfig();

    const { sanitizeInput } = useSanitizeInput();

    let repositoryAssignedDoi = values?.pids?.doi?.identifier;
    // UI serialization is not passed to the form, so I think this is OK, as it is the only
    // thing we need here currently - maybe in the future we could send the UI seiralization
    // of record to form config
    if (repositoryAssignedDoi && !repositoryAssignedDoi.startsWith("https")) {
        repositoryAssignedDoi = `https://doi.org/${repositoryAssignedDoi}`;
    }

    const onBeforeAction = ({ requestActionName, requestOrRequestType }) => {
        const requestType =
            requestOrRequestType?.type || requestOrRequestType?.type_id;
        // Do not try to save in case user is declining or cancelling the request from the form
        if (
            requestActionName === REQUEST_TYPE.DECLINE ||
            requestActionName === REQUEST_TYPE.CANCEL ||
            requestType === "initiate_community_migration" ||
            requestType === "confirm_community_migration"
        ) {
            return true;
        } else {
            return save({
                errorMessage: i18next.t(
                    "The request ({{requestType}}) could not be made due to form validation errors. Please fix them and try again:",
                    {
                        requestType:
                            requestOrRequestType?.stateful_name || requestOrRequestType.name,
                    }
                ),
            });
        }
    };
    return (
        <React.Fragment>
            <Card fluid>
                <Card.Content>
                    <Grid>
                        <Grid.Column width={16}>
                            <div className="flex">
                                <SaveButton fluid className="mb-10" />
                                <PreviewButton fluid className="mb-10" />
                            </div>
                            <RecordRequests
                                record={values}
                                onBeforeAction={onBeforeAction}
                                onErrorPlugins={[beforeActionFormErrorPlugin]}
                                actionExtraContext={{ setErrors }}
                            />
                            <DeleteButton redirectUrl="/me/records" />
                        </Grid.Column>
                        <Grid.Column width={16} className="pt-10">
                            <SelectedCommunity />
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
            <AccessRightField
                label={i18next.t("metadata/accessRights.label")}
                record={values}
                labelIcon="shield"
                fieldPath="access"
                showMetadataAccess={permissions?.can_manage_record_access}
                recordRestrictionGracePeriod={recordRestrictionGracePeriod}
                allowRecordRestriction={allowRecordRestriction}
            />
        </React.Fragment>
    );
};

export default FormActionsContainer;