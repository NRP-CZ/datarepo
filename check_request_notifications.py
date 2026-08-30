#
# This file needs to be run via invenio shell check_request_notifications.py
#

import contextlib
from datetime import UTC, datetime
from io import BytesIO
from typing import cast

from flask import current_app, g
from flask_security.utils import hash_password
from invenio_access.permissions import system_identity
from invenio_accounts.proxies import current_datastore
from invenio_communities.communities.services.service import CommunityService
from invenio_communities.members import MemberService
from invenio_communities.members.errors import InvalidMemberError
from invenio_communities.members.services.request import MembershipRequestRequestType
from invenio_db import db
from invenio_notifications.proxies import current_notifications_manager
from invenio_rdm_records.services.services import RDMRecordService
from invenio_records_resources.proxies import current_service_registry
from invenio_requests.customizations import CommentEventType
from invenio_requests.proxies import (
    current_events_service,
    current_request_type_registry,
    current_requests_service,
)
from invenio_users_resources.services.users.service import UsersService
from oarepo_requests.types import (
    PublishChangedMetadataRequestType,
    PublishNewVersionRequestType,
)
from oarepo_runtime.proxies import current_runtime

if not current_app.config.get("CELERY_ALWAYS_EAGER"):
    raise RuntimeError("Set export INVENIO_CELERY_ALWAYS_EAGER=1 to run this script")

TC_SLUG = "test-community"

CURATOR = "tc_curator@demo.org"
OWNER = "tc_owner@demo.org"
READER = "tc_reader@demo.org"
SUBMITTER = "tc_submitter@demo.org"
EXTRA_READER = "tc_extra_reader@demo.org"
EXTRA_SUBMITTER = "tc_extra_submitter@demo.org"

community_service = cast("CommunityService", current_service_registry.get("communities"))
members_service: MemberService = community_service.members
datasets_service = cast("RDMRecordService", current_service_registry.get("datasets"))


def create_user_if_missing(email, *, password="123456"):
    """Create an active, confirmed user with `email` if it does not exist yet.

    Mirrors `invenio users create -a -c --password <password>` from the
    prerequisites. The datastore stores the password as-is, so it is hashed here
    the same way the CLI hashes it.
    """
    user = current_datastore.find_user(email=email)
    if user is not None:
        return user

    user = current_datastore.create_user(
        email=email,
        password=hash_password(password),
        active=True,
        confirmed_at=datetime.now(UTC),
    )
    # the datastore only stages the user in the session, it does not commit
    db.session.commit()
    print(f"OK: created user {email!r}")
    return user


def create_community_if_missing():
    """Create the test community if it does not exist yet.

    Mirrors `invenio communities create test-community "Test Community"` from the
    prerequisites. The community is created with the system identity, which leaves
    it without an owner (the ownership component skips system creations), so
    `prepare_environment` adds the initial members right afterwards.
    """
    try:
        community_service.record_cls.pid.resolve(TC_SLUG)
        return
    except Exception:
        # any pid resolution failure (missing or deleted community) means it has
        # to be created
        pass

    community_service.create(
        system_identity,
        {
            "slug": TC_SLUG,
            "access": {
                "visibility": "public",
                "member_policy": "closed",
                "record_submission_policy": "open",
                "review_policy": "closed",
            },
            "metadata": {"title": "Test Community"},
        },
    )
    print(f"OK: created community {TC_SLUG!r}")


def reindex_users(*, user_emails):
    users_service = cast("UsersService", current_service_registry.get("users"))
    for user_email in user_emails:
        user = current_datastore.find_user(email=user_email)
        user_obj = users_service.read(system_identity, user.id)
        users_service.indexer.index(user_obj._user)
    users_service.indexer.refresh()


def allow_membership_requests(*, community_slug):
    """Open up the community so that non-members can request to join it."""
    data = community_service.read(system_identity, community_slug).data
    if data["access"]["member_policy"] != "open":
        data["access"]["member_policy"] = "open"
        community_service.update(system_identity, community_slug, data)


def associate_workflow_with_community(*, community_slug, workflow):
    """Associate the `workflow` workflow with the community if it does not have one yet.

    The community custom fields `workflow` (the default workflow given to the community's
    records) and `allowed_workflows` (the workflows accepted by the community) govern which
    workflow applies to records submitted to the community. Without them the record requests
    (community review, changed metadata) can not be routed to the community's curators.
    """
    data = community_service.read(system_identity, community_slug).data
    custom_fields = data.get("custom_fields") or {}

    changed = False
    if not custom_fields.get("workflow"):
        custom_fields["workflow"] = workflow
        changed = True
    if not custom_fields.get("allowed_workflows"):
        custom_fields["allowed_workflows"] = [workflow]
        changed = True

    if changed:
        data["custom_fields"] = custom_fields
        community_service.update(system_identity, community_slug, data)


