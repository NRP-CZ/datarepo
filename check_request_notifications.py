# SPDX-FileCopyrightText: 2026 CESNET z.s.p.o.
# SPDX-License-Identifier: MIT

"""Check the notifications sent by the community and record request workflows.

Run through the invenio shell, ie. ``invenio shell check_request_notifications.py``,
and only when celery runs eagerly (``INVENIO_CELERY_ALWAYS_EAGER=1``), so that the
notification dispatch happens in-process and can be intercepted instead of sent.

The report is written to stdout as Markdown: every phase opens a heading of its
own, every step prints an ``OK:`` list item followed by a literal code block per
every email the notification would have produced, its ``To:`` header naming who
it went to. ``DEBUG`` lines go to stderr instead, so that stdout can be
redirected to a Markdown file on its own.

A mismatch with the expected notification recipients raises an ``AssertionError``.
"""

# ruff: noqa: T201

from __future__ import annotations

import contextlib
import re
import sys
import textwrap
from datetime import UTC, datetime
from io import BytesIO
from typing import TYPE_CHECKING, Any, NamedTuple, cast

from flask import current_app, g
from flask_security.utils import hash_password
from invenio_access.permissions import system_identity
from invenio_accounts.proxies import current_datastore
from invenio_communities.members.errors import InvalidMemberError
from invenio_communities.members.services.request import MembershipRequestRequestType
from invenio_db import db
from invenio_notifications.proxies import current_notifications_manager
from invenio_pidstore.errors import PersistentIdentifierError
from invenio_records_resources.proxies import current_service_registry
from invenio_records_resources.services.errors import PermissionDeniedError
from invenio_requests.customizations import CommentEventType
from invenio_requests.errors import CannotExecuteActionError
from invenio_requests.proxies import (
    current_events_service,
    current_request_type_registry,
    current_requests_service,
)
from marshmallow_utils.html import strip_html
from oarepo_requests.types import (
    PublishChangedMetadataRequestType,
    PublishDraftRequestType,
    PublishNewVersionRequestType,
)
from oarepo_runtime.proxies import current_runtime
from oarepo_runtime.typing import record_from_result

if TYPE_CHECKING:
    from collections.abc import Callable, Iterable, Iterator
    from uuid import UUID

    from flask_principal import Identity
    from invenio_accounts.models import User
    from invenio_communities.communities.services.service import CommunityService
    from invenio_communities.members import MemberService
    from invenio_notifications.backends.email import EmailNotificationBackend
    from invenio_notifications.models import Notification, Recipient
    from invenio_rdm_records.records.api import RDMRecord
    from invenio_rdm_records.services.services import RDMRecordService
    from invenio_requests.customizations import RequestType
    from invenio_users_resources.services.users.service import UsersService

if not current_app.config.get("CELERY_ALWAYS_EAGER"):
    raise RuntimeError("Set export INVENIO_CELERY_ALWAYS_EAGER=1 to run this script")

TC_SLUG = "test-community"

CURATOR = "tc_curator@demo.org"
OWNER = "tc_owner@demo.org"
READER = "tc_reader@demo.org"
SUBMITTER = "tc_submitter@demo.org"
EXTRA_READER = "tc_extra_reader@demo.org"
EXTRA_SUBMITTER = "tc_extra_submitter@demo.org"

INDIVIDUAL_SUBMITTER = "tc_individual_submitter@demo.org"
ADMINISTRATOR = "tc_administrator@demo.org"

community_service = cast("CommunityService", current_service_registry.get("communities"))
members_service: MemberService = community_service.members
datasets_service = cast("RDMRecordService", current_service_registry.get("datasets"))

# the width the literal blocks of the report are wrapped to, leaving room for the
# indentation of the list item they sit in, so that they never overflow the report
_BLOCK_WIDTH = 72

# the indentation of everything belonging to a step's list item
_INDENT = "  "


class _Mail(NamedTuple):
    """One email a notification would have produced.

    `text` is the email as it would have been sent, its `To:` and `Subject:` headers
    and its plain text body included, `error` why it could not be rendered instead,
    one of the two always being set.
    """

    address: str
    text: str | None
    error: str | None


def _heading(title: str, *, level: int = 3) -> None:
    """Open a phase of the report with a Markdown heading of the given level."""
    print(f"\n{'#' * level} {title}\n")


def _ok(text: str) -> None:
    """Report a step whose notifications went to the expected recipients."""
    print(f"- OK: {text}")


def _warn(text: str) -> None:
    """Report a step that was skipped because of the state the instance is in."""
    print(f"- WARN: {text}")


def _wrapped(text: str, *, width: int = _BLOCK_WIDTH) -> list[str]:
    """Hard-wrap `text` to `width` so that it cannot overflow the rendered block.

    A fenced code block is reproduced verbatim, with the reader scrolling sideways
    instead of the text reflowing, so the wrapping has to happen here. A word longer
    than the width is broken rather than left to overflow.
    """
    return textwrap.wrap(text, width=width, break_long_words=True, break_on_hyphens=False)


def _block(text: str) -> None:
    """Print `text` as a literal Markdown block indented under the current step.

    The block is fenced, so that Markdown keeps its content literal instead of eg.
    turning an email address into a link. The fence is made one backtick longer than
    the longest run of backticks in `text`, so that content carrying one cannot close
    the block early, and its lines are wrapped to `_BLOCK_WIDTH`, because a code block
    is not reflowed by the renderer.
    """
    longest = max((len(run) for run in re.findall(r"`+", text)), default=0)
    fence = "`" * max(3, longest + 1)

    print(f"\n{_INDENT}{fence}text")
    for line in text.splitlines():
        for part in _wrapped(line) or [""]:
            print(f"{_INDENT}{part}" if part else "")
    # no blank line after the block: whatever comes next, a heading, the next block or
    # the next step, already separates itself with one
    print(f"{_INDENT}{fence}")


def _mail(mail: _Mail) -> None:
    """Print one captured email as a literal Markdown block under the current step."""
    if mail.text is None:
        _block(f"To: {mail.address}\n(not rendered: {mail.error})")
        return

    _block(mail.text)


def _debug(*args: object) -> None:
    """Write a debug line to stderr, keeping it out of the Markdown report on stdout."""
    print("DEBUG", *args, file=sys.stderr)


