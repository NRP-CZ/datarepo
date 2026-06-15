"""
Test for permissions. This test should be run as a part of invenio shell
"""

import contextlib
import subprocess
import sys
from io import BytesIO
from pathlib import Path

import click
from flask import current_app, g
from flask_principal import identity_loaded
from invenio_access.cli import allow_action
from invenio_access.models import ActionRoles
from invenio_access.permissions import authenticated_user, system_identity
from invenio_access.utils import get_identity
from invenio_accounts.models import Role, User
from invenio_communities.communities import CommunityService
from invenio_communities.communities.records.api import Community
from invenio_communities.communities.resources.ui_schema import UICommunitySchema
from invenio_communities.members.errors import AlreadyMemberError
from invenio_communities.proxies import current_communities
from invenio_communities.records.records.models import CommunityMetadata
from invenio_communities.views.ui import UICommunityJSONSerializer
from invenio_db import db
from invenio_rdm_records.services import RDMRecordService
from invenio_records_resources.proxies import current_service_registry
from invenio_records_resources.services.errors import PermissionDeniedError
from invenio_requests.services import RequestsService
from oarepo_requests.types import PublishDraftRequestType
from oarepo_runtime.proxies import current_runtime
from werkzeug.local import LocalProxy

_datastore = LocalProxy(lambda: current_app.extensions["security"].datastore)
datasets_service: RDMRecordService = LocalProxy(
    lambda: current_runtime.models["datasets"].service
)
requests_service: RequestsService = LocalProxy(
    lambda: current_service_registry.get("requests")
)
communities_service: CommunityService = LocalProxy(lambda: current_communities.service)


@contextlib.contextmanager
def with_logged_user(user_or_email):
    if isinstance(user_or_email, str):
        user = db.session.query(User).filter_by(email=user_or_email).first()
        if user is None:
            raise LookupError(f"User {user_or_email!r} not found in database")
    else:
        user = user_or_email

    with current_app.test_request_context():
        identity = get_identity(user)
        identity.provides.add(authenticated_user)
        identity_loaded.send(current_app._get_current_object(), identity=identity)
        g.identity = identity
        yield identity