def remove_member(*, community_slug, email):
    """Remove a member from a community by email if the member exists."""
    user = current_datastore.find_user(email=email)
    if user is None:
        return

    community = community_service.record_cls.pid.resolve(community_slug)
    data = {"members": [{"type": "user", "id": str(user.id)}]}
    try:
        members_service.delete(system_identity, community.id, data)
    except InvalidMemberError:
        pass


def add_member(*, community_slug, email, role):
    """Add a member to a community with the given role.

    The member is removed first (if present) so the operation is idempotent and the
    requested role always wins, then added with the requested role.
    """
    remove_member(community_slug=community_slug, email=email)

    user = current_datastore.find_user(email=email)
    if user is None:
        return

    community = community_service.record_cls.pid.resolve(community_slug)
    data = {"members": [{"type": "user", "id": str(user.id)}], "role": role}
    members_service.add(system_identity, community.id, data)


def add_member_if_missing(*, community_slug, email, role):
    """Add a member with the given role to the community only if they are not one yet.

    Unlike `add_member`, an existing member is left alone (only a drifted role is
    corrected): the remove-and-re-add cycle would trip ``members_service.delete``
    refusing to leave the community without an owner when the member is its only
    owner. Membership is checked in the database rather than in the search index,
    so freshly added members are seen right away.
    """
    user = current_datastore.find_user(email=email)
    if user is None:
        return

    community = community_service.record_cls.pid.resolve(community_slug)
    members = members_service.record_cls.get_members(community.id, members=[{"type": "user", "id": str(user.id)}])
    member = next((m for m in members if m.model.active), None)
    if member is not None:
        if member.model.role == role:
            print(f"OK: {email!r} is already a {role!r} of community {community_slug!r}")
            return
        members_service.update(
            system_identity,
            community.id,
            {"members": [{"type": "user", "id": str(user.id)}], "role": role},
        )
        print(f"OK: set {email!r}'s role in community {community_slug!r} to {role!r}")
        return

    members_service.add(
        system_identity,
        community.id,
        {"members": [{"type": "user", "id": str(user.id)}], "role": role},
    )
    print(f"OK: added {email!r} to community {community_slug!r} as {role!r}")


def decline_pending_membership_request(*, community_slug, email):
    """Decline a user's pending membership request for a community, if one exists.

    Needed to make repeated runs of this script idempotent, since a user can only have one
    membership request per community at a time.
    """
    user = current_datastore.find_user(email=email)
    if user is None:
        return

    community = community_service.record_cls.pid.resolve(community_slug)
    for request in members_service.search_membership_requests(system_identity, community.id):
        member = request["member"]
        if member["type"] == "user" and member["id"] == str(user.id) and request["request"]["is_open"]:
            try:
                current_requests_service.execute_action(system_identity, request["request"]["id"], "decline")
            except:
                pass


def cancel_pending_invitation(*, community_slug, email):
    """Cancel a user's pending invitation for a community, if one exists.

    Needed to make repeated runs of this script idempotent, since a user can only have one
    invitation per community at a time. An invitation left open blocks a new invitation and, the
    same way as an open membership request, any further membership of that user in the community,
    because both are backed by the same inactive member entry.
    """
    user = current_datastore.find_user(email=email)
    if user is None:
        return

    community = community_service.record_cls.pid.resolve(community_slug)
    for invitation in members_service.search_invitations(system_identity, community.id):
        member = invitation["member"]
        if member["type"] == "user" and member["id"] == str(user.id) and invitation["request"]["is_open"]:
            try:
                current_requests_service.execute_action(system_identity, invitation["request"]["id"], "cancel")
            except:
                pass


def open_invitation_request_id(*, community_id, email):
    """Return the id of the user's open invitation request in a community."""
    user = current_datastore.find_user(email=email)
    for invitation in members_service.search_invitations(system_identity, community_id):
        member = invitation["member"]
        if member["type"] == "user" and member["id"] == str(user.id) and invitation["request"]["is_open"]:
            return invitation["request"]["id"]

    raise AssertionError(f"No open invitation for {email!r} in community {community_id}.")


@contextlib.contextmanager
def record_notifications():
    """Capture emails that would be sent via notifications instead of actually sending them.

    Patches the notification manager's dispatch step (the point right before a backend's
    ``send()`` is invoked) for the duration of the context, so no real email is sent.
    """
    recorded = []

    # has to stay positional, it replaces the manager's own handle_dispatch
    def recording_handle_dispatch(backend_id, recipient, notification):
        if backend_id == "email":
            email = current_notifications_manager.backends[backend_id]._resolve_email(recipient)
            if notification.type == "comment-request-event.create":
                print("DEBUG dispatch", email, "request=", notification.context.get("request"))
            if email:
                recorded.append(email)

    original_handle_dispatch = current_notifications_manager.handle_dispatch
    current_notifications_manager.handle_dispatch = recording_handle_dispatch
    try:
        yield recorded
    finally:
        current_notifications_manager.handle_dispatch = original_handle_dispatch