def _community_id(*, community_slug: str) -> UUID:
    """Return the id of the community identified by `community_slug`.

    The id of a resolved record is optional in the invenio type stubs, because a
    record that was never committed does not have one, but a community resolved
    from its slug always has it.
    """
    community_id = community_service.record_cls.pid.resolve(community_slug).id
    if community_id is None:
        raise AssertionError(f"Community {community_slug!r} resolved without an id.")
    return community_id


def _user_member(user: User) -> dict[str, str]:
    """Return the member entry for the user `user` that the members services take."""
    return {"type": "user", "id": str(user.id)}


def _member_data(user: User, *, role: str | None = None, message: str | None = None) -> dict[str, Any]:
    """Return the payload the members service takes to address the single user `user`.

    The members are always addressed as a list of member entries, see `_user_member`;
    `role` and `message` are carried only when given, as not every call takes them.
    """
    data: dict[str, Any] = {"members": [_user_member(user)]}
    if role is not None:
        data["role"] = role
    if message is not None:
        data["message"] = message
    return data


# the weak default password is intentional, it creates the throwaway demo users
# that the checks below log in as
def create_user_if_missing(email: str, *, password: str = "123456") -> User:  # noqa: S107
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
    _ok(f"created user {email!r}")
    return user


def add_user_to_role(email: str, role: str) -> None:
    """Grant the global role `role` to the user `email`, creating the role if missing.

    The role has to exist before it is handed to the datastore: ``add_role_to_user``
    resolves a role passed by name with ``find_role`` and, when there is no such role,
    appends ``None`` to the user's roles, which only surfaces much later, on an
    unrelated commit, as ``FlushError: Can't flush None value found in collection``.

    The datastore only stages changes in the session, so the transaction is committed
    here. Granting a role does not register the user as changed in the datastore's
    change history, so the automatic post-commit reindex misses them: call this before
    `reindex_users`, which indexes the user's roles.
    """
    user = current_datastore.find_user(email=email)
    if user is None:
        _warn(f"cannot grant role {role!r} to non-existent user {email!r}")
        return

    role_obj = current_datastore.find_role(role) or current_datastore.create_role(name=role)
    if current_datastore.add_role_to_user(user, role_obj):
        _ok(f"added role {role!r} to user {email!r}")
    else:
        _ok(f"user {email!r} already has role {role!r}")
    db.session.commit()


def create_community_if_missing() -> None:
    """Create the test community if it does not exist yet.

    Mirrors `invenio communities create test-community "Test Community"` from the
    prerequisites. The community is created with the system identity, which leaves
    it without an owner (the ownership component skips system creations), so
    `prepare_environment` adds the initial members right afterwards.
    """
    with contextlib.suppress(PersistentIdentifierError):
        # any pid resolution failure (missing or deleted community) means it has
        # to be created
        community_service.record_cls.pid.resolve(TC_SLUG)
        return

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
    _ok(f"created community {TC_SLUG!r}")


def reindex_users(*, user_emails: Iterable[str]) -> None:
    """Index the users with the given emails so that they can be found by search.

    The indexer works on the user's ``UserAggregate`` record, which is the very
    record the users service reads to build its result items.
    """
    users_service = cast("UsersService", current_service_registry.get("users"))
    for user_email in user_emails:
        user = current_datastore.find_user(email=user_email)
        users_service.indexer.index(users_service.record_cls.get_record(user.id))
    users_service.indexer.refresh()


def allow_membership_requests(*, community_slug: str) -> None:
    """Open up the community so that non-members can request to join it."""
    data = community_service.read(system_identity, community_slug).data
    if data["access"]["member_policy"] != "open":
        data["access"]["member_policy"] = "open"
        community_service.update(system_identity, community_slug, data)


def associate_workflow_with_community(*, community_slug: str, workflow: str) -> None:
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


def remove_member(*, community_slug: str, email: str) -> None:
    """Remove a member from a community by email if the member exists."""
    user = current_datastore.find_user(email=email)
    if user is None:
        return

    with contextlib.suppress(InvalidMemberError):
        members_service.delete(system_identity, _community_id(community_slug=community_slug), _member_data(user))


def add_member(*, community_slug: str, email: str, role: str) -> None:
    """Add a member to a community with the given role.

    The member is removed first (if present) so the operation is idempotent and the
    requested role always wins, then added with the requested role.
    """
    remove_member(community_slug=community_slug, email=email)

    user = current_datastore.find_user(email=email)
    if user is None:
        return

    members_service.add(system_identity, _community_id(community_slug=community_slug), _member_data(user, role=role))


def add_member_if_missing(*, community_slug: str, email: str, role: str) -> None:
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

    community_id = _community_id(community_slug=community_slug)
    members = members_service.record_cls.get_members(community_id, members=[_user_member(user)])
    member = next((m for m in members if m.model.active), None)
    if member is not None:
        if member.model.role == role:
            _ok(f"{email!r} is already a {role!r} of community {community_slug!r}")
            return
        members_service.update(system_identity, community_id, _member_data(user, role=role))
        _ok(f"set {email!r}'s role in community {community_slug!r} to {role!r}")
        return

    members_service.add(system_identity, community_id, _member_data(user, role=role))
    _ok(f"added {email!r} to community {community_slug!r} as {role!r}")


def _open_request_id(entry: dict[str, Any], *, user_id: str) -> str | None:
    """Return the id of the request `entry` describes, if it is open and concerns `user_id`.

    `entry` is one hit of `members_service.search_membership_requests` or
    `members_service.search_invitations`, ie. a view pairing a request with the member it
    concerns; any other member or an already decided request yields `None`.
    """
    member = entry["member"]
    request = entry["request"]
    if member["type"] == "user" and member["id"] == user_id and request["is_open"]:
        return request["id"]
    return None


