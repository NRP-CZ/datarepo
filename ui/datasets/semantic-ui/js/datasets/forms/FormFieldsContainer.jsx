import * as React from "react";
import {
    useFormConfig,
    FormikStateLogger,
    FilesField,
    TextField,
} from "@js/oarepo_ui/forms";
import { CommunitySelector } from "@js/communities_components/CommunitySelector/CommunitySelector";
import { LocalVocabularySelectField } from "@js/oarepo_vocabularies";
import { AccordionField } from "react-invenio-forms";
import { i18next } from "@translations/i18next";

const FormFieldsContainer = () => {
    const { formConfig, files: recordFiles } = useFormConfig();

    return (
        <React.Fragment>
            <CommunitySelector />
            <AccordionField
                includesPaths={["metadata.title", "metadata.languages"]}
                active
                label={i18next.t("Basic information")}
            >
                <TextField fieldPath="metadata.title" />
                <LocalVocabularySelectField
                    fieldPath="metadata.languages"
                    optionsListName="languages"
                />
            </AccordionField>
            <AccordionField
                includesPaths={["files.enabled"]}
                active
                label={
                    <label htmlFor="files.enabled">{i18next.t("Files upload")}</label>
                }
                data-testid="filesupload-button"
            >
                <FilesField
                    recordFiles={recordFiles}
                    allowedFileTypes={formConfig.allowed_file_extensions}
                />
            </AccordionField>
            {process.env.NODE_ENV === "development" && <FormikStateLogger />}
        </React.Fragment>
    );
};

export default FormFieldsContainer;