def main():
    print("Running inside the shell")

    # in this test, we will create:
    #
    create_community("test-community-a-open", restricted=False)
    create_community("test-community-b-open", restricted=False)
    create_community("test-community-c-restricted", restricted=True)
    create_community("test-community-d-restricted", restricted=True)

    create_user("test-normal@demo.org", roles=[])

    # this user has superuser access
    create_user("test-admin@demo.org", roles=["admin"])

    create_user("test-administration@demo.org", roles=["administration"])

    create_user(
        "test-direct-publisher@demo.org", roles=["direct-publisher", "submitter"]
    )

    add_role_access("administration", "administration-access")
    add_role_access("administration", "administration-moderation")

    create_user("test-submitter@demo.org", roles=["submitter"])

    create_community_user("test-community-a-open", "member")
    create_community_user("test-community-b-open", "member")
    create_community_user("test-community-a-open", "submitter")
    create_community_user("test-community-b-open", "submitter")
    create_community_user("test-community-a-open", "curator")
    create_community_user("test-community-b-open", "curator")
    create_community_user("test-community-a-open", "owner")
    create_community_user("test-community-b-open", "owner")

    create_community_user("test-community-c-restricted", "member")
    create_community_user("test-community-d-restricted", "member")
    create_community_user("test-community-c-restricted", "submitter")
    create_community_user("test-community-d-restricted", "submitter")
    create_community_user("test-community-c-restricted", "curator")
    create_community_user("test-community-d-restricted", "curator")
    create_community_user("test-community-c-restricted", "owner")
    create_community_user("test-community-d-restricted", "owner")
    test_can_create_record(
        allowed_users=[
            "test-direct-publisher@demo.org",
            # admin can create records
            "test-admin@demo.org",
            # submitter can create records as well
            "test-submitter@demo.org",
            # community roles submitter, curator and owner can create records
            "test-community-a-open-submitter@demo.org",
            "test-community-b-open-submitter@demo.org",
            "test-community-c-restricted-submitter@demo.org",
            "test-community-d-restricted-submitter@demo.org",
            "test-community-a-open-curator@demo.org",
            "test-community-b-open-curator@demo.org",
            "test-community-c-restricted-curator@demo.org",
            "test-community-d-restricted-curator@demo.org",
            "test-community-a-open-owner@demo.org",
            "test-community-b-open-owner@demo.org",
            "test-community-c-restricted-owner@demo.org",
            "test-community-d-restricted-owner@demo.org",
        ],
        disallowed_users=[
            "test-administration@demo.org",
            # normal users cannot create records
            "test-normal@demo.org",
            # community members without submitter role or higher cannot create records
            "test-community-a-open-member@demo.org",
            "test-community-b-open-member@demo.org",
            "test-community-c-restricted-member@demo.org",
            "test-community-d-restricted-member@demo.org",
        ],
    )

    test_can_publish_directly(
        allowed_users=[
            # direct-publisher role can directly publish records
            "test-direct-publisher@demo.org",
            # superuser-access can directly publish records
            "test-admin@demo.org",
        ],
        disallowed_users=[
            # submitter can create records as well
            "test-submitter@demo.org",
            # community roles submitter, curator and owner can't directly publish records
            "test-community-a-open-submitter@demo.org",
            "test-community-b-open-submitter@demo.org",
            "test-community-c-restricted-submitter@demo.org",
            "test-community-d-restricted-submitter@demo.org",
            "test-community-a-open-curator@demo.org",
            "test-community-b-open-curator@demo.org",
            "test-community-c-restricted-curator@demo.org",
            "test-community-d-restricted-curator@demo.org",
            "test-community-a-open-owner@demo.org",
            "test-community-b-open-owner@demo.org",
            "test-community-c-restricted-owner@demo.org",
            "test-community-d-restricted-owner@demo.org",
        ],
    )
    test_can_publish_directly(
        record_owner="test-submitter@demo.org",
        allowed_users=[
            # superuser-access can directly publish records
            "test-admin@demo.org",
        ],
        disallowed_users=[
            # direct-publisher role can directly publish records
            "test-direct-publisher@demo.org",
        ],
    )
    test_publish_with_publish_draft_request(
        allowed_users=[
            # superuser-access can publish records via publish-draft request
            "test-admin@demo.org",
            # submitter can publish the record via publish-draft request as well
            "test-submitter@demo.org",
            # direct publisher role can use request as well
            "test-direct-publisher@demo.org",
        ],
        disallowed_users=[
            # community users must submit through their community
            "test-community-a-open-submitter@demo.org",
            "test-community-b-open-submitter@demo.org",
            "test-community-c-restricted-submitter@demo.org",
            "test-community-d-restricted-submitter@demo.org",
            "test-community-a-open-curator@demo.org",
            "test-community-b-open-curator@demo.org",
            "test-community-c-restricted-curator@demo.org",
            "test-community-d-restricted-curator@demo.org",
            "test-community-a-open-owner@demo.org",
            "test-community-b-open-owner@demo.org",
            "test-community-c-restricted-owner@demo.org",
            "test-community-d-restricted-owner@demo.org",
        ],
    )

    test_publish_to_community_with_review(
        community_slug="test-community-a-open",
        allowed_users=[
            # "test-community-a-open-curator@demo.org",
            # "test-community-a-open-submitter@demo.org",
            # "test-community-a-open-owner@demo.org",
            # # superuser-access can always create review requests
            # "test-admin@demo.org",
        ],
        disallowed_users=[
            # submitter can publish the record via publish-draft request as well
            "test-submitter@demo.org",
            # direct publisher role can use request as well
            "test-direct-publisher@demo.org",
            # member can not create record, so cannot create review request
            # "test-community-a-open-member@demo.org",
            # "test-community-b-open-member@demo.org",
            # "test-community-c-restricted-member@demo.org",
            # "test-community-d-restricted-member@demo.org",
            "test-community-b-open-curator@demo.org",
            "test-community-b-open-submitter@demo.org",
            "test-community-b-open-owner@demo.org",
            "test-community-c-restricted-curator@demo.org",
            "test-community-c-restricted-submitter@demo.org",
            "test-community-c-restricted-owner@demo.org",
            "test-community-d-restricted-curator@demo.org",
            "test-community-d-restricted-submitter@demo.org",
            "test-community-d-restricted-owner@demo.org",
        ],
    )


