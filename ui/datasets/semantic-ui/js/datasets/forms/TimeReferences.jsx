import React from "react";
import PropTypes from "prop-types";
import { ArrayField, GroupField } from "react-invenio-forms";
import { StringArrayField, TextField } from "@js/oarepo_ui/forms";
import {
  ArrayFieldItem,
  EDTFDaterangePicker,
  EDTFSingleDatePicker,
  useSanitizeInput,
  useFieldData,
  I18nTextInputField,
} from "@js/oarepo_ui";
import { useFormikContext, getIn } from "formik";
import { Label } from "semantic-ui-react";

export const TimeReferences = ({ fieldPath }) => {
  const { values, setFieldValue, setFieldTouched, errors } = useFormikContext();

  const { sanitizeInput } = useSanitizeInput();
  const { getFieldData } = useFieldData();
  return (
    <ArrayField
      addButtonLabel={"Add event"}
      fieldPath={fieldPath}
      {...getFieldData({ fieldPath, fieldRepresentation: "text" })}
      addButtonClassName="array-field-add-button"
    >
      {({ arrayHelpers, indexPath }) => {
        const fieldPathPrefix = `${fieldPath}.${indexPath}`;
        const eventNameOriginalFieldPath = `${fieldPathPrefix}.eventNameOriginal`;

        return (
          <ArrayFieldItem
            indexPath={indexPath}
            arrayHelpers={arrayHelpers}
            className={"invenio-group-field events"}
            fieldPathPrefix={fieldPathPrefix}
            style={{ display: "block", marginBottom: "1em" }}
          >
            <EDTFDaterangePicker
              fieldPath={`${fieldPathPrefix}.time_interval`}
            />
            <EDTFSingleDatePicker
              fieldPath={`${fieldPathPrefix}.time_instant.date_time`}
            />
            <I18nTextInputField
              fieldPath={`${fieldPathPrefix}.time_instant.date_information`}
              lngFieldWidth={6}
            />
          </ArrayFieldItem>
        );
      }}
    </ArrayField>
  );
};

TimeReferences.propTypes = {
  fieldPath: PropTypes.string.isRequired,
};
