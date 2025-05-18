#
# Roles within the workflow:
#
# Community roles:
#
# CommunityRole("submitter") == people who can create new records
# CommunityRole("curator") == people who can publish records and remove them
# CommunityRole("owner") == supercurator, NTK staff
# CommunityMembers() == member of the community
#
# Synthetic roles:
#
# RecordOwners() == actual owner of the record (person who created it)
#
#
# Record states:
#
# draft == record is being created
# submitted == record is submitted for approval/publishing but not yet accepted
# published == record is published
# deleting == record is in the process of being deleted (request filed but not yet accepted)
#

from datetime import timedelta

from invenio_i18n import lazy_gettext as _
from invenio_rdm_records.services.generators import IfRecordDeleted, IfRestricted
from invenio_records_permissions.generators import (
    AnyUser,
    Disable,
    SystemProcess,
)
from invenio_users_resources.services.permissions import UserManager
from oarepo_communities.services.permissions.generators import (
    CommunityRole,
    PrimaryCommunityMembers,
    PrimaryCommunityRole,
    TargetCommunityRole,
)
from oarepo_communities.services.permissions.policy import (
    CommunityDefaultWorkflowPermissions,
)
from oarepo_requests.services.permissions.generators import IfRequestedBy
from oarepo_runtime.services.permissions.generators import IfDraftType, RecordOwners
from oarepo_workflows import (
    AutoApprove,
    IfInState,
    WorkflowRequest,
    WorkflowRequestEscalation,
    WorkflowRequestPolicy,
    WorkflowTransitions,
)


class DefaultWorkflowPermissions(CommunityDefaultWorkflowPermissions):
    can_create = [
        PrimaryCommunityRole("submitter"),
        PrimaryCommunityRole("owner"),
        PrimaryCommunityRole("curator"),
    ]

    can_read_generic = [
        RecordOwners(),
        # curator can see the record in any state
        CommunityRole("curator"),
        # owner of community can see the record in any state
        CommunityRole("owner"),
        # if the record is published and restricted, only members of the community can see it,
        # otherwise, any user can see it
        # every member of the community can see the metadata of the drafts, but not the files
        IfInState(
            "draft",
            then_=[PrimaryCommunityMembers()],
        ),
    ]

    can_read = can_read_generic + [
        IfInState(
            "published",
            then_=[
                IfRestricted(
                    "record",
                    then_=[PrimaryCommunityMembers()],
                    else_=[AnyUser()],
                )
            ],
        ),
    ]
    can_read_deleted = [
        IfRecordDeleted(
            then_=[
                UserManager,  # this is strange, but taken from RDM
                SystemProcess(),
            ],
            else_=can_read,
        )
    ]

    can_read_files = can_read_generic + [
        IfInState(
            "published",
            then_=[
                IfRestricted(
                    "files",
                    then_=[PrimaryCommunityMembers()],
                    else_=[AnyUser()],
                )
            ],
        ),
    ]

    can_list_files = can_read_files

    can_get_content_files = can_read_files

    can_update = [
        IfInState(
            "draft",
            then_=[
                RecordOwners(),
                PrimaryCommunityRole("curator"),
                PrimaryCommunityRole("owner"),
            ],
        ),
        # if not draft, can not be directly updated by any means, must use request
        IfInState(
            "submitted",
            then_=[
                PrimaryCommunityRole("curator"),
                PrimaryCommunityRole("owner"),
            ],
        ),
    ]

    can_delete = [
        # draft can be deleted, published record must be deleted via request
        IfInState(
            "draft",
            then_=[
                RecordOwners(),
                PrimaryCommunityRole("curator"),
                PrimaryCommunityRole("owner"),
            ],
        ),
    ] + CommunityDefaultWorkflowPermissions.can_delete

    can_manage_files = [
        Disable(),
    ]


# if the record is in draft state, the owner or curator can request publishing
publish_requesters = IfInState(
    "draft", then_=[RecordOwners(), PrimaryCommunityRole("curator")]
)

# if the requester is the curator of the community, auto approve the request
publish_recipients = IfRequestedBy(
    requesters=[
        PrimaryCommunityRole("curator"),
        PrimaryCommunityRole("owner"),
    ],
    then_=[AutoApprove()],
    else_=[PrimaryCommunityRole("curator"), PrimaryCommunityRole("owner")],
)

publish_transitions = WorkflowTransitions(
    submitted="submitted",
    accepted="published",
    declined="draft",
    cancelled="draft",
)

# if the request is not resolved in 21 days, escalate it to the administrator
publish_escalations = [
    WorkflowRequestEscalation(
        after=timedelta(days=21),
        recipients=[
            PrimaryCommunityRole("owner"),
        ],
    )
]


