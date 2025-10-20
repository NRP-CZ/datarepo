import * as React from "react";
import {
  useFormConfig,
  FormikStateLogger,
  TextField,
  EDTFSingleDatePicker,
  CreatibutorsField,
  CreatibutorField,
} from "@js/oarepo_ui/forms";
import { AccordionField } from "react-invenio-forms";
import { i18next } from "@translations/i18next";
import { UppyUploader, TitlesField } from "@js/invenio_rdm_records";
import { connect } from "react-redux";
import PropTypes from "prop-types";
import { LanguagesField } from "@js/invenio_rdm_records";
import { RemoteSelectField } from "./RemoteSelectField";

const severityChecksConfig = {
  info: {
    label: i18next.t("Recommendation"),
    description: i18next.t("This check is recommended but not mandatory."),
  },
  error: {
    label: i18next.t("Error"),
    description: i18next.t(
      "This check indicates a critical issue that must be addressed."
    ),
  },
};

const alternativeTitleOptions = {
  type: [
    { text: i18next.t("Alternative title"), value: "alternative-title" },
    { text: i18next.t("Translated title"), value: "translated-title" },
    { text: i18next.t("Subtitle"), value: "subtitle" },
    { text: i18next.t("Other"), value: "other" },
  ],
};
const FormFieldsContainerComponent = ({ record }) => {
  const formConfig = useFormConfig();
  const { filesLocked } = formConfig;
  console.log(formConfig, "sectionsConfig");
  return (
    <React.Fragment>
      <AccordionField
        includesPaths={["metadata.title", "metadata.publication_date"]}
        active
        label={i18next.t("Basic information")}
        // severityChecks={severityChecksConfig}
      >
        <TextField fieldPath="metadata.version" />
        <TitlesField
          options={alternativeTitleOptions}
          fieldPath="metadata.title"
          recordUI={record.ui}
          required
        />

        <EDTFSingleDatePicker fieldPath="metadata.publication_date" />
      </AccordionField>
      <AccordionField
        includesPaths={["metadata.ccmm_publisher"]}
        active
        label={i18next.t("Publisher information")}
      >
        {/* <CreatibutorField
          fieldPath="metadata.ccmm_publisher"
          schema="creators"
          autocompleteNames="search"
        /> */}
      </AccordionField>
      <AccordionField
        includesPaths={["files.enabled"]}
        active
        label={
          <label htmlFor="files.enabled">{i18next.t("Files upload")}</label>
        }
        data-testid="filesupload-button"
      >
        <UppyUploader
          isDraftRecord={!record.is_published}
          config={formConfig}
          quota={formConfig.quota}
          decimalSizeDisplay={formConfig.decimal_size_display}
          allowEmptyFiles={formConfig.allow_empty_files}
          fileUploadConcurrency={formConfig.file_upload_concurrency}
          showMetadataOnlyToggle={false}
          filesLocked={filesLocked}
        />
      </AccordionField>
      {process.env.NODE_ENV === "development" && <FormikStateLogger />}
    </React.Fragment>
  );
};

FormFieldsContainerComponent.propTypes = {
  record: PropTypes.object.isRequired,
};

const mapStateToProps = (state) => {
  return {
    record: state.deposit.record,
  };
};

export default connect(mapStateToProps)(FormFieldsContainerComponent);