def _close_open_member_request(
    *,
    community_slug: str,
    email: str,
    search: Callable[[Identity, UUID], Iterable[dict[str, Any]]],
    action: str,
    noun: str,
) -> None:
    """Run `action` on the open request of `email` in the community, if it has one.

    `search` finds the pending requests of the kind, ie. either
    ``members_service.search_membership_requests`` or ``members_service.search_invitations``.
    A request that cannot be executed is only warned about, never raised: the searches read
    the search index, which can lag behind a request already decided by a previous run of
    this script. `noun` names what is being closed in that warning.
    """
    user = current_datastore.find_user(email=email)
    if user is None:
        return

    community_id = _community_id(community_slug=community_slug)
    for entry in search(system_identity, community_id):
        request_id = _open_request_id(entry, user_id=str(user.id))
        if request_id is None:
            continue
        try:
            current_requests_service.execute_action(system_identity, request_id, action)
        except (CannotExecuteActionError, PermissionDeniedError) as exc:
            _warn(f"could not {action} the {noun} of {email!r}: {exc}")


def decline_pending_membership_request(*, community_slug: str, email: str) -> None:
    """Decline a user's pending membership request for a community, if one exists.

    Needed to make repeated runs of this script idempotent, since a user can only have one
    membership request per community at a time.
    """
    _close_open_member_request(
        community_slug=community_slug,
        email=email,
        search=members_service.search_membership_requests,
        action="decline",
        noun="membership request",
    )


def cancel_pending_invitation(*, community_slug: str, email: str) -> None:
    """Cancel a user's pending invitation for a community, if one exists.

    Needed to make repeated runs of this script idempotent, since a user can only have one
    invitation per community at a time. An invitation left open blocks a new invitation and, the
    same way as an open membership request, any further membership of that user in the community,
    because both are backed by the same inactive member entry.
    """
    _close_open_member_request(
        community_slug=community_slug,
        email=email,
        search=members_service.search_invitations,
        action="cancel",
        noun="invitation",
    )


def open_invitation_request_id(*, community_id: UUID, email: str) -> str:
    """Return the id of the user's open invitation request in a community."""
    user = current_datastore.find_user(email=email)
    for invitation in members_service.search_invitations(system_identity, community_id):
        request_id = _open_request_id(invitation, user_id=str(user.id))
        if request_id is not None:
            return request_id

    raise AssertionError(f"No open invitation for {email!r} in community {community_id}.")


def _render_mail(
    *,
    backend: EmailNotificationBackend,
    notification: Notification,
    recipient: Recipient,
    address: str,
) -> _Mail:
    """Return the email `notification` would have produced for `recipient`.

    The mail is rendered the very way ``EmailNotificationBackend.send`` builds the
    message it hands to invenio-mail, its ``To:`` and ``Subject:`` headers and its
    plain text body included, so that the report shows the text the recipient would
    have read. It has to be rendered here, while the notification is dispatched,
    because the templates are resolved against the context of the action that
    produced the notification.

    A mail that cannot be rendered, eg. because the notification type has no email
    template, is reported on the mail itself rather than raised, so that a missing
    template does not look like a recipient mismatch.
    """
    try:
        content = backend.render_template(notification, recipient)
        body = strip_html(content["plain_body"]).strip()
        text = f"To: {address}\nSubject: {content['subject'].strip()}\n\n{body}"
    except Exception as exc:  # noqa: BLE001  - a broken mail must not fail the recipient check
        return _Mail(address=address, text=None, error=f"{type(exc).__name__}: {exc}")

    return _Mail(address=address, text=text, error=None)


@contextlib.contextmanager
def record_notifications() -> Iterator[list[_Mail]]:
    """Capture the emails that would be sent via notifications instead of sending them.

    Patches the notification manager's dispatch step (the point right before a backend's
    ``send()`` is invoked) for the duration of the context, so no real email is sent. The
    captured emails carry the text they would have had, see `_render_mail`.
    """
    recorded: list[_Mail] = []

    # has to stay positional, it replaces the manager's own handle_dispatch
    def recording_handle_dispatch(backend_id: str, recipient: Recipient, notification: Notification) -> None:
        if backend_id != "email":
            return

        backend = current_notifications_manager.backends[backend_id]
        # the email backend resolves the address itself, so use the very helper it
        # uses to know what address an email would have gone to
        email = backend._resolve_email(recipient)  # noqa: SLF001
        if not email:
            return

        if notification.type == "comment-request-event.create":
            _debug("dispatch", email, "request=", notification.context.get("request"))
        recorded.append(_render_mail(backend=backend, notification=notification, recipient=recipient, address=email))

    original_handle_dispatch = current_notifications_manager.handle_dispatch
    current_notifications_manager.handle_dispatch = recording_handle_dispatch
    try:
        yield recorded
    finally:
        current_notifications_manager.handle_dispatch = original_handle_dispatch


def _assert_notification_recipients(
    *,
    action_description: str,
    sent_mails: Iterable[_Mail],
    expected_recipients: Iterable[str],
) -> None:
    expected = set(expected_recipients)
    mails = sorted(sent_mails, key=lambda mail: mail.address)
    actual = {mail.address for mail in mails}
    if actual != expected:
        raise AssertionError(
            f"Notification recipients mismatch for {action_description}: "
            f"missing={sorted(expected - actual)}, unexpected={sorted(actual - expected)}"
        )
    _ok(f"{action_description} notifications sent to {len(actual)} recipient(s)")
    for mail in mails:
        _mail(mail)


@contextlib.contextmanager
def _check_notifications(
    *,
    email: str,
    action_description: str,
    expected_recipients: Iterable[str],
) -> Iterator[None]:
    """Act as `email`, capturing the emails the action sends, then check who they went to.

    The body of the `with` block performs the action whose notifications are checked; the
    captured mails are asserted against `expected_recipients` once the body has run and the
    notification dispatch has been restored, see `record_notifications`.
    """
    with record_notifications() as sent_mails, current_runtime.login_user(email):
        yield
    _assert_notification_recipients(
        action_description=action_description,
        sent_mails=sent_mails,
        expected_recipients=expected_recipients,
    )


@contextlib.contextmanager
def _check_permission_denied(*, email: str, action: str) -> Iterator[None]:
    """Act as `email` and require the action performed by the body to be refused.

    The body of the `with` block performs an action `email` must not be entitled to perform.
    Only a `PermissionDeniedError` passes the check; the action succeeding is a failure just
    like any other error, so that a permission policy widened by accident cannot go
    unnoticed. Nothing is notified by a refused action, so no notifications are recorded.
    """
    with current_runtime.login_user(email):
        try:
            yield
        except PermissionDeniedError:
            _ok(f"{email!r} is not allowed to {action}")
            return
    raise AssertionError(f"{email!r} should not have been allowed to {action}.")


