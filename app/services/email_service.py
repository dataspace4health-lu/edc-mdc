from typing import Annotated, List, Dict
from fastapi import Depends
import os
import smtplib
from email.message import EmailMessage
from enum import Enum
from fastapi import Depends
from string import Template
from dataclasses import dataclass
from services.user import UserService
from services.config import ConfigService, get_config_service
from repositories.organisation import OrganisationRepository
from repositories.role import RoleRepository
from repositories.user_assignment import UserAssignmentRepository
from models.user import User
from models.dataset import Dataset


@dataclass
class EmailRecipient:
    name: str
    email: str


class EmailService:
    def __init__(
        self,
        user_service: Annotated[UserService, Depends(UserService)],
        config_service: Annotated[ConfigService, Depends(get_config_service)],
        organisation_repository: OrganisationRepository = Depends(
            OrganisationRepository
        ),
        role_repository: RoleRepository = Depends(RoleRepository),
        user_assignment_repository: UserAssignmentRepository = Depends(
            UserAssignmentRepository
        ),
    ):
        self.smtp_server = os.getenv("SMTP_SERVER")
        self.smtp_port = int(os.getenv("SMTP_PORT", "587"))
        self.smtp_username = os.getenv("SMTP_USERNAME")
        self.smtp_password = os.getenv("SMTP_PASSWORD")
        self.sender_email = os.getenv("SENDER_EMAIL")
        self.base_url = os.getenv("APP_URL", "http://localhost:5173")
        self._user_service = user_service
        self._config_service = config_service
        self._organisation_repository = organisation_repository
        self._role_repository = role_repository
        self._user_assignment_repository = user_assignment_repository

    def _get_app_url(self) -> str:
        return os.getenv("APP_URL", "Not available")

    def _get_template(self, template_key):
        templates = self._config_service.get_email_templates()
        template_data = templates.get(template_key, {})
        return {
            "subject": Template(template_data.get("subject", "")),
            "body": Template(template_data.get("body", "")),
        }

    def _get_roles_with_permission(self, permission: str) -> List[str]:
        all_roles = self._config_service.get_roles()
        disable_email_for_roles = self._config_service.get_roles_with_disable_email()
        all_roles = [
            role for role in all_roles if role["name"] not in disable_email_for_roles
        ]
        return [role["name"] for role in all_roles if permission in role["permissions"]]

    def _get_users_by_iam_role(self, role: str) -> List[User]:
        return self._user_service.find_by_iam_role(role)

    def _create_dataset_link(self, dataset_id: int) -> str:
        return f"{self.base_url}/?datasetId={dataset_id}"

    def _send_emails(
        self,
        recipients: List[EmailRecipient],
        template_key: str,
        **template_params,
    ):
        if not recipients:
            return

        unique_recipients = {r.email: r for r in recipients}.values()
        template = self._get_template(template_key)
        subject_template = template["subject"]
        body_template = template["body"]

        for r in unique_recipients:
            msg = EmailMessage()
            template_params["recipient_name"] = r.name
            msg.set_content(body_template.substitute(**template_params))
            msg["Subject"] = subject_template.substitute(**template_params)
            msg["From"] = self.sender_email
            msg["To"] = r.email

            try:
                with smtplib.SMTP(self.smtp_server, self.smtp_port) as server:
                    # Try STARTTLS on all connections for security
                    # Fall back gracefully if server doesn't support it
                    try:
                        server.starttls()
                    except (smtplib.SMTPNotSupportedError, RuntimeError):
                        # SMTPNotSupportedError: Server doesn't support STARTTLS
                        # RuntimeError: STARTTLS already negotiated or not available
                        pass
                    if self.smtp_username and self.smtp_password:
                        server.login(self.smtp_username, self.smtp_password)
                    server.send_message(msg)
            except Exception as e:
                print("exception", e)
                print(f"Failed to send email to {r.email}: {str(e)}")

    def notify_dataset_completed(self, dataset: Dataset):
        permission_needed = "datasets:status-change:validate:group"
        another_permission_needed = "datasets:status-change:validate"

        if self._config_service.get_enable_multi_tenants():
            valid_users = self._get_users_for_completion_validation_and_approval(
                dataset, another_permission_needed
            )
        else:
            roles = self._get_roles_with_permission(permission_needed)

            if not roles:
                return

            group_manager_ids = {gm.user_id for gm in dataset.group_managers}
            valid_users = [
                user
                for role in roles
                for user in self._get_users_by_iam_role(role)
                if user.id in group_manager_ids
            ]

            another_roles = self._get_roles_with_permission(another_permission_needed)

            if another_roles:
                valid_users += [
                    user
                    for role in another_roles
                    for user in self._get_users_by_iam_role(role)
                ]

        if not valid_users:
            return

        recipients = [EmailRecipient(u.name, u.email) for u in valid_users]
        dataset_link = self._create_dataset_link(dataset.id)
        self._send_emails(
            recipients,
            "DATASET_COMPLETED",
            dataset_title=dataset.title,
            dataset_link=dataset_link,
        )

    def notify_dataset_validated(self, dataset: Dataset):
        permission_needed = "datasets:status-change:approve"

        if self._config_service.get_enable_multi_tenants():
            users = self._get_users_for_completion_validation_and_approval(
                dataset, permission_needed
            )
        else:
            roles = self._get_roles_with_permission(permission_needed)

            if not roles:
                return

            users = [
                user for role in roles for user in self._get_users_by_iam_role(role)
            ]
            users = [user for user in users if user.id != dataset.user_id]

            if not users:
                return

        recipients = [EmailRecipient(u.name, u.email) for u in users]
        dataset_link = self._create_dataset_link(dataset.id)
        self._send_emails(
            recipients,
            "DATASET_VALIDATED",
            dataset_title=dataset.title,
            dataset_link=dataset_link,
        )

    def notify_dataset_approved(self, dataset: Dataset):
        # Note: Only notifies users with publish permission, not internal-only permission
        permission_needed = "datasets:status-change:publish"

        if self._config_service.get_enable_multi_tenants():
            users = self._get_users_for_completion_validation_and_approval(
                dataset, permission_needed
            )
        else:
            roles = self._get_roles_with_permission(permission_needed)

            if not roles:
                return

            users = [
                user for role in roles for user in self._get_users_by_iam_role(role)
            ]

            # Add editors (or just creator if multi-tenants disabled)
            editors = self._get_dataset_editors_or_creator(dataset)
            for editor in editors:
                if editor not in users:
                    users.append(editor)

            if not users:
                return

        recipients = [EmailRecipient(u.name, u.email) for u in users]
        dataset_link = self._create_dataset_link(dataset.id)
        self._send_emails(
            recipients,
            "DATASET_APPROVED",
            dataset_title=dataset.title,
            dataset_link=dataset_link,
        )

    def notify_dataset_back_to_draft(self, dataset: Dataset):
        editors = self._get_dataset_editors_or_creator(dataset)
        dataset_link = self._create_dataset_link(dataset.id)

        recipients = [EmailRecipient(u.name, u.email) for u in editors]
        self._send_emails(
            recipients,
            "DATASET_BACK_TO_DRAFT",
            dataset_title=dataset.title,
            dataset_link=dataset_link,
        )

    def notify_dataset_published(self, dataset: Dataset):
        recipients = (
            self._get_dataset_contacts_and_roles_manager_and_all_and_all_org_roles(
                dataset
            )
        )

        dataset_link = self._create_dataset_link(dataset.id)
        self._send_emails(
            recipients,
            "DATASET_PUBLISHED",
            dataset_title=dataset.title,
            dataset_link=dataset_link,
        )

    def notify_dataset_marked_as_internal(self, dataset: Dataset):
        editors = self._get_dataset_editors_or_creator(dataset)
        dataset_link = self._create_dataset_link(dataset.id)

        recipients = [EmailRecipient(u.name, u.email) for u in editors]
        self._send_emails(
            recipients,
            "DATASET_MARKED_AS_INTERNAL",
            dataset_title=dataset.title,
            dataset_link=dataset_link,
        )

    def notify_dataset_deprecated(self, dataset: Dataset):
        editors = self._get_dataset_editors_or_creator(dataset)
        dataset_link = self._create_dataset_link(dataset.id)

        recipients = [EmailRecipient(u.name, u.email) for u in editors]
        self._send_emails(
            recipients,
            "DATASET_DEPRECATED",
            dataset_title=dataset.title,
            dataset_link=dataset_link,
        )

    def notify_role_assigned(
        self,
        target_user_id: int,
        organisation_id: int,
        role_id: int,
        assigner_user_id: int,
    ):
        target_user = self._user_service.find_by_id(target_user_id)
        if not target_user:
            return

        users = [target_user]
        manage_roles_users = self._get_manage_roles_users()
        users.extend(manage_roles_users)

        roles_manage_organisation_users = (
            self._get_users_with_permission_in_organisation(
                "roles:manage:organisation", organisation_id
            )
        )
        users.extend(roles_manage_organisation_users)

        assigner_user = self._user_service.find_by_id(assigner_user_id)
        if not assigner_user:
            return

        users = [user for user in users if user.id != assigner_user_id]

        organisation_name = self._get_organisation_name(organisation_id)
        role_name = self._get_role_name(role_id)

        self._send_emails(
            users,
            "ROLE_ASSIGNED",
            target_user_name=target_user.name,
            target_user_email=target_user.email,
            role_name=role_name,
            organisation_name=organisation_name,
            assigner_name=assigner_user.name,
            app_url=self._get_app_url(),
        )

    def _get_users_with_permission_in_iam_roles(self, permission: str) -> List[User]:
        roles = self._get_roles_with_permission(permission)
        users = []
        for role in roles:
            users.extend(self._get_users_by_iam_role(role))
        return users

    def _get_users_with_permission_in_organisation(
        self, permission: str, organisation_id: int
    ) -> List[User]:
        roles = self._get_roles_with_permission(permission)
        users = self._get_users_in_organisation_with_roles(organisation_id, roles)
        return users

    def _get_organisation_name(self, organisation_id: int) -> str:
        org = self._organisation_repository.get_organisation(organisation_id)
        if org:
            return org.name

        return f"Organisation {organisation_id} not found"

    def _get_role_name(self, role_id: int) -> str:
        role = self._role_repository.get_by_id(role_id)
        if role:
            return role.name

        return f"Role {role_id} not found"

    def _get_users_in_organisation_with_roles(
        self, organisation_id: int, roles: List[str]
    ) -> List[User]:
        assignments = (
            self._user_assignment_repository.get_user_organisation_assignments_by_roles(
                organisation_id, roles
            )
        )

        users = [assignment.user for assignment in assignments]
        return users

    def _get_dataset_creator(self, dataset: Dataset) -> User:
        return self._user_service.find_by_id(dataset.user_id)

    def _is_user_member_of_organisation(
        self, user_id: int, organisation_id: int
    ) -> bool:
        assignment = self._user_assignment_repository.get_user_organisation_assignment(
            organisation_id, user_id
        )
        return assignment is not None

    def _user_has_global_manage_permission(self, user: User) -> bool:
        if not user or not user.iam_roles:
            return False

        manage_roles = self._get_roles_with_permission("roles:manage")
        user_role_names = [r.strip() for r in user.iam_roles.split(",") if r.strip()]

        return any(role in user_role_names for role in manage_roles)

    def _get_dataset_editors_or_creator(self, dataset: Dataset) -> List[User]:
        if not self._config_service.get_enable_multi_tenants():
            creator = self._get_dataset_creator(dataset)
            return [creator] if creator else []

        editors = []

        # Add users with organisation-level edit permission
        org_editors = self._get_users_with_permission_in_organisation(
            "datasets:edit:draft:organisation", dataset.publisher_id
        )
        editors.extend(org_editors)

        # Add users with global edit permission
        global_editors = self._get_users_with_permission_in_iam_roles(
            "datasets:edit:draft"
        )
        editors.extend(global_editors)

        # Include creator only if they're still in the org or have global manage permission
        creator = self._get_dataset_creator(dataset)
        if creator and creator not in editors:
            # Check if creator is still member of the organisation
            if self._is_user_member_of_organisation(creator.id, dataset.publisher_id):
                editors.append(creator)
            # Or if they have global manage permission (cross-org admin)
            elif self._user_has_global_manage_permission(creator):
                editors.append(creator)

        return editors

    def _get_dataset_contacts_and_roles_manager_and_all_and_all_org_roles(
        self, dataset: Dataset
    ) -> List[EmailRecipient]:
        recipients = []

        # 1. Add dataset contacts if they exist
        for dataset_contact in dataset.contacts:
            contact = dataset_contact.contact
            if contact:
                recipients.append(EmailRecipient(contact.name, contact.email))

        # 2. Add dataset editors (or just creator if multi-tenants disabled)
        editors = self._get_dataset_editors_or_creator(dataset)
        recipients.extend([EmailRecipient(u.name, u.email) for u in editors])

        manage_roles_users = self._get_manage_roles_users()
        recipients.extend([EmailRecipient(u.name, u.email) for u in manage_roles_users])

        # 5. Add users with "datasets:read:published" permission in the organization
        datasets_read_published_users = self._get_users_with_permission_in_organisation(
            "datasets:read:published", dataset.publisher_id
        )
        recipients.extend(
            [EmailRecipient(u.name, u.email) for u in datasets_read_published_users]
        )

        return list(recipients)

    def _get_manage_roles_users(self) -> List[User]:
        return self._get_users_with_permission_in_iam_roles("roles:manage")

    def _get_users_for_completion_validation_and_approval(
        self,
        dataset: Dataset,
        permission_needed: str,
    ) -> List[User]:
        valid_users = self._get_users_with_permission_in_organisation(
            permission_needed, dataset.publisher_id
        )

        manage_roles_users = self._get_manage_roles_users()
        valid_users.extend(manage_roles_users)

        manage_organisation_roles_users = (
            self._get_users_with_permission_in_organisation(
                "roles:manage:organisation", dataset.publisher_id
            )
        )
        valid_users.extend(manage_organisation_roles_users)

        if permission_needed != "datasets:status-change:validate":
            # Add editors (or just creator if multi-tenants disabled)
            editors = self._get_dataset_editors_or_creator(dataset)
            for editor in editors:
                if editor not in valid_users:
                    valid_users.append(editor)

        return valid_users
