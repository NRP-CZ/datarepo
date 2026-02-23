import React, { Component } from "react";
import PropTypes from "prop-types";
import { getIn, FieldArray } from "formik";
import { Form, Label, List, Icon } from "semantic-ui-react";
import { FieldLabel } from "react-invenio-forms";
import { HTML5Backend } from "react-dnd-html5-backend";
import { DndProvider } from "react-dnd";
import { RelatedResourceModal } from "./RelatedResourceModal";
import { RelatedResourceFieldItem } from "./RelatedResourceFieldItem";
import { i18next } from "@translations/i18next";
import { useFormConfig } from "@js/oarepo_ui/forms";
import { save } from "@js/oarepo_ui/forms/state/deposit/actions";
import { connect } from "react-redux";
import { useDepositFormAction } from "@js/oarepo_ui/forms/hooks";

class RelatedResourceFieldForm extends Component {
  handleOnResourceChange = (selectedResource) => {
    const { push: formikArrayPush } = this.props;
    formikArrayPush(selectedResource);
  };

  render() {
    const {
      form: { values, errors, initialErrors, initialValues },
      remove: formikArrayRemove,
      replace: formikArrayReplace,
      move: formikArrayMove,
      fieldPath,
      label = i18next.t("Related resources"),
      icon = "linkify",
      required = false,
      vocabularies,
      relatedResourceUI,
      handleSave,
    } = this.props;

    const resourcesList = getIn(values, fieldPath, []);
    const formikInitialValues = getIn(initialValues, fieldPath, []);

    const error = getIn(errors, fieldPath, null);
    const initialError = getIn(initialErrors, fieldPath, null);
    const resourcesError =
      error || (resourcesList === formikInitialValues && initialError);

    const modalHeader = {
      addLabel: i18next.t("Add related resource"),
      editLabel: i18next.t("Edit related resource"),
    };

    return (
      <DndProvider backend={HTML5Backend}>
        <Form.Field
          required={required}
          className={resourcesError ? "error" : ""}
        >
          <FieldLabel htmlFor={fieldPath} label={label} icon={icon} />
          <List>
            {resourcesList.map((value, index) => {
              const key = `${fieldPath}.${index}`;
              const displayName =
                value?.title || i18next.t("Untitled resource");

              return (
                <RelatedResourceFieldItem
                  key={key}
                  relatedResourceUI={relatedResourceUI}
                  handleSave={handleSave}
                  {...{
                    displayName,
                    index,
                    compKey: key,
                    initialResource: value,
                    removeResource: formikArrayRemove,
                    replaceResource: formikArrayReplace,
                    moveResource: formikArrayMove,
                    addLabel: modalHeader.addLabel,
                    editLabel: modalHeader.editLabel,
                    vocabularies,
                  }}
                />
              );
            })}
          </List>
          <RelatedResourceModal
            onResourceChange={this.handleOnResourceChange}
            handleSave={handleSave}
            action="add"
            addLabel={modalHeader.addLabel}
            editLabel={modalHeader.editLabel}
            vocabularies={vocabularies}
            relatedResourceUI={relatedResourceUI}
            trigger={
              <Form.Button
                className="array-field-add-button inline-block"
                type="button"
                icon
                labelPosition="left"
              >
                <Icon name="add" />
                {i18next.t("Add related resource")}
              </Form.Button>
            }
          />
          {resourcesError && typeof resourcesError == "string" && (
            <Label pointing="left" prompt>
              {resourcesError}
            </Label>
          )}
        </Form.Field>
      </DndProvider>
    );
  }
}

RelatedResourceFieldForm.propTypes = {
  form: PropTypes.object.isRequired,
  remove: PropTypes.func.isRequired,
  replace: PropTypes.func.isRequired,
  move: PropTypes.func.isRequired,
  push: PropTypes.func.isRequired,
  fieldPath: PropTypes.string.isRequired,
  required: PropTypes.bool,
  label: PropTypes.string,
  icon: PropTypes.string,
  vocabularies: PropTypes.object,
  relatedResourceUI: PropTypes.object,
  handleSave: PropTypes.func.isRequired,
};

export class RelatedResourceFieldInnerComponent extends Component {
  render() {
    const {
      fieldPath,
      required = false,
      vocabularies,
      relatedResourceUI,
      handleSave,
    } = this.props;

    return (
      <FieldArray
        name={fieldPath}
        render={(formikProps) => (
          <RelatedResourceFieldForm
            required={required}
            vocabularies={vocabularies}
            relatedResourceUI={relatedResourceUI}
            handleSave={handleSave}
            {...formikProps}
            {...this.props}
          />
        )}
      />
    );
  }
}

RelatedResourceFieldInnerComponent.propTypes = {
  fieldPath: PropTypes.string.isRequired,
  required: PropTypes.bool,
  label: PropTypes.string,
  icon: PropTypes.string,
  vocabularies: PropTypes.object,
  relatedResourceUI: PropTypes.object,
  handleSave: PropTypes.func.isRequired,
};

const RelatedResourceFieldComponent = ({
  icon = "linkify",
  label,
  fieldPath,
  relatedResourceUI,
  saveAction,
  ...props
}) => {
  const formConfig = useFormConfig();
  const vocabularies = formConfig?.config?.vocabularies || {};
  const { handleAction: handleSave } = useDepositFormAction({
    action: saveAction,
  });
  return (
    <RelatedResourceFieldInnerComponent
      fieldPath={fieldPath}
      handleSave={handleSave}
      icon={icon}
      label={label || i18next.t("Related resources")}
      vocabularies={vocabularies}
      relatedResourceUI={relatedResourceUI}
      {...props}
    />
  );
};

RelatedResourceFieldComponent.propTypes = {
  fieldPath: PropTypes.string.isRequired,
  required: PropTypes.bool,
  label: PropTypes.string,
  icon: PropTypes.string,
  vocabularies: PropTypes.object,
  relatedResourceUI: PropTypes.object,
  saveAction: PropTypes.func.isRequired,
};

const mapDispatchToProps = (dispatch) => ({
  saveAction: (values, params) => dispatch(save(values, params)),
});

export const RelatedResourceField = connect(
  null,
  mapDispatchToProps,
)(RelatedResourceFieldComponent);