def _assert_notification_recipients(*, action_description, sent_emails, expected_recipients):
    expected = set(expected_recipients)
    actual = set(sent_emails)
    if actual != expected:
        raise AssertionError(
            f"Notification recipients mismatch for {action_description}: "
            f"missing={sorted(expected - actual)}, unexpected={sorted(actual - expected)}"
        )
    print(f"OK: {action_description} notifications sent to {sorted(actual)}")


def create_request_check_emails(*, creator, request_type, request_payload, community_slug, expected_recipients) -> str:
    """Create a request as `creator` and check that email notifications go to the expected recipients.

    The request is submitted for the community identified by `community_slug`. Membership
    requests are routed through ``members_service.request_membership`` (the only path that
    actually builds and sends the submission notification); everything else goes through the
    generic ``requests_service.create`` with the community as receiver.

    Returns the id of the created request.
    """
    request_type_id = request_type if isinstance(request_type, str) else request_type.type_id

    community = community_service.record_cls.pid.resolve(community_slug)

    with record_notifications() as sent_emails, current_runtime.login_user(creator):
        identity = g.identity
        if request_type_id == MembershipRequestRequestType.type_id:
            created_request = members_service.request_membership(identity, community.id, request_payload)
        else:
            if isinstance(request_type, str):
                request_type = current_request_type_registry.lookup(request_type, quiet=False)
            created_request = current_requests_service.create(
                identity,
                request_payload,
                request_type,
                receiver={"community": str(community.id)},
            )

    _assert_notification_recipients(
        action_description=f"creating request type {request_type_id!r}",
        sent_emails=sent_emails,
        expected_recipients=expected_recipients,
    )
    return created_request.data["id"]


def invite_to_community_check_emails(*, inviter, invitee, role, community_slug, expected_recipients) -> str:
    """Invite `invitee` to the community as `inviter` and check that email notifications go to the expected recipients.

    Invitations go through ``members_service.invite``, the only path that creates the
    ``CommunityInvitation`` request - with the community as its creator and the invited user as its
    receiver - together with the inactive member entry and the submission notification. ``invite``
    returns only ``True``, so the id of the created request has to be looked up afterwards.

    Returns the id of the created invitation request.
    """
    community = community_service.record_cls.pid.resolve(community_slug)
    user = current_datastore.find_user(email=invitee)

    with record_notifications() as sent_emails, current_runtime.login_user(inviter):
        members_service.invite(
            g.identity,
            community.id,
            {
                "members": [{"type": "user", "id": str(user.id)}],
                "role": role,
                "message": f"Please join the community as a {role}.",
            },
        )

    _assert_notification_recipients(
        action_description=f"inviting {invitee!r} as {role!r} to community {community_slug!r}",
        sent_emails=sent_emails,
        expected_recipients=expected_recipients,
    )
    return open_invitation_request_id(community_id=community.id, email=invitee)


def accept_request_check_emails(*, actor, request_id, expected_recipients):
    """Accept a request as `actor` and check that email notifications go to the expected recipients."""
    with record_notifications() as sent_emails, current_runtime.login_user(actor):
        current_requests_service.execute_action(g.identity, request_id, "accept")

    _assert_notification_recipients(
        action_description=f"accepting request {request_id}",
        sent_emails=sent_emails,
        expected_recipients=expected_recipients,
    )


def decline_request_check_emails(*, actor, request_id, expected_recipients):
    """Decline a request as `actor` and check that email notifications go to the expected recipients."""
    with record_notifications() as sent_emails, current_runtime.login_user(actor):
        current_requests_service.execute_action(g.identity, request_id, "decline")

    _assert_notification_recipients(
        action_description=f"declining request {request_id}",
        sent_emails=sent_emails,
        expected_recipients=expected_recipients,
    )


def add_comment_check_emails(*, email, request_id, comment_text, expected_recipients):
    """Add a comment on `request_id` as `email` and check that email notifications go to the expected recipients."""
    with record_notifications() as sent_emails, current_runtime.login_user(email):
        current_events_service.create(
            g.identity,
            request_id,
            {"payload": {"content": comment_text}},
            CommentEventType,
        )

    _assert_notification_recipients(
        action_description=f"commenting on request {request_id}",
        sent_emails=sent_emails,
        expected_recipients=expected_recipients,
    )


def set_member_role(*, email, role, setter_email, expected_recipients):
    """Set a community member's role as `setter_email` and check the expected notifications fire.

    A membership request is always granted the "reader" role, regardless of what the requester
    asked for in their message, so this is how an owner/curator would honor a request such as
    "I want to become a curator" after accepting it. Role changes on an active member do not
    trigger any notification, so no recipients are expected.
    """
    user = current_datastore.find_user(email=email)
    community = community_service.record_cls.pid.resolve(TC_SLUG)

    with record_notifications() as sent_emails, current_runtime.login_user(setter_email):
        members_service.update(
            g.identity,
            community.id,
            {"members": [{"type": "user", "id": str(user.id)}], "role": role},
        )

    _assert_notification_recipients(
        action_description=f"setting {email}'s role to {role!r}",
        sent_emails=sent_emails,
        expected_recipients=expected_recipients,
    )