def test_publish_to_community_with_review(
    *, community_slug, allowed_users, disallowed_users
):
    failures = []
    all_users = [
        *[(x, True) for x in allowed_users],
        *[(x, False) for x in disallowed_users],
    ]
    for email, allowed in all_users:
        click.secho(
            f"Testing if user {email} can publish to community via review (allowed: {allowed})",
            fg="green",
        )
        with with_logged_user(email) as identity:
            rec_id = create_record(identity)
            draft_rec = datasets_service.read_draft(identity, rec_id, expand=True)
            if "review" not in draft_rec.to_dict()["links"]:
                if allowed:
                    click.secho(
                        f"User {email} does not have review link but should be allowed to publish to community via review (allowed: {allowed})",
                        fg="red",
                    )
                    failures.append(email)

            communities_list = communities_service.search(
                identity, params={"size": 100}
            ).to_dict()["hits"]["hits"]
            communities_list = [
                UICommunityJSONSerializer().dump_obj(community)
                for community in communities_list
            ]
            community = next(
                (c for c in communities_list if c["slug"] == community_slug), None
            )
            if not community:
                if allowed:
                    click.secho(
                        f"Community {community_slug} not found but should be allowed (allowed: {allowed})",
                        fg="red",
                    )
                    failures.append(email)
                    continue
                else:
                    click.secho(
                        f"Community {community_slug} not found and user is not allowed to publish in it (allowed: {allowed})",
                        fg="green",
                    )
                    continue
            # we have found the community, let's check if the user is allowed to publish in it
            permissions = community["ui"]["permissions"]
            if permissions["can_submit_record"]:
                if not allowed:
                    click.secho(
                        f"User {email} is allowed to publish in community {community_slug} but should not be allowed (allowed: {allowed})",
                        fg="red",
                    )
                    failures.append(email)
            else:
                if allowed:
                    click.secho(
                        f"User {email} is not allowed to publish in community {community_slug} but should be allowed (allowed: {allowed})",
                        fg="red",
                    )
                    failures.append(email)

            # let's call the review
            try:
                created_review = datasets_service.review.create(
                    identity,
                    {
                        "type": "community-submission",
                        "receiver": {"community": community["id"]},
                    },
                    draft_rec._record,
                )
                review_created = True
            except PermissionDeniedError as e:
                review_created = False
            if review_created != allowed:
                if review_created:
                    click.secho(
                        f"Review was created for user {email} but should not be allowed (allowed: {allowed})",
                        fg="red",
                    )
                    failures.append(email)
                else:
                    click.secho(
                        f"Review was not created for user {email} but should be allowed (allowed: {allowed})",
                        fg="red",
                    )
                    failures.append(email)
                continue


def test_publish_with_publish_draft_request(*, allowed_users, disallowed_users):
    failures = []
    all_users = [
        *[(x, True) for x in allowed_users],
        *[(x, False) for x in disallowed_users],
    ]
    for email, allowed in all_users:
        click.secho(
            f"Testing if user {email} can publish via publish draft request (allowed: {allowed})",
            fg="green",
        )
        with with_logged_user(email) as identity:
            rec_id = create_record(identity)
            draft_rec = datasets_service.read_draft(identity, rec_id, expand=True)
            # look at the requests in the expanded section
            expanded_section = draft_rec.to_dict()["expanded"]
            request_types = expanded_section.get("request_types", [])
            publish_draft = next(
                iter((x for x in request_types if x["type_id"] == "publish_draft")),
                None,
            )
            if publish_draft is None:
                if allowed:
                    click.secho(
                        f"User {email} cannot publish through publish draft, request type not found (allowed: {allowed})",
                        fg="red",
                    )
                    failures.append(email)
                else:
                    click.secho(
                        f"User {email} cannot publish through publish draft, that is ok (allowed: {allowed})",
                        fg="green",
                    )
                continue
            else:
                if not allowed:
                    click.secho(
                        f"User {email} can publish through publish draft but should not (allowed: {allowed})",
                        fg="red",
                    )
                    continue
            # ok, user should be able to publish through publish draft, let's try it
            try:
                created_request = requests_service.create(
                    identity,
                    {},
                    PublishDraftRequestType(),
                    receiver=None,
                    creator=None,
                    topic=draft_rec._record,
                )
                status = "allowed"
            except PermissionDeniedError as e:
                status = "denied"

            if status == "allowed":
                if not allowed:
                    click.secho(
                        f"User {email} can publish through publish draft but should not (allowed: {allowed})",
                        fg="red",
                    )
                    failures.append(email)
                else:
                    click.secho(
                        f"User {email} can publish through publish draft (allowed: {allowed})",
                        fg="green",
                    )
            else:
                if allowed:
                    click.secho(
                        f"User {email} cannot publish through publish draft but should (allowed: {allowed})",
                        fg="red",
                    )
                    failures.append(email)
                else:
                    click.secho(
                        f"User {email} cannot publish through publish draft, that is ok (allowed: {allowed})",
                        fg="green",
                    )