def _check_no_access_to_request(*, request_id: str) -> None:
    """Check that an administrator is refused every action on `request_id`.

    Commenting on a request requires reading it, which is reserved to the creator and the
    receiver of the request, and deciding it is reserved to its receivers. An administrator
    is neither of those on a request of the individual workflow, which has no reviewer roles
    configured, so all three actions have to be refused.
    """
    with _check_permission_denied(email=ADMINISTRATOR, action=f"comment on request {request_id}"):
        current_events_service.create(
            g.identity,
            request_id,
            {"payload": {"content": "Let me take a look at it."}},
            CommentEventType,
        )
    with _check_permission_denied(email=ADMINISTRATOR, action=f"decline request {request_id}"):
        current_requests_service.execute_action(g.identity, request_id, "decline")
    with _check_permission_denied(email=ADMINISTRATOR, action=f"accept request {request_id}"):
        current_requests_service.execute_action(g.identity, request_id, "accept")


def create_request_check_emails(
    *,
    creator: str,
    request_type: type[RequestType] | str,
    request_payload: dict[str, Any],
    community_slug: str,
    expected_recipients: Iterable[str],
) -> str:
    """Create a request as `creator` and check that email notifications go to the expected recipients.

    The request is submitted for the community identified by `community_slug`. Membership
    requests are routed through ``members_service.request_membership`` (the only path that
    actually builds and sends the submission notification); everything else goes through the
    generic ``requests_service.create`` with the community as receiver.

    Returns the id of the created request.
    """
    request_type_id = request_type if isinstance(request_type, str) else request_type.type_id

    community_id = _community_id(community_slug=community_slug)

    with _check_notifications(
        email=creator,
        action_description=f"creating request type {request_type_id!r}",
        expected_recipients=expected_recipients,
    ):
        identity = g.identity
        if request_type_id == MembershipRequestRequestType.type_id:
            created_request = members_service.request_membership(identity, community_id, request_payload)
        else:
            if isinstance(request_type, str):
                request_type = current_request_type_registry.lookup(request_type, quiet=False)
            created_request = current_requests_service.create(
                identity,
                request_payload,
                request_type,
                receiver={"community": str(community_id)},
            )

    return created_request.data["id"]


def invite_to_community_check_emails(
    *,
    inviter: str,
    invitee: str,
    role: str,
    community_slug: str,
    expected_recipients: Iterable[str],
) -> str:
    """Invite `invitee` to the community as `inviter` and check that email notifications go to the expected recipients.

    Invitations go through ``members_service.invite``, the only path that creates the
    ``CommunityInvitation`` request - with the community as its creator and the invited user as its
    receiver - together with the inactive member entry and the submission notification. ``invite``
    returns only ``True``, so the id of the created request has to be looked up afterwards.

    Returns the id of the created invitation request.
    """
    community_id = _community_id(community_slug=community_slug)
    user = current_datastore.find_user(email=invitee)

    with _check_notifications(
        email=inviter,
        action_description=f"inviting {invitee!r} as {role!r} to community {community_slug!r}",
        expected_recipients=expected_recipients,
    ):
        members_service.invite(
            g.identity,
            community_id,
            _member_data(user, role=role, message=f"Please join the community as a {role}."),
        )

    return open_invitation_request_id(community_id=community_id, email=invitee)


def accept_request_check_emails(*, actor: str, request_id: str, expected_recipients: Iterable[str]) -> None:
    """Accept a request as `actor` and check that email notifications go to the expected recipients."""
    with _check_notifications(
        email=actor,
        action_description=f"accepting request {request_id}",
        expected_recipients=expected_recipients,
    ):
        current_requests_service.execute_action(g.identity, request_id, "accept")


def decline_request_check_emails(*, actor: str, request_id: str, expected_recipients: Iterable[str]) -> None:
    """Decline a request as `actor` and check that email notifications go to the expected recipients."""
    with _check_notifications(
        email=actor,
        action_description=f"declining request {request_id}",
        expected_recipients=expected_recipients,
    ):
        current_requests_service.execute_action(g.identity, request_id, "decline")


def add_comment_check_emails(
    *, email: str, request_id: str, comment_text: str, expected_recipients: Iterable[str]
) -> None:
    """Add a comment on `request_id` as `email` and check that email notifications go to the expected recipients."""
    with _check_notifications(
        email=email,
        action_description=f"commenting on request {request_id}",
        expected_recipients=expected_recipients,
    ):
        current_events_service.create(
            g.identity,
            request_id,
            {"payload": {"content": comment_text}},
            CommentEventType,
        )


def set_member_role(*, email: str, role: str, setter_email: str, expected_recipients: Iterable[str]) -> None:
    """Set a community member's role as `setter_email` and check the expected notifications fire.

    A membership request is always granted the "reader" role, regardless of what the requester
    asked for in their message, so this is how an owner/curator would honor a request such as
    "I want to become a curator" after accepting it. Role changes on an active member do not
    trigger any notification, so no recipients are expected.
    """
    user = current_datastore.find_user(email=email)
    community_id = _community_id(community_slug=TC_SLUG)

    with _check_notifications(
        email=setter_email,
        action_description=f"setting {email}'s role to {role!r}",
        expected_recipients=expected_recipients,
    ):
        members_service.update(g.identity, community_id, _member_data(user, role=role))


def _membership_request_with_comments(*, requester: str, message: dict[str, str], reviewer: str) -> str:
    """Open a membership request as `requester` and let it be answered in the test community.

    `reviewer`, one of the members that can act on the request, acknowledges it and the
    `requester` thanks them; every one of the three notifications is checked against the
    recipients it must have reached. Returns the id of the created request, which is left
    open for the caller to decide.
    """
    other_reviewer = CURATOR if reviewer == OWNER else OWNER

    request_id = create_request_check_emails(
        creator=requester,
        request_type=MembershipRequestRequestType,
        request_payload=message,
        community_slug=TC_SLUG,
        expected_recipients=[CURATOR, OWNER],
    )
    add_comment_check_emails(
        email=reviewer,
        request_id=request_id,
        comment_text="Thanks for your request, we'll review it soon.",
        expected_recipients=[requester, other_reviewer],
    )
    add_comment_check_emails(
        email=requester,
        request_id=request_id,
        comment_text="Thank you!",
        expected_recipients=[OWNER, CURATOR],
    )
    return request_id