def check_adding_to_community_via_membership_request(*, requester, role):
    """Check the notifications sent when `requester` asks to join the community as `role`.

    Runs the request through each of its outcomes - declined by the owner, declined by the curator,
    accepted by the owner and accepted by the curator - checking the recipients of every notification
    sent on the way.

    A membership request has the user as its creator and the community as its receiver, so its
    submission is notified to the members that can act on it, ie. the roles the request type maps the
    community receiver to (needs_context["community_roles"], see oarepo_communities CommunityRecipient)
    - owner and curator. The requester does not receive it, they created it.

    A comment on a request is notified to the request participants (the requester and the previous
    commenters) and, since the receiver is the community, to the members that can act on it as well.
    Members without rights on the request (reader, submitter) must not see it. The member writing the
    comment never receives it (UserRecipientFilter).

    The decision itself is notified to the requester only.
    """
    message = {"message": f"I would like to join as a {role}."}

    request_id = create_request_check_emails(
        creator=requester,
        request_type=MembershipRequestRequestType,
        request_payload=message,
        community_slug=TC_SLUG,
        expected_recipients=[CURATOR, OWNER],
    )
    add_comment_check_emails(
        email=OWNER,
        request_id=request_id,
        comment_text="Thanks for your request, we'll review it soon.",
        expected_recipients=[requester, CURATOR],
    )
    add_comment_check_emails(
        email=requester,
        request_id=request_id,
        comment_text="Thank you!",
        expected_recipients=[OWNER, CURATOR],
    )
    decline_request_check_emails(actor=OWNER, request_id=request_id, expected_recipients=[requester])

    request_id = create_request_check_emails(
        creator=requester,
        request_type=MembershipRequestRequestType,
        request_payload=message,
        community_slug=TC_SLUG,
        expected_recipients=[CURATOR, OWNER],
    )
    add_comment_check_emails(
        email=CURATOR,
        request_id=request_id,
        comment_text="Thanks for your request, we'll review it soon.",
        expected_recipients=[requester, OWNER],
    )
    add_comment_check_emails(
        email=requester,
        request_id=request_id,
        comment_text="Thank you!",
        expected_recipients=[CURATOR, OWNER],
    )
    decline_request_check_emails(actor=CURATOR, request_id=request_id, expected_recipients=[requester])

    request_id = create_request_check_emails(
        creator=requester,
        request_type=MembershipRequestRequestType,
        request_payload=message,
        community_slug=TC_SLUG,
        expected_recipients=[CURATOR, OWNER],
    )
    add_comment_check_emails(
        email=OWNER,
        request_id=request_id,
        comment_text="Thanks for your request, we'll review it soon.",
        expected_recipients=[requester, CURATOR],
    )
    add_comment_check_emails(
        email=requester,
        request_id=request_id,
        comment_text="Thank you!",
        expected_recipients=[OWNER, CURATOR],
    )
    accept_request_check_emails(actor=OWNER, request_id=request_id, expected_recipients=[requester])
    set_member_role(email=requester, role=role, setter_email=OWNER, expected_recipients=[])
    remove_member(community_slug=TC_SLUG, email=requester)

    request_id = create_request_check_emails(
        creator=requester,
        request_type=MembershipRequestRequestType,
        request_payload=message,
        community_slug=TC_SLUG,
        expected_recipients=[CURATOR, OWNER],
    )
    add_comment_check_emails(
        email=CURATOR,
        request_id=request_id,
        comment_text="Thanks for your request, we'll review it soon.",
        expected_recipients=[requester, OWNER],
    )
    add_comment_check_emails(
        email=requester,
        request_id=request_id,
        comment_text="Thank you!",
        expected_recipients=[CURATOR, OWNER],
    )
    accept_request_check_emails(actor=CURATOR, request_id=request_id, expected_recipients=[requester])
    set_member_role(email=requester, role=role, setter_email=CURATOR, expected_recipients=[])


