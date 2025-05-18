import * as React from "react";
import {
    useFormConfig,
    FormikStateLogger,
    useFieldData,
    useSanitizeInput,
    FilesField,
} from "@js/oarepo_ui/forms";
import { CommunitySelector } from "@js/communities_components/CommunitySelector/CommunitySelector";
import { LocalVocabularySelectField } from "@js/oarepo_vocabularies";
import { AccordionField, TextField } from "react-invenio-forms";
import { i18next } from "@translations/i18next";
import { useFormikContext, getIn } from "formik";

const FormFieldsContainer = () => {
    const { formConfig, files: recordFiles } = useFormConfig();

    const { getFieldData } = useFieldData();

    const { values, setFieldValue, setFieldTouched } = useFormikContext();
    const { sanitizeInput } = useSanitizeInput();

    return (
        <React.Fragment>
            <CommunitySelector />
            <AccordionField
                includesPaths={["metadata.title", "metadata.languages"]}
                active
                label={i18next.t("Basic information")}
            >
                <TextField
                    optimized
                    fieldPath="metadata.title"
                    {...getFieldData({ fieldPath: "metadata.title" })}
                    onBlur={() => {
                        const cleanedContent = sanitizeInput(
                            getIn(values, "metadata.title")
                        );
                        setFieldValue("metadata.title", cleanedContent);
                        setFieldTouched("metadata.title", true);
                    }}
                />
                <LocalVocabularySelectField
                    optimized
                    fieldPath="metadata.languages"
                    multiple={true}
                    clearable
                    optionsListName="languages"
                    {...getFieldData({
                        fieldPath: "metadata.languages",
                        icon: "language",
                    })}
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