def check_adding_to_community_via_membership_request(*, requester: str, role: str) -> None:
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
    _heading(f"Membership request of {requester} as {role}")

    message = {"message": f"I would like to join as a {role}."}

    request_id = _membership_request_with_comments(requester=requester, message=message, reviewer=OWNER)
    decline_request_check_emails(actor=OWNER, request_id=request_id, expected_recipients=[requester])

    request_id = _membership_request_with_comments(requester=requester, message=message, reviewer=CURATOR)
    decline_request_check_emails(actor=CURATOR, request_id=request_id, expected_recipients=[requester])

    request_id = _membership_request_with_comments(requester=requester, message=message, reviewer=OWNER)
    accept_request_check_emails(actor=OWNER, request_id=request_id, expected_recipients=[requester])
    set_member_role(email=requester, role=role, setter_email=OWNER, expected_recipients=[])
    remove_member(community_slug=TC_SLUG, email=requester)

    request_id = _membership_request_with_comments(requester=requester, message=message, reviewer=CURATOR)
    accept_request_check_emails(actor=CURATOR, request_id=request_id, expected_recipients=[requester])
    set_member_role(email=requester, role=role, setter_email=CURATOR, expected_recipients=[])


def _invitation_with_comments(*, inviter: str, invitee: str, role: str, invitee_reply: str) -> str:
    """Invite `invitee` to the test community as `inviter` and let both parties comment.

    `inviter` welcomes the `invitee` and the invitee answers with `invitee_reply`; every one
    of the three notifications is checked against the recipients it must have reached.
    Returns the id of the created invitation request, which is left open for the invitee to
    decide.
    """
    other_manager = CURATOR if inviter == OWNER else OWNER

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
        comment_text=invitee_reply,
        expected_recipients=[OWNER, CURATOR],
    )
    return request_id


def check_adding_to_community_via_invitation(*, inviter: str, invitee: str, role: str) -> None:
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
    _heading(f"Invitation of {invitee} as {role} by {inviter}")

    # the invitee must not be a member and must have no request or invitation pending
    cancel_pending_invitation(community_slug=TC_SLUG, email=invitee)
    decline_pending_membership_request(community_slug=TC_SLUG, email=invitee)
    remove_member(community_slug=TC_SLUG, email=invitee)

    request_id = _invitation_with_comments(
        inviter=inviter,
        invitee=invitee,
        role=role,
        invitee_reply="Thanks, I'll think about it.",
    )
    accept_request_check_emails(actor=invitee, request_id=request_id, expected_recipients=[OWNER, CURATOR])
    remove_member(community_slug=TC_SLUG, email=invitee)

    request_id = _invitation_with_comments(
        inviter=inviter,
        invitee=invitee,
        role=role,
        invitee_reply="Thanks, I'll rather not.",
    )
    decline_request_check_emails(actor=invitee, request_id=request_id, expected_recipients=[OWNER, CURATOR])

    # the invitee must have been left out of the community by the declined invitation
    remove_member(community_slug=TC_SLUG, email=invitee)


def prepare_environment() -> None:
    """Prepare the environment for the tests.

    Checks the prerequisites listed in the module header and creates whatever is
    missing - the users, the community and the initial community members - so the
    script also runs against a fresh instance, then resets the state the tests
    depend on.
    """
    for email in (
        CURATOR,
        OWNER,
        READER,
        SUBMITTER,
        EXTRA_READER,
        EXTRA_SUBMITTER,
        INDIVIDUAL_SUBMITTER,
        ADMINISTRATOR,
    ):
        create_user_if_missing(email)
    create_community_if_missing()
    add_member_if_missing(community_slug=TC_SLUG, email=OWNER, role="owner")
    add_member_if_missing(community_slug=TC_SLUG, email=CURATOR, role="curator")
    add_member_if_missing(community_slug=TC_SLUG, email=EXTRA_READER, role="reader")
    add_member_if_missing(community_slug=TC_SLUG, email=EXTRA_SUBMITTER, role="submitter")

    add_user_to_role(email=INDIVIDUAL_SUBMITTER, role="submitter")
    # the individual workflow has no reviewer roles configured, so the checks of that
    # workflow assert that this role grants nothing on somebody else's record
    add_user_to_role(email=ADMINISTRATOR, role="administrator")

    reindex_users(
        user_emails=(
            CURATOR,
            OWNER,
            READER,
            SUBMITTER,
            EXTRA_READER,
            EXTRA_SUBMITTER,
            INDIVIDUAL_SUBMITTER,
            ADMINISTRATOR,
        )
    )
    allow_membership_requests(community_slug=TC_SLUG)
    associate_workflow_with_community(community_slug=TC_SLUG, workflow="community")
    remove_member(community_slug=TC_SLUG, email=READER)
    remove_member(community_slug=TC_SLUG, email=SUBMITTER)
    decline_pending_membership_request(community_slug=TC_SLUG, email=READER)
    decline_pending_membership_request(community_slug=TC_SLUG, email=SUBMITTER)
    cancel_pending_invitation(community_slug=TC_SLUG, email=READER)
    cancel_pending_invitation(community_slug=TC_SLUG, email=SUBMITTER)


def test_membership_request() -> None:
    """Test that membership requests are handled correctly."""
    for requester, role in ((READER, "reader"), (SUBMITTER, "submitter")):
        check_adding_to_community_via_membership_request(requester=requester, role=role)


def test_invitation_to_community() -> None:
    """Test that invitations to the community are handled correctly."""
    for inviter, invitee, role in (
        (OWNER, READER, "reader"),
        (CURATOR, READER, "reader"),
        (OWNER, SUBMITTER, "submitter"),
        (CURATOR, SUBMITTER, "submitter"),
    ):
        check_adding_to_community_via_invitation(inviter=inviter, invitee=invitee, role=role)


def create_record_with_file(identity: Identity) -> str:
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
    if response.get("errors") is not None:
        raise AssertionError(f"Record creation failed with errors: {response['errors']}")
    rec_id = response["id"]

    # upload a small sample file
    datasets_service.draft_files.init_files(identity, rec_id, [{"key": "sample.txt"}])
    datasets_service.draft_files.set_file_content(identity, rec_id, "sample.txt", BytesIO(b"hello"))
    datasets_service.draft_files.commit_file(identity, rec_id, "sample.txt")
    return rec_id


