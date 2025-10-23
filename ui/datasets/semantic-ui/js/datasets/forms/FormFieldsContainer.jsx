import * as React from "react";
import {
  useFormConfig,
  FormikStateLogger,
  TextField,
  EDTFSingleDatePicker,
  CreatibutorsField,
  CreatibutorField,
  IdentifiersField,
  objectIdentifiersSchema,
  FundingField,
} from "@js/oarepo_ui/forms";
import { AccordionField, SelectField } from "react-invenio-forms";
import { i18next } from "@translations/i18next";
import {
  UppyUploader,
  FilesUploader,
  TitlesField,
  DescriptionsField,
  IdentifiersField as RDMIdentifiersField,
  SubjectsField,
  LanguagesField,
  ResourceTypeField,
} from "@js/invenio_rdm_records";
import { connect } from "react-redux";
import PropTypes from "prop-types";
import { AdditionalDescriptionsField } from "@js/invenio_rdm_records/src/deposit/fields/DescriptionsField/components";
import { RemoteSelectField } from "./RemoteSelectField";
import _get from "lodash/get";
import { useFormikContext } from "formik";
import { Dropdown, Button } from "semantic-ui-react";
import { TimeReferences } from "./TimeReferences";

const friendOptions = [
  {
    key: "Jenny Hess",
    text: "Jenny Hess",
    value: "Jenny Hess",
    image: { avatar: true, src: "/images/avatar/small/jenny.jpg" },
  },
  {
    key: "Elliot Fu",
    text: "Elliot Fu",
    value: "Elliot Fu",
    image: { avatar: true, src: "/images/avatar/small/elliot.jpg" },
  },
  {
    key: "Stevie Feliciano",
    text: "Stevie Feliciano",
    value: "Stevie Feliciano",
    image: { avatar: true, src: "/images/avatar/small/stevie.jpg" },
  },
  {
    key: "Christian",
    text: "Christian",
    value: "Christian",
    image: { avatar: true, src: "/images/avatar/small/christian.jpg" },
  },
  {
    key: "Matt",
    text: "Matt",
    value: "Matt",
    image: { avatar: true, src: "/images/avatar/small/matt.jpg" },
  },
  {
    key: "Justen Kitsune",
    text: "Justen Kitsune",
    value: "Justen Kitsune",
    image: { avatar: true, src: "/images/avatar/small/justen.jpg" },
  },
];

const resourceTypes = [
  {
    icon: "file alternate",
    id: "publication-annotationcollection",
    subtype_name: "Annotation collection",
    type_name: "Publication",
  },
  {
    icon: "file alternate",
    id: "publication-section",
    subtype_name: "Book chapter",
    type_name: "Publication",
  },
  {
    icon: "file alternate",
    id: "publication-conferenceproceeding",
    subtype_name: "Conference proceeding",
    type_name: "Publication",
  },
  {
    icon: "file alternate",
    id: "publication-journal",
    subtype_name: "Journal",
    type_name: "Publication",
  },
  {
    icon: "file alternate",
    id: "publication-article",
    subtype_name: "Journal article",
    type_name: "Publication",
  },
];
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
const limitToOptions = [
  { text: "All", value: "all" },
  { text: "FOS", value: "FOS" },
  { text: "Other", value: "other" },
];
const alternativeTitleOptions = {
  type: [
    { text: i18next.t("Alternative title"), value: "alternative-title" },
    { text: i18next.t("Translated title"), value: "translated-title" },
    { text: i18next.t("Subtitle"), value: "subtitle" },
    { text: i18next.t("Other"), value: "other" },
  ],
};

const descriptionTypeOptions = {
  type: [
    {
      text: i18next.t("Abstract"),
      value: "abstract",
      datacite: "Abstract",
    },
    {
      text: i18next.t("Methods"),
      value: "methods",
      datacite: "Methods",
    },
    {
      text: i18next.t("Series information"),
      value: "series-information",
      datacite: "SeriesInformation",
    },
    {
      text: i18next.t("Table of contents"),
      value: "table-of-contents",
      datacite: "TableOfContents",
    },
    {
      text: i18next.t("Technical info"),
      value: "technical-info",
      datacite: "TechnicalInfo",
    },
    {
      text: i18next.t("Other"),
      value: "other",
      datacite: "Other",
    },
  ],
};

const FormFieldsContainerComponent = ({ record }) => {
  const formConfig = useFormConfig();
  const { filesLocked } = formConfig;
  const { values } = useFormikContext();

  return (
    <React.Fragment>
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
        // severityChecks={severityChecksConfig}
      >
        <TextField fieldPath="metadata.version" />
        <TitlesField
          options={alternativeTitleOptions}
          fieldPath="metadata.title"
          recordUI={record.ui}
          required
        />
        <Dropdown
          placeholder="Select Friend"
          fluid
          selection
          options={friendOptions}
        />

        <EDTFSingleDatePicker fieldPath="metadata.publication_date" />
        <AdditionalDescriptionsField
          recordUI={_get(record, "ui", null)}
          options={descriptionTypeOptions}
          optimized
          fieldPath="metadata.additional_descriptions"
          values={values}
        />
        <SubjectsField
          fieldPath="metadata.subjects"
          initialOptions={_get(record, "ui.subjects", null)}
          limitToOptions={limitToOptions}
          searchOnFocus
        />
        <FundingField fieldPath="metadata.funding" />

        <LanguagesField
          fieldPath="metadata.languages"
          initialOptions={_get(record, "ui.languages", []).filter(
            (lang) => lang !== null
          )} // needed because dumped empty record from backend gives [null]
          serializeSuggestions={(suggestions) =>
            suggestions.map((item) => ({
              text: item.title_l10n,
              value: item.id,
              key: item.id,
            }))
          }
        />
        <Dropdown
          options={resourceTypes.map((rt) => ({
            text: `${rt.type_name} - ${rt.subtype_name}`,
            value: rt.id,
          }))}
          required
        />
      </AccordionField>
      <AccordionField
        includesPaths={["metadata.ccmm_publisher"]}
        active
        label={i18next.t("Publisher information")}
      >
        <TimeReferences fieldPath="metadata.time_references" />
        {/* <CreatibutorField
          fieldPath="metadata.ccmm_publisher"
          schema="creators"
          autocompleteNames="search"
        /> */}
      </AccordionField>
      <AccordionField
        includesPaths={["metadata.identifiers"]}
        active
        label={i18next.t("Identifiers information")}
      >
        <IdentifiersField
          options={objectIdentifiersSchema}
          fieldPath="metadata.identifiers"
        />
        <RDMIdentifiersField
          fieldPath="metadata.identifiers"
          label={i18next.t("Alternate identifiers")}
          labelIcon="barcode"
          schemeOptions={objectIdentifiersSchema}
          showEmptyValue
        />
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
      <div>
        <Button size="mini">Mini Button</Button>
        <Button size="tiny">Tiny Button</Button>
        <Button size="small">Small Button</Button>
        <Button size="medium">Medium Button</Button>
        <Button size="large">Large Button</Button>
        <Button size="big">Big Button</Button>
      </div>
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