def check_adding_to_community_via_invitation(*, inviter, invitee, role):
    """Check the notifications sent when `inviter` invites `invitee` to the community as `role`.

    Runs the invitation through both outcomes - accepted and declined by the invited user - checking
    the recipients of every notification sent on the way.

    An invitation is the mirror image of a membership request: the community is its creator and the
    invited user its receiver. Its submission is therefore notified only to the invited user
    (UserRecipient on request.receiver); the inviter is not notified of their own invitation.

    A comment is notified to both parties of the invitation: the invited user (request.receiver) and
    the members that can act on it (the community in request.created_by resolved to its manage
    roles), minus its author. Members without rights on the invitation cannot even comment on it.

    The decision itself is notified back to the members that can act on the invitation - owner and
    curator. The invited user is not among them, not even after accepting, when they join with a role
    without rights on the request.
    """
    other_manager = CURATOR if inviter == OWNER else OWNER

    # the invitee must not be a member and must have no request or invitation pending
    cancel_pending_invitation(community_slug=TC_SLUG, email=invitee)
    decline_pending_membership_request(community_slug=TC_SLUG, email=invitee)
    remove_member(community_slug=TC_SLUG, email=invitee)

    request_id = invite_to_community_check_emails(
        inviter=inviter,
        invitee=invitee,
        role=role,
        community_slug=TC_SLUG,
        expected_recipients=[invitee],
    )
    add_comment_check_emails(
        email=inviter,
        request_id=request_id,
        comment_text="We'd be glad to have you in the community.",
        expected_recipients=[invitee, other_manager],
    )
    add_comment_check_emails(
        email=invitee,
        request_id=request_id,
        comment_text="Thanks, I'll think about it.",
        expected_recipients=[OWNER, CURATOR],
    )
    accept_request_check_emails(actor=invitee, request_id=request_id, expected_recipients=[OWNER, CURATOR])
    remove_member(community_slug=TC_SLUG, email=invitee)

    request_id = invite_to_community_check_emails(
        inviter=inviter,
        invitee=invitee,
        role=role,
        community_slug=TC_SLUG,
        expected_recipients=[invitee],
    )
    add_comment_check_emails(
        email=inviter,
        request_id=request_id,
        comment_text="We'd be glad to have you in the community.",
        expected_recipients=[invitee, other_manager],
    )
    add_comment_check_emails(
        email=invitee,
        request_id=request_id,
        comment_text="Thanks, I'll rather not.",
        expected_recipients=[OWNER, CURATOR],
    )
    decline_request_check_emails(actor=invitee, request_id=request_id, expected_recipients=[OWNER, CURATOR])

    # the invitee must have been left out of the community by the declined invitation
    remove_member(community_slug=TC_SLUG, email=invitee)


def prepare_environment():
    """Prepare the environment for the tests.

    Checks the prerequisites listed in the module header and creates whatever is
    missing - the users, the community and the initial community members - so the
    script also runs against a fresh instance, then resets the state the tests
    depend on.
    """
    for email in (CURATOR, OWNER, READER, SUBMITTER, EXTRA_READER, EXTRA_SUBMITTER):
        create_user_if_missing(email)
    create_community_if_missing()
    add_member_if_missing(community_slug=TC_SLUG, email=OWNER, role="owner")
    add_member_if_missing(community_slug=TC_SLUG, email=CURATOR, role="curator")
    add_member_if_missing(community_slug=TC_SLUG, email=EXTRA_READER, role="reader")
    add_member_if_missing(community_slug=TC_SLUG, email=EXTRA_SUBMITTER, role="submitter")

    reindex_users(user_emails=(CURATOR, OWNER, READER, SUBMITTER, EXTRA_READER, EXTRA_SUBMITTER))
    allow_membership_requests(community_slug=TC_SLUG)
    associate_workflow_with_community(community_slug=TC_SLUG, workflow="community")
    remove_member(community_slug=TC_SLUG, email=READER)
    remove_member(community_slug=TC_SLUG, email=SUBMITTER)
    decline_pending_membership_request(community_slug=TC_SLUG, email=READER)
    decline_pending_membership_request(community_slug=TC_SLUG, email=SUBMITTER)
    cancel_pending_invitation(community_slug=TC_SLUG, email=READER)
    cancel_pending_invitation(community_slug=TC_SLUG, email=SUBMITTER)


def test_membership_request():
    """Test that membership requests are handled correctly."""
    for requester, role in ((READER, "reader"), (SUBMITTER, "submitter")):
        check_adding_to_community_via_membership_request(requester=requester, role=role)


def test_invitation_to_community():
    """Test that invitations to the community are handled correctly."""
    for inviter, invitee, role in (
        (OWNER, READER, "reader"),
        (CURATOR, READER, "reader"),
        (OWNER, SUBMITTER, "submitter"),
        (CURATOR, SUBMITTER, "submitter"),
    ):
        check_adding_to_community_via_invitation(inviter=inviter, invitee=invitee, role=role)