def submit_record_for_review(
    *, community_slug: str, submitter_email: str, expected_recipients: Iterable[str]
) -> tuple[str, str]:
    """Create a record with a small file as `submitter_email` and submit it for review.

    The record is submitted for review by the community identified by `community_slug`, which
    publishes it and moves the review request from draft to submit state. Submission is
    notified to the members that can act on the request, ie. the community's owner and curator.

    Returns the ids of the created record and of its review request.
    """
    community_id = _community_id(community_slug=community_slug)

    with current_runtime.login_user(submitter_email):
        identity = g.identity

        rec_id = create_record_with_file(identity)
        _ok(f"submitter {submitter_email!r} created draft record {rec_id}")

        with record_notifications() as sent_mails:
            draft_record = record_from_result(datasets_service.read_draft(identity, rec_id, expand=True))
            review = datasets_service.review.create(
                identity,
                {"type": "community-submission", "receiver": {"community": str(community_id)}},
                draft_record,
            )
            _ok(f"review request {review.id} created for record {rec_id}")

            datasets_service.review.submit(identity, rec_id)

    _assert_notification_recipients(
        action_description=f"submitting record {rec_id} for review by community {community_slug!r}",
        sent_mails=sent_mails,
        expected_recipients=expected_recipients,
    )
    return rec_id, review.id


def test_record_requests() -> list[str]:
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
        _heading(f"Review request declined by {actor}")
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

    approved_record_ids: list[str] = []
    for actor in (CURATOR, OWNER):
        _heading(f"Review request accepted by {actor}")
        rec_id, request_id = submit_record_for_review(
            community_slug=TC_SLUG,
            submitter_email=SUBMITTER,
            expected_recipients=[OWNER, CURATOR],
        )
        accept_request_check_emails(actor=actor, request_id=request_id, expected_recipients=[SUBMITTER])
        approved_record_ids.append(rec_id)

    return approved_record_ids


def submit_changed_metadata_request(*, record_id: str, creator_email: str, expected_recipients: Iterable[str]) -> str:
    """Create and submit a changed-metadata request for `record_id` as `creator_email`.

    The request is created on the record's draft without an explicit receiver, so oarepo
    requests picks the default receiver from the record's workflow: on the community
    workflow the curator roles configured on the community, ie. the curator and the owner,
    and on the individual workflow its only reviewer, ie. the owner of the record. Either
    way the receiver is resolved only when the notification is built.

    Submitting the request locks the draft and notifies that receiver.

    Returns the id of the created request.
    """
    with _check_notifications(
        email=creator_email,
        action_description=f"submitting changed metadata of record {record_id} for review",
        expected_recipients=expected_recipients,
    ):
        draft_record = record_from_result(datasets_service.read_draft(g.identity, record_id))
        request = current_requests_service.create(
            g.identity,
            {},
            PublishChangedMetadataRequestType.type_id,
            receiver=None,
            topic=draft_record,
        )
        current_requests_service.execute_action(g.identity, request.id, "submit")

    return request.id


def change_record_title(*, record_id: str, editor_email: str, new_title: str) -> None:
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


def test_change_metadata(approved_record_id: str) -> None:
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
    _ok(f"submitter {SUBMITTER!r} changed the title of record {approved_record_id}")

    # every decline closes its request but keeps the draft for the next one
    for actor, other in ((CURATOR, OWNER), (OWNER, CURATOR)):
        _heading(f"Changed metadata declined by {actor}")
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
        _heading(f"Changed metadata accepted by {actor}")
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


def create_new_version_with_file(*, record_id: str, submitter_email: str, file_key: str) -> str:
    """Create a new version of `record_id` as `submitter_email` and upload a new file to it.

    A record pid always resolves to the very version it was minted for - publishing
    a new version mints a new pid from the new version draft and leaves the pid of the
    published version where it is - so once a newer version has been published, the
    given `record_id` points to an older version. The version chain to the latest
    published version is not followed here, ``new_version`` resolves it on its own and
    builds the draft from the latest published version of the record's parent. It could
    not be followed through ``versions.latest_id`` anyway, as that holds the *id* of the
    latest record and not its pid value, so reading it as a pid fails with
    ``PIDDoesNotExistError`` (``read_latest`` is the service method that follows the
    chain). Unlike a metadata-change draft, a new version draft starts with files
    disabled (its files are not copied from the previous version), so files are enabled
    on the draft before the new file is uploaded.

    If a draft of the next version already exists (left behind by a previously
    declined request), it is reused and the file is only added to it.

    Returns the id of the new version draft.
    """
    with current_runtime.login_user(submitter_email):
        identity = g.identity

        # the pid can point to an older version (eg. after an acceptance published a
        # newer one), which matters only for what is reported below - the new version is
        # built on the latest published version of the parent either way. The cast to
        # RDMRecord is needed because record_from_result is typed against the base
        # Record, which does not declare the versions systemfield the datasets records
        # carry
        record = cast("RDMRecord", record_from_result(datasets_service.read(identity, record_id)))
        _ok(
            f"record pid {record_id} points to v{record.versions.index}, the latest "
            f"published version of its parent is v{record.versions.latest_index} "
            f"(is_latest={record.versions.is_latest})"
        )

        draft = datasets_service.new_version(identity, record_id)
        draft_id = draft.id
        _ok(f"submitter {submitter_email!r} created new version draft {draft_id} of record {record_id}")

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
        _ok(f"uploaded file {file_key!r} to new version draft {draft_id}")
    return draft_id


def submit_new_version_request(
    *, draft_id: str, creator_email: str, version: str, expected_recipients: Iterable[str]
) -> str:
    """Create and submit a publish-new-version request for the draft `draft_id` as `creator_email`.

    Like a changed-metadata request, the request is created on the draft without an
    explicit receiver, so oarepo requests picks the default receiver from the record's
    workflow: on the community workflow the curator roles configured on the community,
    ie. the curator and the owner, and on the individual workflow its only reviewer, ie.
    the owner of the record. The `version` from the payload is stored on the draft at
    submission and published with the record once the request is accepted. Submitting the
    request notifies that receiver.

    Returns the id of the created request.
    """
    with _check_notifications(
        email=creator_email,
        action_description=f"submitting new version {version!r} of draft {draft_id} for review",
        expected_recipients=expected_recipients,
    ):
        draft_record = record_from_result(datasets_service.read_draft(g.identity, draft_id))
        request = current_requests_service.create(
            g.identity,
            {"payload": {"version": version}},
            PublishNewVersionRequestType.type_id,
            receiver=None,
            topic=draft_record,
        )
        current_requests_service.execute_action(g.identity, request.id, "submit")

    return request.id


