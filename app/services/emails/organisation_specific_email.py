from typing import List, Optional
from fastapi import Depends
from services.email_service import EmailService, EmailRecipient
from models.dataset import Dataset


class OrganisationSpecificEmailsService(EmailService):

    def notify_keyword_promoted_to_global(
        self, old_organisation_id: int, keyword_name: str, promoter: int
    ):
        users = self._get_users_with_permission_in_organisation(
            "form-fields:edit:organisation", old_organisation_id
        )
        users_with_edit_my = self._get_users_with_permission_in_organisation(
            "form-fields:edit:my", old_organisation_id
        )

        users.extend(users_with_edit_my)

        manage_roles_users = self._get_manage_roles_users()
        users.extend(manage_roles_users)

        unique_users = {user.id: user for user in users}

        recipients = [
            EmailRecipient(user.name, user.email) for user in unique_users.values()
        ]

        promoter_user = next(
            (u for u in unique_users.values() if u.id == promoter), None
        )

        self._send_emails(
            recipients,
            "KEYWORD_PROMOTED_TO_GLOBAL",
            keyword_name=keyword_name,
            promoter_name=promoter_user.name,
        )