def create_record_with_file(identity):
    """Create a draft record as `identity` and attach a small sample file to it.

    Returns the id of the created draft.
    """
    record_data = {
        "files": {"enabled": True},
        "metadata": {
            "title": "Test Record",
            "creators": [
                {
                    "role": {"id": "Other"},
                    "person_or_org": {
                        "name": "Novák, Jan",
                        "type": "personal",
                        "given_name": "Jan",
                        "family_name": "Novák",
                    },
                    "affiliations": [{"name": "Univerzita Karlova"}],
                }
            ],
            "resource_type": {"id": "c_ddb1"},
            "publication_date": "2024-01-01",
            "publisher": "CESNET",
        },
    }
    response = datasets_service.create(identity, record_data).to_dict()
    assert response.get("errors") is None
    rec_id = response["id"]

    # upload a small sample file
    datasets_service.draft_files.init_files(identity, rec_id, [{"key": "sample.txt"}])
    datasets_service.draft_files.set_file_content(identity, rec_id, "sample.txt", BytesIO(b"hello"))
    datasets_service.draft_files.commit_file(identity, rec_id, "sample.txt")
    return rec_id


def submit_record_for_review(*, community_slug, submitter_email, expected_recipients) -> tuple:
    """Create a record with a small file as `submitter_email` and submit it for review.

    The record is submitted for review by the community identified by `community_slug`, which
    publishes it and moves the review request from draft to submit state. Submission is
    notified to the members that can act on the request, ie. the community's owner and curator.

    Returns the ids of the created record and of its review request.
    """
    community = community_service.record_cls.pid.resolve(community_slug)

    with current_runtime.login_user(submitter_email):
        identity = g.identity

        rec_id = create_record_with_file(identity)
        print(f"OK: submitter {submitter_email!r} created draft record {rec_id}")

        with record_notifications() as sent_emails:
            draft_rec = datasets_service.read_draft(identity, rec_id, expand=True)
            review = datasets_service.review.create(
                identity,
                {"type": "community-submission", "receiver": {"community": str(community.id)}},
                draft_rec._record,
            )
            print(f"OK: review request {review.id} created for record {rec_id}")

            datasets_service.review.submit(identity, rec_id)

    _assert_notification_recipients(
        action_description=f"submitting record {rec_id} for review by community {community_slug!r}",
        sent_emails=sent_emails,
        expected_recipients=expected_recipients,
    )
    return rec_id, review.id


def test_record_requests() -> list:
    """Test the notifications sent when a submitter submits a record to the community.

    The submitter is (re)added to the community with the "submitter" role. Record review
    requests are then run through both outcomes - declined by the curator and by the owner,
    accepted by the curator and by the owner - checking the recipients of every notification
    sent on the way. Each request gets its own record submission, since a request is closed
    by the decision that ends it.

    A record review request has the submitter as its creator and the community as its
    receiver, so - like a membership request - its submission is notified to the members that
    can act on it (owner and curator), a comment to the other participants (the submitter and
    the previous commenters, never the commenter themselves) and the decision to the
    submitter only.

    Returns the ids of the records whose review requests were accepted.
    """
    add_member(community_slug=TC_SLUG, email=SUBMITTER, role="submitter")

    # a declined or accepted request is closed, so every pass needs its own submission
    for actor, other in ((CURATOR, OWNER), (OWNER, CURATOR)):
        rec_id, request_id = submit_record_for_review(
            community_slug=TC_SLUG,
            submitter_email=SUBMITTER,
            expected_recipients=[OWNER, CURATOR],
        )
        add_comment_check_emails(
            email=actor,
            request_id=request_id,
            comment_text="Thanks for your submission, we'll review it soon.",
            expected_recipients=[SUBMITTER, other],
        )
        add_comment_check_emails(
            email=SUBMITTER,
            request_id=request_id,
            comment_text="Thank you!",
            expected_recipients=[OWNER, CURATOR],
        )
        decline_request_check_emails(actor=actor, request_id=request_id, expected_recipients=[SUBMITTER])

    approved_record_ids = []
    for actor in (CURATOR, OWNER):
        rec_id, request_id = submit_record_for_review(
            community_slug=TC_SLUG,
            submitter_email=SUBMITTER,
            expected_recipients=[OWNER, CURATOR],
        )
        accept_request_check_emails(actor=actor, request_id=request_id, expected_recipients=[SUBMITTER])
        approved_record_ids.append(rec_id)

    return approved_record_ids


def submit_changed_metadata_request(*, record_id, creator_email, expected_recipients) -> str:
    """Create and submit a changed-metadata request for `record_id` as `creator_email`.

    The request is created on the record's draft without an explicit receiver, so oarepo
    requests picks the default receiver from the record's workflow - the community curator
    roles configured on the community workflow, ie. the curator and the owner here.
    Submitting the request locks the draft and notifies that receiver.

    Returns the id of the created request.
    """
    with record_notifications() as sent_emails, current_runtime.login_user(creator_email):
        draft_record = datasets_service.read_draft(g.identity, record_id)._record
        request = current_requests_service.create(
            g.identity,
            {},
            PublishChangedMetadataRequestType.type_id,
            receiver=None,
            topic=draft_record,
        )
        current_requests_service.execute_action(g.identity, request.id, "submit")

    _assert_notification_recipients(
        action_description=f"submitting changed metadata of record {record_id} for review",
        sent_emails=sent_emails,
        expected_recipients=expected_recipients,
    )
    return request.id


