import { DepositFormApp, parseFormAppConfig } from "@js/oarepo_ui/forms";
import React from "react";
import ReactDOM from "react-dom";
import { EDTFSingleDatePicker } from "@js/oarepo_ui/forms";
import { parametrize } from "react-overridable";
import { SubmitReviewModal } from "@js/invenio_rdm_records";
import { Icon } from "semantic-ui-react";
import PropTypes from "prop-types";
import { Trans } from "react-i18next";
import { i18next } from "@translations/i18next";
import {
  CCMMDepositRecordSerializer,
  CCMMSections,
} from "@js/ccmm_invenio/forms";

const { rootEl, config, ...rest } = parseFormAppConfig();
const recordSerializer = new CCMMDepositRecordSerializer(
  config.default_locale,
  config.custom_fields.vocabularies,
);

const parametrizeEDTFSingleDatePicker = parametrize(EDTFSingleDatePicker, {
  customInputProps: { width: 16 },
});

// Unwrap the Overridable to avoid the override-lookup loop when we render it below.
const RawSubmitReviewModal = SubmitReviewModal.originalComponent;

const CurationPolicySubmitReviewModal = (props) => {
  const { community } = props;
  const curationPolicyUrl = `${community.links.self_html}/curation-policy`;

  return (
    <RawSubmitReviewModal
      {...props}
      afterContent={() => (
        <p className="mt-10">
          <Icon name="exclamation circle" />
          <Trans i18n={i18next}>
            By submitting, you agree to the community's{" "}
            <a
              href={curationPolicyUrl}
              target="_blank"
              rel="noopener noreferrer"
            >
              curation policy
            </a>
            .
          </Trans>
        </p>
      )}
    />
  );
};

CurationPolicySubmitReviewModal.propTypes = {
  community: PropTypes.shape({
    links: PropTypes.shape({
      self_html: PropTypes.string,
    }),
  }).isRequired,
};

export const componentOverrides = {
  "InvenioRdmRecords.DepositForm.DatesField.DateField":
    parametrizeEDTFSingleDatePicker,
  "InvenioRdmRecords.SubmitReviewModal.container":
    CurationPolicySubmitReviewModal,
};

ReactDOM.render(
  <DepositFormApp
    config={config}
    {...rest}
    sections={CCMMSections}
    recordSerializer={recordSerializer}
    componentOverrides={componentOverrides}
    useWizardForm
  />,
  rootEl,
);
