import { DepositFormApp, parseFormAppConfig } from "@js/oarepo_ui/forms";
import React from "react";
import ReactDOM from "react-dom";
import { OARepoDepositSerializer } from "@js/oarepo_ui/api";
import { CommunityHeader } from "@js/invenio_rdm_records";
import { UppyUploader } from "@js/invenio_rdm_records";
import { TextField } from "@js/oarepo_ui/forms";
import { i18next } from "@translations/i18next";

const sections = [
  {
    key: "community",
    label: i18next.t("Community"),
    render: (record) => (
      <CommunityHeader
        imagePlaceholderLink="/static/images/square-placeholder.png"
        record={record}
      />
    ),
    includedPaths: ["parent.communities.default"],
  },
  {
    key: "basic",
    label: i18next.t("Basic information"),
    render: () => <TextField fieldPath="metadata.title" />,
    includedPaths: ["metadata.title"],
  },
  {
    key: "files",
    label: i18next.t("Files upload"),
    render: (record, formConfig) => (
      <UppyUploader
        isDraftRecord={!record.is_published}
        config={formConfig}
        quota={formConfig.quota}
        decimalSizeDisplay={formConfig.decimal_size_display}
        allowEmptyFiles={formConfig.allow_empty_files}
        fileUploadConcurrency={formConfig.file_upload_concurrency}
        showMetadataOnlyToggle
        filesLocked={false}
      />
    ),
    includedPaths: ["files.enabled"],
  },
];

const { rootEl, config, ...rest } = parseFormAppConfig();

ReactDOM.render(
  <DepositFormApp sections={sections} config={config} {...rest} />,
  rootEl,
);