def change_record_title(*, record_id, editor_email, new_title):
    """Create a draft of `record_id` as `editor_email` (if it does not exist) and change its title.

    Changing draft metadata does not trigger any notification. After an acceptance publishes
    the changed metadata, calling this again creates the next draft of the freshly published
    record.
    """
    with current_runtime.login_user(editor_email):
        draft = datasets_service.edit(g.identity, record_id)
        draft_data = draft.to_dict()
        draft_data["metadata"]["title"] = new_title
        datasets_service.update_draft(g.identity, draft.id, draft_data)


def test_change_metadata(approved_record_id):
    """Test the notifications sent when the submitter changes metadata of an approved record.

    The submitter (the record's owner) edits the approved record, changes its title and submits
    the changed metadata for review via a ``publish_changed_metadata`` request. The request is
    created without a receiver, which is picked from the record's workflow as the community's
    curator roles (curator and owner here), so the submit notification goes to them, a comment
    to the other participants (the submitter, the receivers and the previous commenters, never
    the commenter themselves) and the decision to the creator, ie. the submitter.

    The changed metadata is run through each of its outcomes - declined by the curator,
    declined by the owner, accepted by the curator and accepted by the owner - checking the
    recipients of every notification sent on the way. A declined request is closed but leaves
    the draft intact so the next request can be created on it, while an accepted one publishes
    the draft, so every acceptance needs a freshly changed draft.
    """
    # as the record's owner, edit it and change the title
    change_record_title(record_id=approved_record_id, editor_email=SUBMITTER, new_title="Changed title")
    print(f"OK: submitter {SUBMITTER!r} changed the title of record {approved_record_id}")

    # every decline closes its request but keeps the draft for the next one
    for actor, other in ((CURATOR, OWNER), (OWNER, CURATOR)):
        request_id = submit_changed_metadata_request(
            record_id=approved_record_id,
            creator_email=SUBMITTER,
            expected_recipients=[OWNER, CURATOR],
        )
        add_comment_check_emails(
            email=actor,
            request_id=request_id,
            comment_text="Thanks for the update, we'll review it soon.",
            expected_recipients=[SUBMITTER, other],
        )
        add_comment_check_emails(
            email=SUBMITTER,
            request_id=request_id,
            comment_text="Thank you!",
            expected_recipients=[OWNER, CURATOR],
        )
        decline_request_check_emails(actor=actor, request_id=request_id, expected_recipients=[SUBMITTER])

    # an acceptance publishes the changed metadata, so each one needs its own changed draft
    for round_, actor in enumerate((CURATOR, OWNER), start=2):
        change_record_title(
            record_id=approved_record_id,
            editor_email=SUBMITTER,
            new_title=f"Changed title (round {round_})",
        )
        request_id = submit_changed_metadata_request(
            record_id=approved_record_id,
            creator_email=SUBMITTER,
            expected_recipients=[OWNER, CURATOR],
        )
        accept_request_check_emails(actor=actor, request_id=request_id, expected_recipients=[SUBMITTER])


def create_new_version_with_file(*, record_id, submitter_email, file_key) -> str:
    """Create a new version of `record_id` as `submitter_email` and upload a new file to it.

    A record pid always resolves to the very version it was minted for - publishing
    a new version mints a new pid from the new version draft - so once a newer
    version has been published, the given `record_id` points to an older version.
    The version chain is therefore followed via ``versions.latest_id`` to the latest
    published version, which is used as the base of the new version. Unlike a
    metadata-change draft, a new version draft starts with files disabled (its files
    are not copied from the previous version), so files are enabled on the draft
    before the new file is uploaded.

    If a draft of the next version already exists (left behind by a previously
    declined request), it is reused and the file is only added to it.

    Returns the id of the new version draft.
    """
    with current_runtime.login_user(submitter_email):
        identity = g.identity

        # a pid resolves to the version it was minted for, so when it points to an
        # older version (eg. after an acceptance published a newer one), follow the
        # version chain to the latest published version
        record = datasets_service.read(identity, record_id)._record
        if not record.versions.is_latest:
            latest_id = str(record.versions.latest_id)
            print(
                f"OK: record pid {record_id} points to v{record.versions.index}, "
                f"following the version chain to the latest version {latest_id}"
            )
            record_id = latest_id
            record = datasets_service.read(identity, record_id)._record
        print(
            f"OK: latest version of record {record_id} is v{record.versions.index} "
            f"(is_latest={record.versions.is_latest})"
        )

        draft = datasets_service.new_version(identity, record_id)
        draft_id = draft.id
        print(f"OK: submitter {submitter_email!r} created new version draft {draft_id} of record {record_id}")

        # the new version draft starts with files disabled, so enable them before
        # uploading (the whole draft data has to be sent back, an update carrying
        # only `files` would wipe the metadata)
        draft_data = draft.to_dict()
        draft_data.setdefault("files", {})["enabled"] = True
        datasets_service.update_draft(identity, draft_id, draft_data)

        datasets_service.draft_files.init_files(identity, draft_id, [{"key": file_key}])
        datasets_service.draft_files.set_file_content(
            identity, draft_id, file_key, BytesIO(f"content of {file_key}".encode())
        )
        datasets_service.draft_files.commit_file(identity, draft_id, file_key)
        print(f"OK: uploaded file {file_key!r} to new version draft {draft_id}")
    return draft_id