def test_can_publish_directly(*, record_owner=None, allowed_users, disallowed_users):
    failures = []
    all_users = [
        *[(x, True) for x in allowed_users],
        *[(x, False) for x in disallowed_users],
    ]
    for email, allowed in all_users:
        click.secho(
            f"Testing if user {email} can publish directly (allowed: {allowed})",
            fg="green",
        )
        with with_logged_user(record_owner or email) as identity:
            rec_id = create_record(identity)

        with with_logged_user(email) as identity:
            # rec = datasets_service.read_draft(identity, rec_id)._record
            # permission_policy = datasets_service.permission_policy
            # can_publish = permission_policy("publish", record=rec)
            # if not can_publish.allows(identity):
            #     raise PermissionDeniedError("publish")
            try:
                datasets_service.publish(identity, rec_id)
                status = "allowed"
            except PermissionDeniedError as e:
                status = "denied"

            expected = "allowed" if allowed else "denied"
            if status != expected:
                msg = f"FAIL: {email} → {status} (expected {expected})"
                click.secho(f"  {msg}", fg="red")
                failures.append(msg)
            else:
                click.secho(f"  OK: {status}", fg="green")
    print_failures(failures)


def test_can_create_record(allowed_users, disallowed_users):
    permission_policy = datasets_service.permission_policy
    all_users = [
        *[(x, True) for x in allowed_users],
        *[(x, False) for x in disallowed_users],
    ]
    failures = []
    for email, allowed in all_users:
        click.secho(
            f"Testing if user {email} can create a record (allowed: {allowed})",
            fg="green",
        )

        with with_logged_user(email) as identity:
            result = permission_policy("create").allows(identity)

        status = "ALLOWED" if result else "DENIED"
        expected = "allowed" if allowed else "denied"
        if result != allowed:
            msg = f"FAIL: {email} → {status} (expected {expected})"
            click.secho(f"  {msg}", fg="red")
            failures.append(msg)
        else:
            click.secho(f"  OK: {status}", fg="green")
    print_failures(failures)


def print_failures(failures):
    click.secho("")
    if failures:
        click.secho(f"{len(failures)} failure(s):", fg="red")
        for msg in failures:
            click.secho(f"  {msg}", fg="red")
    else:
        click.secho("All checks passed.", fg="green")


def create_record(identity):
    sample_record_data = {
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
    response = datasets_service.create(identity, sample_record_data).to_dict()
    assert response.get("errors") is None
    rec_id = response["id"]
    # upload a sample file
    datasets_service.draft_files.init_files(identity, rec_id, [{"key": "sample.txt"}])
    datasets_service.draft_files.set_file_content(
        identity, rec_id, "sample.txt", BytesIO(b"hello")
    )
    datasets_service.draft_files.commit_file(identity, rec_id, "sample.txt")
    return rec_id


def create_community(slug, restricted):
    click.secho(f"Creating community {slug}", fg="green")
    md = db.session.query(CommunityMetadata).filter_by(slug=slug).first()
    if md is not None:
        return

    resp = communities_service.create(
        system_identity,
        {
            "slug": slug,
            "metadata": {
                "title": slug,
            },
            "access": {"visibility": "restricted" if restricted else "public"},
            "custom_fields": {
                "allowed_workflows": ["community"],
                "workflow": "community",
            },
        },
    ).to_dict()
    assert not resp.get("errors")


def create_user(email: str, roles: list[str]) -> User:
    click.secho(f"Creating user {email} with roles {roles}", fg="green")
    user = db.session.query(User).filter_by(email=email).first()
    if user is None:
        user = _datastore.create_user(email=email, active=True)
    else:
        user = user
    db.session.add(user)
    db.session.commit()

    for role in roles:
        r = db.session.query(Role).filter_by(name=role).first()
        if r is None:
            r = _datastore.create_role(id=role, name=role)
        _datastore.add_role_to_user(user, r)
    return user


def create_community_user(community_slug, role):
    email = f"{community_slug}-{role}@demo.org"
    click.secho(f"Creating community user {email}", fg="green")
    user = create_user(email, [])

    community_id = Community.pid.resolve(community_slug).id
    if community_id is None:
        raise click.ClickException(f"Community with slug {community_slug} not found")

    user_id = str(user.id)

    with contextlib.suppress(AlreadyMemberError):
        communities_service.members.add(
            system_identity,
            str(community_id),
            {
                "members": [
                    {
                        "type": "user",
                        "id": user_id,
                    }
                ],
                "role": role,
            },
        )


def add_role_access(role_name, access_name):
    role = Role.query.filter_by(name=role_name).first()
    existing_action = ActionRoles.query.filter_by(
        action=access_name, role_id=role.id
    ).first()
    if existing_action is None:
        db.session.add(ActionRoles.allow(access_name, argument=None, role_id=role.id))
    db.session.commit()


if __name__ == "__main__":
    main()