class DefaultWorkflowRequests(WorkflowRequestPolicy):
    publish_draft = WorkflowRequest(
        requesters=[
            IfDraftType(
                "metadata",
                then_=publish_requesters,
            )
        ],
        recipients=[publish_recipients],
        transitions=publish_transitions,
        escalations=publish_escalations,
    )

    publish_new_version = WorkflowRequest(
        requesters=[
            IfDraftType(
                ["new_version", "initial"],
                then_=publish_requesters,
            )
        ],
        recipients=[publish_recipients],
        transitions=publish_transitions,
        escalations=publish_escalations,
    )

    edit_published_record = WorkflowRequest(
        requesters=[
            IfInState(
                "published",
                then_=[
                    RecordOwners(),
                    PrimaryCommunityRole("curator"),
                    PrimaryCommunityRole("owner"),
                ],
            )
        ],
        # the request is auto-approve, we do not limit the owner of the record to create a new
        # draft version. It will need to be accepted by the curator though.
        recipients=[AutoApprove()],
    )

    new_version = WorkflowRequest(
        requesters=[
            IfInState(
                "published",
                then_=[
                    RecordOwners(),
                    PrimaryCommunityRole("curator"),
                    PrimaryCommunityRole("owner"),
                ],
            )
        ],
        # the request is auto-approve, we do not limit the owner of the record to create a new
        # draft version. It will need to be accepted by the curator though.
        recipients=[AutoApprove()],
    )

    delete_published_record = WorkflowRequest(
        # if the record is draft, it is covered by the delete permission
        # if published, only the owner or curator can request deleting
        requesters=[
            IfInState(
                "published",
                then_=[
                    RecordOwners(),
                    PrimaryCommunityRole("curator"),
                    PrimaryCommunityRole("owner"),
                ],
            )
        ],
        # if the requester is the curator of the community or administrator, auto approve the request,
        # otherwise, the request is sent to the curator
        recipients=[
            IfRequestedBy(
                requesters=[
                    PrimaryCommunityRole("curator"),
                    PrimaryCommunityRole("owner"),
                ],
                then_=[AutoApprove()],
                else_=[PrimaryCommunityRole("curator")],
            )
        ],
        # the record comes to the state of retracting when the request is submitted. If the request
        # is accepted, the record is deleted, if declined, it is published again.
        transitions=WorkflowTransitions(
            submitted="retracting",
            declined="published",
            accepted="deleted",
            cancelled="published",
        ),
        # if the request is not resolved in 21 days, escalate it to the administrator
        escalations=[
            WorkflowRequestEscalation(
                after=timedelta(days=21),
                recipients=[
                    PrimaryCommunityRole("owner"),
                ],
            )
        ],
    )

    assign_doi = WorkflowRequest(
        requesters=[
            RecordOwners(),
            PrimaryCommunityRole("curator"),
            PrimaryCommunityRole("owner"),
        ],
        recipients=[
            IfRequestedBy(
                requesters=[
                    PrimaryCommunityRole("curator"),
                    PrimaryCommunityRole("owner"),
                ],
                then_=[AutoApprove()],
                else_=[PrimaryCommunityRole("curator")],
            )
        ],
        escalations=[
            WorkflowRequestEscalation(
                after=timedelta(days=21), recipients=[PrimaryCommunityRole("owner")]
            )
        ],
    )
    initiate_community_migration = WorkflowRequest(
        requesters=[
            IfInState(
                "published",
                then_=[
                    RecordOwners(),
                    PrimaryCommunityRole("curator"),
                    PrimaryCommunityRole("owner"),
                ],
            )
        ],
        recipients=[
            IfRequestedBy(
                requesters=[
                    PrimaryCommunityRole("curator"),
                    PrimaryCommunityRole("owner"),
                ],
                then_=[AutoApprove()],
                else_=[PrimaryCommunityRole("curator"), PrimaryCommunityRole("owner")],
            )
        ],
    )
    confirm_community_migration = WorkflowRequest(
        requesters=[],
        recipients=[
            TargetCommunityRole("curator"),
            TargetCommunityRole("owner"),
        ],
    )
    secondary_community_submission = WorkflowRequest(
        requesters=[
            IfInState(
                "published",
                then_=[PrimaryCommunityMembers()],
            )
        ],
        recipients=[
            IfRequestedBy(
                requesters=[
                    TargetCommunityRole("curator"),
                    TargetCommunityRole("owner"),
                ],
                then_=[AutoApprove()],
                else_=[TargetCommunityRole("curator"), TargetCommunityRole("owner")],
            )
        ],
    )


if False:
    # just for translation extraction
    translated_strings = [
        _("state:draft"),
        _("state:published"),
        _("state:submitted"),
        _("state:retracting"),
        _("state:deleted"),
    ]
