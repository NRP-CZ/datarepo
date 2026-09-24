import React from "react";
import PropTypes from "prop-types";
import { TextField, TextAreaField } from "react-invenio-forms";
import { Button, Icon } from "semantic-ui-react";
import { i18next } from "@translations/ccmm_invenio";

export function GeolocationInputFieldDetail({ basePath, handleRemove }) {
  return (
    <div className="geolocation-detail">
      <TextField
        fieldPath={`${basePath}.place`}
        label={i18next.t("Name")}
        placeholder={i18next.t("e.g. Prague, Czechia")}
      />

      <TextAreaField
        fieldPath={`${basePath}.description`}
        label={i18next.t("Description")}
        placeholder={i18next.t("Additional details about this location...")}
      />

      <Button
        type="button"
        color="red"
        icon
        labelPosition="left"
        onClick={handleRemove}
        style={{ marginTop: "15px" }}
      >
        <Icon name="trash alternate" />
        {i18next.t("Remove Location")}
      </Button>
    </div>
  );
}

GeolocationInputFieldDetail.propTypes = {
  basePath: PropTypes.string.isRequired,
  handleRemove: PropTypes.func.isRequired,
};
