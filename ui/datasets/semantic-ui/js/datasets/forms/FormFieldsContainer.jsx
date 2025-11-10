import * as React from "react";
import {
  useFormConfig,
  FormikStateLogger,
  TextField,
  EDTFSingleDatePicker,
  CreatibutorsField,
  objectIdentifiersSchema,
  FundingField,
} from "@js/oarepo_ui/forms";
import { AccordionField } from "react-invenio-forms";
import { i18next } from "@translations/i18next";
import {
  UppyUploader,
  TitlesField,
  IdentifiersField,
  SubjectsField,
  LanguagesField,
  ResourceTypeField,
  PublisherField,
  VersionField,
} from "@js/invenio_rdm_records";
import { connect } from "react-redux";
import PropTypes from "prop-types";
import { AdditionalDescriptionsField } from "@js/invenio_rdm_records/src/deposit/fields/DescriptionsField/components";
import _get from "lodash/get";

const limitToOptions = [
  { text: "All", value: "all" },
  { text: "FOS", value: "FOS" },
  { text: "Other", value: "other" },
];

const FormFieldsContainerComponent = ({ record }) => {
  const formConfig = useFormConfig();
  const {
    config: { filesLocked, vocabularies },
  } = formConfig;
  return (
    <React.Fragment key="form-fields-container">
      <AccordionField
        includesPaths={[
          "metadata.title",
          "metadata.publication_date",
          "metadata.additional_descriptions",
          "metadata.version",
          "metadata.additional_descriptions",
        ]}
        active
        label={i18next.t("Basic information")}
      >
        <ResourceTypeField
          options={vocabularies?.resource_type}
          fieldPath="metadata.resource_type"
          required
        />
        <TitlesField
          options={vocabularies?.titles}
          fieldPath="metadata.title"
          recordUI={record.ui}
          required
        />
        <EDTFSingleDatePicker fieldPath="metadata.publication_date" />
        <AdditionalDescriptionsField
          recordUI={_get(record, "ui", null)}
          options={vocabularies?.descriptions}
          optimized
          fieldPath="metadata.additional_descriptions"
          values={record}
        />

        <LanguagesField
          fieldPath="metadata.languages"
          initialOptions={_get(record, "ui.languages", []).filter(
            (lang) => lang !== null
          )}
          serializeSuggestions={(suggestions) =>
            suggestions.map((item) => ({
              text: item.title_l10n,
              value: item.id,
              key: item.id,
            }))
          }
        />
        <PublisherField fieldPath="metadata.publisher" />
        <VersionField fieldPath="metadata.version" />
      </AccordionField>

      <AccordionField
        includesPaths={["metadata.identifiers"]}
        active
        label={i18next.t("Identifiers information")}
      >
        <IdentifiersField
          fieldPath="metadata.identifiers"
          label={i18next.t("Alternate identifiers")}
          labelIcon="barcode"
          schemeOptions={vocabularies?.identifiers?.scheme}
          showEmptyValue
        />
        <SubjectsField
          fieldPath="metadata.subjects"
          initialOptions={_get(record, "ui.subjects", null)}
          limitToOptions={vocabularies?.subjects?.limit_to}
          searchOnFocus
        />
        <FundingField fieldPath="metadata.funding" />
      </AccordionField>

      <AccordionField
        includesPaths={["metadata.creators", "metadata.contributors"]}
        active
        label={i18next.t("Creators and Contributors information")}
      >
        <CreatibutorsField
          fieldPath="metadata.creators"
          schema="creators"
          autocompleteNames="search"
        />
        <CreatibutorsField
          fieldPath="metadata.contributors"
          schema="contributors"
          autocompleteNames="search"
          showRoleField
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
