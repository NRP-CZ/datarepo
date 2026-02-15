import * as React from "react";
import {
  useFormConfig,
  FormikStateLogger,
  EDTFSingleDatePicker,
  CreatibutorsField,
  FundingField,
  AccessRightField,
} from "@js/oarepo_ui/forms";
import { AccordionField } from "react-invenio-forms";
import { i18next } from "@translations/i18next";
import { connect } from "react-redux";
import { AdditionalDescriptionsField } from "@js/invenio_rdm_records/src/deposit/fields/DescriptionsField/components";
import PropTypes from "prop-types";
import {
  UppyUploader,
  TitlesField,
  IdentifiersField,
  LanguagesField,
  ResourceTypeField,
  PublisherField,
  VersionField,
  LicenseField,
  SubjectsField,
  DatesField,
  CommunityHeader,
} from "@js/invenio_rdm_records";
import _get from "lodash/get";
import { RelatedResourceField } from "./RelatedResourceField";

const FormFieldsContainerComponent = ({ record }) => {
  const formConfig = useFormConfig();
  const {
    config: {
      filesLocked,
      vocabularies,
      permissions,
      allowRecordRestriction,
      recordRestrictionGracePeriod,
      hide_community_selection: hideCommunitySelection,
    },
  } = formConfig;

  return (
    <React.Fragment>
      {!hideCommunitySelection && (
        <CommunityHeader
          imagePlaceholderLink="/static/images/square-placeholder.png"
          record={record}
        />
      )}
      <AccordionField
        includesPaths={[
          "metadata.title",
          "metadata.resource_type",
          "metadata.publication_date",
          "metadata.additional_descriptions",
          "metadata.languages",
          "metadata.publisher",
          "metadata.version",
          "metadata.rights",
          "metadata.subjects",
          "metadata.dates",
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
            (lang) => lang !== null,
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
        <LicenseField
          fieldPath="metadata.rights"
          searchConfig={{
            searchApi: {
              axios: {
                headers: {
                  Accept: "application/vnd.inveniordm.v1+json",
                },
                url: "/api/vocabularies/licenses",
                withCredentials: false,
              },
            },
            initialQueryState: {
              filters: [["tags", "recommended"]],
              sortBy: "bestmatch",
              sortOrder: "asc",
              layout: "list",
              page: 1,
              size: 12,
            },
          }}
          serializeLicenses={(result) => ({
            title: result.title_l10n,
            description: result.description_l10n,
            id: result.id,
            link: result.props.url,
          })}
        />
        <SubjectsField
          fieldPath="metadata.subjects"
          initialOptions={_get(record, "ui.subjects", null)}
          limitToOptions={vocabularies.subjects.limit_to}
          searchOnFocus
        />
        <DatesField
          fieldPath="metadata.dates"
          options={vocabularies.dates}
          showEmptyValue
        />
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
        includesPaths={["metadata.related_resources"]}
        active
        label={i18next.t("Related resources")}
      >
        <RelatedResourceField
          fieldPath="metadata.related_resources"
          relatedResourceUI={record.ui?.related_resources}
        />
      </AccordionField>
      <AccordionField
        includesPaths={["access"]}
        active
        label={i18next.t("Access rights information")}
      >
        <AccessRightField
          label={i18next.t("Visibility")}
          record={record}
          labelIcon="shield"
          fieldPath="access"
          showMetadataAccess={permissions?.can_manage_record_access}
          recordRestrictionGracePeriod={recordRestrictionGracePeriod}
          allowRecordRestriction={allowRecordRestriction}
          id="visibility-section"
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