def submit_new_version_request(*, draft_id, creator_email, version, expected_recipients) -> str:
    """Create and submit a publish-new-version request for the draft `draft_id` as `creator_email`.

    Like a changed-metadata request, the request is created on the draft without an
    explicit receiver, so oarepo requests picks the default receiver from the record's
    workflow - the community curator roles configured on the community workflow, ie.
    the curator and the owner here. The `version` from the payload is stored on the
    draft at submission and published with the record once the request is accepted.
    Submitting the request notifies that receiver.

    Returns the id of the created request.
    """
    with record_notifications() as sent_emails, current_runtime.login_user(creator_email):
        draft_record = datasets_service.read_draft(g.identity, draft_id)._record
        request = current_requests_service.create(
            g.identity,
            {"payload": {"version": version}},
            PublishNewVersionRequestType.type_id,
            receiver=None,
            topic=draft_record,
        )
        current_requests_service.execute_action(g.identity, request.id, "submit")

    _assert_notification_recipients(
        action_description=f"submitting new version {version!r} of draft {draft_id} for review",
        sent_emails=sent_emails,
        expected_recipients=expected_recipients,
    )
    return request.id


def test_new_version(approved_record_id):
    """Test the notifications sent when the submitter publishes a new version of an approved record.

    The submitter (the record's owner) reads the latest version of the approved record,
    creates a new version of it, uploads a new file to the new version draft and submits
    it for review via a ``publish_new_version`` request. Like a changed-metadata request,
    it is created without a receiver, which is picked from the record's workflow as the
    community's curator roles (curator and owner here), so the submit notification goes
    to them, a comment to the other participants (the submitter, the receivers and the
    previous commenters, never the commenter themselves) and the decision to the creator,
    ie. the submitter.

    The new version is run through each of its outcomes - declined by the curator,
    declined by the owner, accepted by the curator and accepted by the owner - checking
    the recipients of every notification sent on the way. A declined request is closed
    but leaves the new version draft intact so the next request can be created on it,
    while an accepted one publishes the draft, so every acceptance needs a freshly
    created new version with a newly uploaded file.

    The version string in the request payload must be unique across the rounds: a
    declined submit leaves it on the draft and an accepted one on the published record,
    and a request reusing an already taken version string is rejected with
    ``VersionAlreadyExists``.
    """
    # as the record's owner, create a new version of it and upload a new file
    draft_id = create_new_version_with_file(
        record_id=approved_record_id, submitter_email=SUBMITTER, file_key="sample-new.txt"
    )

    # every decline closes its request but keeps the new version draft for the next one
    for round_, (actor, other) in enumerate(((CURATOR, OWNER), (OWNER, CURATOR)), start=1):
        request_id = submit_new_version_request(
            draft_id=draft_id,
            creator_email=SUBMITTER,
            version=f"2.0.{round_}",
            expected_recipients=[OWNER, CURATOR],
        )
        add_comment_check_emails(
            email=actor,
            request_id=request_id,
            comment_text="Thanks for the new version, we'll review it soon.",
            expected_recipients=[SUBMITTER, other],
        )
        add_comment_check_emails(
            email=SUBMITTER,
            request_id=request_id,
            comment_text="Thank you!",
            expected_recipients=[OWNER, CURATOR],
        )
        decline_request_check_emails(actor=actor, request_id=request_id, expected_recipients=[SUBMITTER])

    # an acceptance publishes the new version (minting a new record pid for it), so
    # each one needs its own new version draft built on the latest published version
    for round_, actor in enumerate((CURATOR, OWNER), start=3):
        draft_id = create_new_version_with_file(
            record_id=approved_record_id,
            submitter_email=SUBMITTER,
            file_key=f"sample-new-{round_}.txt",
        )
        request_id = submit_new_version_request(
            draft_id=draft_id,
            creator_email=SUBMITTER,
            version=f"2.0.{round_}",
            expected_recipients=[OWNER, CURATOR],
        )
        accept_request_check_emails(actor=actor, request_id=request_id, expected_recipients=[SUBMITTER])


# running ...
prepare_environment()
test_membership_request()
test_invitation_to_community()
approved_record_ids = test_record_requests()
test_change_metadata(approved_record_ids[0])