def test_new_version(approved_record_id: str) -> None:
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
        _heading(f"New version declined by {actor}")
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
        _heading(f"New version accepted by {actor}")
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


def submit_publish_draft_request(*, draft_id: str, creator_email: str, expected_recipients: Iterable[str]) -> str:
    """Create and submit a publish-draft request for the draft `draft_id` as `creator_email`.

    The draft was created outside of any community, so the individual workflow applies and
    the request is created without an explicit receiver, which oarepo requests picks from
    the draft's workflow. That workflow is configured (see ``invenio.cfg``) without any
    reviewer role and with self-review enabled, so its only reviewer is the owner of the
    draft who also holds the "submitter" role the workflow requires to create a draft, ie.
    the creator of the request. Neither is expanded on creation, the entity being resolved
    only when the notification is built. Submitting the request notifies that receiver, ie.
    the creator themselves.

    Returns the id of the created request.
    """
    with _check_notifications(
        email=creator_email,
        action_description=f"submitting draft {draft_id} for individual review",
        expected_recipients=expected_recipients,
    ):
        draft_record = record_from_result(datasets_service.read_draft(g.identity, draft_id))
        request = current_requests_service.create(
            g.identity,
            {},
            PublishDraftRequestType.type_id,
            receiver=None,
            topic=draft_record,
        )
        current_requests_service.execute_action(g.identity, request.id, "submit")

    return request.id


def test_record_individual() -> str:
    """Test the notifications sent when a submitter publishes a record outside a community.

    The submitter, who holds the global "submitter" role the individual workflow requires
    to create a draft, creates a draft record outside of any community - so the individual
    workflow governs it rather than the community one - uploads a single file to it and
    submits it for review through a ``publish_draft`` request.

    The individual workflow is configured (see ``invenio.cfg``) without any reviewer role and
    with self-review enabled, so its only reviewer is the owner of the draft who holds the
    "submitter" role, ie. the submitter themselves. Nobody else has any rights on the record
    or on its request, the members of the global "administrator" role included, which makes
    the individual workflow the mirror image of the community one: the review is not routed
    to anybody but the submitter, who therefore also decides their own request.

    The actions on the record are therefore checked from both sides, refused when performed
    as an administrator and allowed, with the expected notifications, when performed as the
    submitter. The submission is notified to the submitter as the receiver of the request, a
    comment of theirs to nobody (they are its only participant and a comment never reaches its
    author) and the decision back to them as the creator of the request.

    The request is run through both outcomes - declined, then accepted on a freshly
    submitted request. A declined publish-draft request only moves the draft to the
    "revision_requested" state, so the second request is submitted over the very same draft,
    the way a submitter would respond to the review.

    Returns the id of the record published by the accepted request, which the changed
    metadata of an individual record are then submitted for review on.
    """
    with current_runtime.login_user(INDIVIDUAL_SUBMITTER):
        rec_id = create_record_with_file(g.identity)
    _ok(f"submitter {INDIVIDUAL_SUBMITTER!r} created individual draft record {rec_id}")

    _heading(f"Individual draft record {rec_id} with no review request yet")

    # the administrator is neither the owner of the draft nor a reviewer of the individual
    # workflow, which has no reviewer roles configured, so they have no rights on it
    with _check_permission_denied(email=ADMINISTRATOR, action=f"read the individual draft {rec_id}"):
        datasets_service.read_draft(g.identity, rec_id)

    # the draft is read here with the system identity, so that the refusal below is about
    # creating the request and not about reading the draft the request is created on
    draft_record = record_from_result(datasets_service.read_draft(system_identity, rec_id))
    with _check_permission_denied(email=ADMINISTRATOR, action=f"submit the individual draft {rec_id} for review"):
        current_requests_service.create(
            g.identity,
            {},
            PublishDraftRequestType.type_id,
            receiver=None,
            topic=draft_record,
        )

    _heading(f"Publish draft request declined by {INDIVIDUAL_SUBMITTER}")
    request_id = submit_publish_draft_request(
        draft_id=rec_id,
        creator_email=INDIVIDUAL_SUBMITTER,
        # self-review makes the submitter the receiver of their own request
        expected_recipients=[INDIVIDUAL_SUBMITTER],
    )
    _check_no_access_to_request(request_id=request_id)
    add_comment_check_emails(
        email=INDIVIDUAL_SUBMITTER,
        request_id=request_id,
        comment_text="This is ready to be published.",
        # the submitter is the only participant on the request and a comment never reaches
        # its author, so there is nobody left to notify
        expected_recipients=[],
    )
    decline_request_check_emails(
        actor=INDIVIDUAL_SUBMITTER,
        request_id=request_id,
        # the decision is notified to the creator of the request, ie. to the submitter, even
        # though they are the one who decided
        expected_recipients=[INDIVIDUAL_SUBMITTER],
    )

    # the declined request left the draft in "revision_requested", so the submitter can
    # answer the review by submitting the same draft again
    _heading(f"Publish draft request accepted by {INDIVIDUAL_SUBMITTER}")
    request_id = submit_publish_draft_request(
        draft_id=rec_id,
        creator_email=INDIVIDUAL_SUBMITTER,
        expected_recipients=[INDIVIDUAL_SUBMITTER],
    )
    _check_no_access_to_request(request_id=request_id)
    accept_request_check_emails(
        actor=INDIVIDUAL_SUBMITTER,
        request_id=request_id,
        expected_recipients=[INDIVIDUAL_SUBMITTER],
    )
    return rec_id


