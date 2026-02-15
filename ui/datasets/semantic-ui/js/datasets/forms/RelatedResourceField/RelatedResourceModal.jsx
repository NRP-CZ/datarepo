import { i18next } from "@translations/i18next";
import { Formik } from "formik";
import * as Yup from "yup";
import _isEmpty from "lodash/isEmpty";
import _get from "lodash/get";
import PropTypes from "prop-types";
import React, { Component } from "react";
import { SelectField } from "react-invenio-forms";
import { Button, Form, Modal } from "semantic-ui-react";
import {
  EDTFSingleDatePicker,
  CreatibutorsField,
  FundingField,
  FormikStateLogger,
} from "@js/oarepo_ui/forms";
import {
  TitlesField,
  IdentifiersField,
  LanguagesField,
  ResourceTypeField,
  PublisherField,
  LicenseField,
  SubjectsField,
  DatesField,
} from "@js/invenio_rdm_records";
import { AdditionalDescriptionsField } from "@js/invenio_rdm_records/src/deposit/fields/DescriptionsField/components";
import { AccordionField } from "react-invenio-forms";

const ModalActions = {
  ADD: "add",
  EDIT: "edit",
};

// Form uses metadata.* paths internally
const emptyRelatedResource = {
  metadata: {
    relation_type: null,
    title: "",
    resource_type: null,
    publication_date: "",
    publisher: "",
    additional_titles: [],
    additional_descriptions: [],
    identifiers: [],
    creators: [],
    contributors: [],
    dates: [],
    subjects: [],
    funding: [],
    rights: [],
    languages: [],
  },
};

// Transform flat structure to metadata.* structure for form
// metadata namespacing necessary, because some invenio components simply have hardcoded metadata.smth field paths inside
const toFormValues = (resource) => {
  if (_isEmpty(resource)) return emptyRelatedResource;
  return {
    metadata: resource,
  };
};

// Transform metadata.* structure back to flat structure for parent form
const fromFormValues = (values) => {
  const { metadata } = values;
  return metadata;
};

const RelatedResourceValidationSchema = Yup.object().shape({
  metadata: Yup.object().shape({
    relation_type: Yup.string().required(
      i18next.t("Relation type is required"),
    ),
    title: Yup.string().required(i18next.t("Title is required")),
    resource_type: Yup.string().required(
      i18next.t("Resource type is required"),
    ),
    publication_date: Yup.string().required(
      i18next.t("Publication date is required"),
    ),
    creators: Yup.array()
      .min(1, i18next.t("At least one creator is required"))
      .required(i18next.t("At least one creator is required")),
  }),
});

export class RelatedResourceModal extends Component {
  constructor(props) {
    super(props);

    this.state = {
      open: false,
      saveAndContinueLabel: i18next.t("Save and add another"),
      action: null,
    };
  }

  openModal = () => {
    this.setState({ open: true, action: null });
  };

  closeModal = () => {
    this.setState({
      open: false,
      action: null,
    });
  };

  changeContent = () => {
    this.setState({ saveAndContinueLabel: i18next.t("Added") });
    setTimeout(() => {
      this.setState({
        saveAndContinueLabel: i18next.t("Save and add another"),
      });
    }, 2000);
  };

  displayActionLabel = () => {
    const { action, addLabel, editLabel } = this.props;
    return action === ModalActions.ADD ? addLabel : editLabel;
  };

  onSubmit = async (values, formikBag) => {
    const { onResourceChange, handleSave } = this.props;
    const { action } = this.state;
    onResourceChange(fromFormValues(values));
    await new Promise((resolve) => setTimeout(resolve, 100));

    formikBag.setSubmitting(false);
    formikBag.resetForm();
    switch (action) {
      case "saveAndContinue":
        this.closeModal();
        this.openModal();
        this.changeContent();
        break;
      case "saveAndClose":
        this.closeModal();
        await handleSave();
        break;
      default:
        await handleSave();
        break;
    }
  };

