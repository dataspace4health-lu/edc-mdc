import json
from datetime import datetime, UTC
from typing import Annotated, List, Dict, Union

from fastapi import Depends

from models.activity_log import ActivityLog
from models.contact import Contact
from repositories.activity_log import ActivityLogRepository
from schemas.activity_logs import ResourceActivityLog, activity_log_entity_to_resource
from schemas.organisation import OrganisationDto
from schemas.contact import ContactDto
from schemas.form_field import ApplicableLegislationFormFieldDto
from utils.organisation_diff import OrganisationDiff


class ActivityLogService:
    def __init__(
        self,
        repository: Annotated[ActivityLogRepository, Depends(ActivityLogRepository)],
    ):
        self._repository = repository

    def _to_plain_dict(self, value):
        if value is None:
            return {}
        if isinstance(value, dict):
            return value
        if hasattr(value, "model_dump"):
            return value.model_dump()
        if hasattr(value, "dict"):
            return value.dict()
        return {"value": str(value)}

    def log_organisation_activities(
        self,
        user_id: int,
        organisation_id: int,
        organisation_data: dict,
        updated_organisation_data: Union[OrganisationDto, dict],
        action_type: str,
    ) -> None:
        entity_type = "organisation"
        if isinstance(updated_organisation_data, dict):
            updated_data = updated_organisation_data
        else:
            updated_data = json.loads(updated_organisation_data.model_dump_json())
        diff = OrganisationDiff.compute(organisation_data, updated_data)
        if diff and json.loads(diff):
            self._log_activity(user_id, action_type, entity_type, organisation_id, diff)

    def log_applicable_legislation_activities(
        self,
        user_id: int,
        applicable_legislation_key: str,
        applicable_legislation_data: dict,
        updated_applicable_legislation_data: Union[
            ApplicableLegislationFormFieldDto, dict
        ],
        action_type: str,
    ) -> None:
        entity_type = "applicable_legislation"
        updated_data = self._to_plain_dict(updated_applicable_legislation_data)
        changes = []

        if action_type == "create":
            for field, new_value in updated_data.items():
                changes.append(
                    {
                        "field": field,
                        "old_value": None,
                        "new_value": new_value,
                        "change_type": "created",
                    }
                )
        elif action_type == "promote_to_global":
            changes.append(
                {
                    "field": "global_promotion",
                    "old_value": None,
                    "new_value": None,
                    "change_type": "promoted_to_global",
                }
            )
        else:
            for field, old_value in applicable_legislation_data.items():
                new_value = updated_data.get(field)
                if old_value != new_value:
                    changes.append(
                        {
                            "field": field,
                            "old_value": old_value,
                            "new_value": new_value,
                            "change_type": "values_changed",
                        }
                    )

        if changes:
            self._log_activity(
                user_id,
                action_type,
                entity_type,
                applicable_legislation_key,
                json.dumps(changes),
            )

    def log_keyword_activities(
        self,
        user_id: int,
        keyword_key: str,
        keyword_data: dict,
        updated_keyword_data: dict,
        action_type: str,
    ) -> None:
        entity_type = "keyword"
        changes = []

        if action_type == "create":
            for field, new_value in updated_keyword_data.items():
                changes.append(
                    {
                        "field": field,
                        "old_value": None,
                        "new_value": new_value,
                        "change_type": "created",
                    }
                )
        elif action_type == "promote_to_global":
            changes.append(
                {
                    "field": "global_promotion",
                    "old_value": None,
                    "new_value": None,
                    "change_type": "promoted_to_global",
                }
            )
        else:
            for field, old_value in keyword_data.items():
                new_value = updated_keyword_data.get(field)
                if old_value != new_value:
                    changes.append(
                        {
                            "field": field,
                            "old_value": old_value,
                            "new_value": new_value,
                            "change_type": "values_changed",
                        }
                    )

        if changes:
            self._log_activity(
                user_id, action_type, entity_type, keyword_key, json.dumps(changes)
            )

    def log_external_keyword_import(
        self,
        user_id: int,
        keyword_key: str,
        source_instance: str,
        label: str | None = None,
    ) -> None:
        formatted_diff = [
            {
                "field": "import",
                "change_type": "external_import",
                "source_instance": source_instance,
                "label": label or keyword_key,
            }
        ]
        self._log_activity(
            user_id, "create", "keyword", keyword_key, json.dumps(formatted_diff)
        )

    def log_external_applicable_legislation_import(
        self,
        user_id: int,
        applicable_legislation_key: str,
        source_instance: str,
        label: str | None = None,
    ) -> None:
        formatted_diff = [
            {
                "field": "import",
                "change_type": "external_import",
                "source_instance": source_instance,
                "label": label or applicable_legislation_key,
            }
        ]
        self._log_activity(
            user_id,
            "create",
            "applicable_legislation",
            applicable_legislation_key,
            json.dumps(formatted_diff),
        )

    def _log_activity(
        self,
        user_id: int,
        action_type: str,
        entity_type: str,
        entity_id: Union[int, str],
        diff: str,
    ) -> None:
        log_entry = ActivityLog(
            user_id=user_id,
            action_type=action_type,
            entity_type=entity_type,
            entity_id=str(entity_id),
            changes=diff,
            timestamp=datetime.now(UTC),
        )
        self._repository.add(log_entry)
        self._repository.commit()

    def get_activity_logs_from_organisation(
        self, organisation_id: int, page: int, page_size: int
    ) -> List[ResourceActivityLog]:
        activity_logs = self._repository.get_activity_logs_from_organisation(
            organisation_id, page, page_size
        )
        return [activity_log_entity_to_resource(it) for it in activity_logs]

    def get_all_activity_logs_from_organisations(
        self, organisation_ids: List[int], page: int, page_size: int
    ) -> List[ResourceActivityLog]:
        if organisation_ids is None:
            activity_logs = self._repository.get_all_activity_logs_for_entity(
                entity_type="organisation",
                page=page,
                page_size=page_size,
            )
        elif not organisation_ids:
            activity_logs = []
        else:
            activity_logs = self._repository.get_all_activity_logs_from_organisations(
                organisation_ids,
                page,
                page_size,
            )
        return [activity_log_entity_to_resource(it) for it in activity_logs]

    def get_activity_logs_from_form_field(
        self, form_field: str, page: int, page_size: int
    ) -> List[ResourceActivityLog]:
        if form_field == "keyword":
            logs = self._repository.get_all_activity_logs_for_entity(
                "keyword", page, page_size
            )
        elif form_field == "applicable_legislation":
            logs = self._repository.get_all_activity_logs_for_entity(
                "applicable_legislation", page, page_size
            )
        else:
            logs = []

        return [activity_log_entity_to_resource(log) for log in logs]

    def get_all_activity_logs(
        self, page: int, page_size: int
    ) -> List[ResourceActivityLog]:
        all_logs = self._repository.get_all_activity_logs_for_entity(
            self.get_entity_type(), page, page_size
        )
        return [activity_log_entity_to_resource(log) for log in all_logs]