def test_change_metadata_individual(approved_record_id: str) -> None:
    """Test the notifications sent when the submitter changes metadata of an individual record.

    The mirror image of `test_change_metadata` outside of any community: the submitter, as
    the owner of the record published by `test_record_individual`, edits it, changes its
    title and submits the changed metadata for review on a ``publish_changed_metadata``
    request created without a receiver, which the individual workflow picks as its only
    reviewer, ie. the submitter themselves.

    The individual workflow configures the changed-metadata request the very same way as the
    publish-draft one, so the administrator is refused every action on it too and the
    notifications go to the same addressees: the submission to the submitter as the receiver
    of the request, a comment of theirs to nobody and the decision back to them as its
    creator.

    Like in `test_change_metadata`, the changed metadata are run through both outcomes -
    a decline closes the request but leaves the draft for the next one, while an acceptance
    publishes the draft, so the acceptance needs a freshly changed draft.
    """
    change_record_title(
        record_id=approved_record_id,
        editor_email=INDIVIDUAL_SUBMITTER,
        new_title="Changed individual title",
    )
    _ok(f"submitter {INDIVIDUAL_SUBMITTER!r} changed the title of individual record {approved_record_id}")

    _heading(f"Individual changed metadata declined by {INDIVIDUAL_SUBMITTER}")
    request_id = submit_changed_metadata_request(
        record_id=approved_record_id,
        creator_email=INDIVIDUAL_SUBMITTER,
        expected_recipients=[INDIVIDUAL_SUBMITTER],
    )
    _check_no_access_to_request(request_id=request_id)
    add_comment_check_emails(
        email=INDIVIDUAL_SUBMITTER,
        request_id=request_id,
        comment_text="These changes are ready to be published.",
        expected_recipients=[],
    )
    decline_request_check_emails(
        actor=INDIVIDUAL_SUBMITTER,
        request_id=request_id,
        expected_recipients=[INDIVIDUAL_SUBMITTER],
    )

    # the acceptance publishes the changed metadata, so it needs its own changed draft
    _heading(f"Individual changed metadata accepted by {INDIVIDUAL_SUBMITTER}")
    change_record_title(
        record_id=approved_record_id,
        editor_email=INDIVIDUAL_SUBMITTER,
        new_title="Changed individual title, again",
    )
    request_id = submit_changed_metadata_request(
        record_id=approved_record_id,
        creator_email=INDIVIDUAL_SUBMITTER,
        expected_recipients=[INDIVIDUAL_SUBMITTER],
    )
    _check_no_access_to_request(request_id=request_id)
    accept_request_check_emails(
        actor=INDIVIDUAL_SUBMITTER,
        request_id=request_id,
        expected_recipients=[INDIVIDUAL_SUBMITTER],
    )


def test_new_version_individual(approved_record_id: str) -> None:
    """Test the notifications sent when the submitter publishes a new version of an individual record.

    The mirror image of `test_new_version` outside of any community: the submitter, as the owner of
    the record published by `test_record_individual`, creates a new version of it, uploads a new file
    to the new version draft and submits it for review on a ``publish_new_version`` request created
    without a receiver, which the individual workflow picks as its only reviewer, ie. the submitter
    themselves.

    The individual workflow configures the new-version request the very same way as the publish-draft
    and changed-metadata ones, so the administrator is refused every action on it too and the
    notifications go to the same addressees: the submission to the submitter as the receiver of the
    request, a comment of theirs to nobody and the decision back to them as its creator. As the
    submitter is the only actor on the request, each of its outcomes is checked once only, unlike the
    two curators' rounds of the community record.

    The declined request leaves the new version draft in the "revision_requested" state rather than
    discarding it, so the acceptance is submitted over the very same draft, the way a submitter would
    answer the review. The version string of the second request has to differ from the first one that
    the declined request left on the draft, a request reusing a version already taken being rejected
    with ``VersionAlreadyExists``.
    """
    # as the record's owner, create a new version of it and upload a new file
    draft_id = create_new_version_with_file(
        record_id=approved_record_id,
        submitter_email=INDIVIDUAL_SUBMITTER,
        file_key="sample-individual-new.txt",
    )

    _heading(f"Individual new version declined by {INDIVIDUAL_SUBMITTER}")
    request_id = submit_new_version_request(
        draft_id=draft_id,
        creator_email=INDIVIDUAL_SUBMITTER,
        version="2.0.1",
        # self-review makes the submitter the receiver of their own request
        expected_recipients=[INDIVIDUAL_SUBMITTER],
    )
    _check_no_access_to_request(request_id=request_id)
    add_comment_check_emails(
        email=INDIVIDUAL_SUBMITTER,
        request_id=request_id,
        comment_text="This new version is ready to be published.",
        # the submitter is the only participant on the request and a comment never reaches
        # its author, so there is nobody left to notify
        expected_recipients=[],
    )
    decline_request_check_emails(
        actor=INDIVIDUAL_SUBMITTER,
        request_id=request_id,
        # the decision is notified to the creator of the request, ie. to the submitter, even
        # though they are the one who decided
        expected_recipients=[INDIVIDUAL_SUBMITTER],
    )

    # the declined request left the new version draft in "revision_requested", so the submitter
    # answers the review by submitting the same draft for review again
    _heading(f"Individual new version accepted by {INDIVIDUAL_SUBMITTER}")
    request_id = submit_new_version_request(
        draft_id=draft_id,
        creator_email=INDIVIDUAL_SUBMITTER,
        version="2.0.2",
        expected_recipients=[INDIVIDUAL_SUBMITTER],
    )
    _check_no_access_to_request(request_id=request_id)
    accept_request_check_emails(
        actor=INDIVIDUAL_SUBMITTER,
        request_id=request_id,
        expected_recipients=[INDIVIDUAL_SUBMITTER],
    )


# running ...
print("# Request notification checks")

_heading("Prepare the environment", level=2)
prepare_environment()

_heading("Membership requests", level=2)
test_membership_request()

_heading("Invitations to the community", level=2)
test_invitation_to_community()

_heading("Record review requests", level=2)
approved_record_ids = test_record_requests()

_heading("Changed metadata requests", level=2)
test_change_metadata(approved_record_ids[0])

_heading("New version requests", level=2)
test_new_version(approved_record_ids[0])

_heading("Publish draft requests outside a community", level=2)
individual_record_id = test_record_individual()

_heading("Changed metadata of a record outside a community", level=2)
test_change_metadata_individual(individual_record_id)

_heading("New version of a record outside a community", level=2)
test_new_version_individual(individual_record_id)