  render() {
    const {
      initialResource = {},
      vocabularies = {},
      trigger,
      action,
      relatedResourceUI,
      index,
    } = this.props;
    const { open, saveAndContinueLabel } = this.state;

    const ActionLabel = this.displayActionLabel();
    const initialValues = toFormValues(initialResource);
    const relationTypeOptions = (
      vocabularies?.related_identifiers?.relations || []
    ).map((item) => ({
      text: item.text || item.title_l10n || item.id,
      value: item.value || item.id,
      key: item.value || item.id,
    }));

    return (
      <Formik
        initialValues={initialValues}
        validationSchema={RelatedResourceValidationSchema}
        onSubmit={this.onSubmit}
        enableReinitialize
        validateOnChange={false}
        validateOnBlur={false}
      >
        {({ values, resetForm, handleSubmit }) => {
          return (
            <Modal
              centered={false}
              onOpen={() => this.openModal()}
              open={open}
              trigger={trigger}
              onClose={() => {
                this.closeModal();
                resetForm();
              }}
              closeIcon
              closeOnDimmerClick={false}
              size="large"
            >
              <Modal.Header as="h2" className="pt-10 pb-10">
                {ActionLabel}
              </Modal.Header>
              <Modal.Content scrolling>
                <Form>
                  <AccordionField
                    includesPaths={[
                      "metadata.relation_type",
                      "metadata.title",
                      "metadata.resource_type",
                      "metadata.publication_date",
                    ]}
                    active
                    label={i18next.t("Basic information")}
                  >
                    <SelectField
                      fieldPath="metadata.relation_type"
                      label={i18next.t("Relation type")}
                      options={relationTypeOptions}
                      placeholder={i18next.t("Select relation type...")}
                      required
                      clearable
                      optimized
                    />
                    <TitlesField
                      options={vocabularies?.titles}
                      fieldPath="metadata.title"
                      recordUI={relatedResourceUI?.[index]}
                      required
                    />
                    <ResourceTypeField
                      options={vocabularies?.resource_type}
                      fieldPath="metadata.resource_type"
                    />
                    <EDTFSingleDatePicker
                      fieldPath="metadata.publication_date"
                      required
                    />
                    <PublisherField fieldPath="metadata.publisher" />
                  </AccordionField>

                  <AccordionField
                    includesPaths={[
                      "metadata.additional_descriptions",
                      "metadata.languages",
                    ]}
                    label={i18next.t("Additional details")}
                  >
                    <AdditionalDescriptionsField
                      recordUI={relatedResourceUI?.[index]}
                      options={vocabularies?.descriptions}
                      optimized
                      fieldPath="metadata.additional_descriptions"
                    />
                    <LanguagesField
                      fieldPath="metadata.languages"
                      initialOptions={_get(
                        relatedResourceUI?.[index],
                        "languages",
                        [],
                      ).filter((lang) => lang !== null)}
                      serializeSuggestions={(suggestions) =>
                        suggestions.map((item) => ({
                          text: item.title_l10n,
                          value: item.id,
                          key: item.id,
                        }))
                      }
                    />
                  </AccordionField>

                  <AccordionField
                    includesPaths={["metadata.identifiers"]}
                    label={i18next.t("Identifiers")}
                  >
                    <IdentifiersField
                      fieldPath="metadata.identifiers"
                      label={i18next.t("Identifiers")}
                      labelIcon="barcode"
                      schemeOptions={vocabularies?.identifiers?.scheme}
                      showEmptyValue
                    />
                  </AccordionField>

                  <AccordionField
                    includesPaths={[
                      "metadata.creators",
                      "metadata.contributors",
                    ]}
                    label={i18next.t("Creators and Contributors")}
                  >
                    <CreatibutorsField
                      fieldPath="metadata.creators"
                      schema="creators"
                      autocompleteNames="search"
                      required
                    />
                    <CreatibutorsField
                      fieldPath="metadata.contributors"
                      schema="contributors"
                      autocompleteNames="search"
                      showRoleField
                    />
                  </AccordionField>

                  <AccordionField
                    includesPaths={["metadata.dates", "metadata.subjects"]}
                    label={i18next.t("Dates and Subjects")}
                  >
                    <DatesField
                      fieldPath="metadata.dates"
                      options={vocabularies?.dates}
                      showEmptyValue
                    />
                    <SubjectsField
                      fieldPath="metadata.subjects"
                      initialOptions={_get(initialResource, "subjects", null)}
                      limitToOptions={vocabularies?.subjects?.limit_to}
                      searchOnFocus
                    />
                  </AccordionField>

                  <AccordionField
                    includesPaths={["metadata.funding", "metadata.rights"]}
                    label={i18next.t("Funding and Rights")}
                  >
                    <FundingField fieldPath="metadata.funding" />
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
                  </AccordionField>
                </Form>
              </Modal.Content>
              <Modal.Actions>
                <Button
                  name="cancel"
                  onClick={() => {
                    resetForm();
                    this.closeModal();
                  }}
                  icon="remove"
                  content={i18next.t("Cancel")}
                  floated="left"
                />
                {action === ModalActions.ADD && (
                  <Button
                    name="submit"
                    onClick={() => {
                      this.setState(
                        {
                          action: "saveAndContinue",
                        },
                        () => {
                          handleSubmit();
                        },
                      );
                    }}
                    primary
                    icon="checkmark"
                    content={saveAndContinueLabel}
                  />
                )}
                <Button
                  name="submit"
                  onClick={() => {
                    this.setState(
                      {
                        action: "saveAndClose",
                      },
                      () => handleSubmit(),
                    );
                  }}
                  primary
                  icon="checkmark"
                  content={i18next.t("Save")}
                />
              </Modal.Actions>
            </Modal>
          );
        }}
      </Formik>
    );
  }
}

RelatedResourceModal.propTypes = {
  action: PropTypes.oneOf(["add", "edit"]).isRequired,
  addLabel: PropTypes.string.isRequired,
  editLabel: PropTypes.string.isRequired,
  initialResource: PropTypes.object,
  trigger: PropTypes.object.isRequired,
  onResourceChange: PropTypes.func.isRequired,
  vocabularies: PropTypes.object,
  relatedResourceUI: PropTypes.object,
  index: PropTypes.number,
  handleSave: PropTypes.func,
};
