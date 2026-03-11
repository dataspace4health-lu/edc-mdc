from typing import Optional, Set

from services.form_fields_service import FormFieldsService
from models.identity_context import IdentityContext
from models.applicable_legislation import ApplicableLegislation
from schemas.form_field import (
    CreateFormFieldDto,
    CreateApplicableLegislationFormFieldDto,
)


class FormFieldsImportService(FormFieldsService):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self._suppress_create_logging = False

    def ensure_keyword_exists(
        self,
        keyword_value: str,
        organisation_id: Optional[int] = None,
        created_by_id: Optional[int] = None,
        source_instance: Optional[str] = None,
    ) -> str:
        dto = CreateFormFieldDto(
            eng_label=keyword_value,
            organisation_ids=[organisation_id] if organisation_id else [],
        )
        identity = IdentityContext(
            user_id=created_by_id, permissions=[], current_organisation_id=None
        )

        if source_instance:
            self._suppress_create_logging = True

        result = self.create("keyword", dto, identity)

        self._suppress_create_logging = False

        if source_instance and created_by_id:
            self._activity_log_service.log_external_keyword_import(
                user_id=created_by_id,
                keyword_key=result.key,
                source_instance=source_instance,
                label=keyword_value,
            )

        return result.key

    def ensure_applicable_legislation_exists(
        self,
        applicable_legislation_key: str,
        organisation_id: Optional[int] = None,
        created_by_id: Optional[int] = None,
        title: Optional[str] = None,
        link: Optional[str] = None,
        source_instance: Optional[str] = None,
    ) -> str:
        applicable_legislation = (
            self._applicable_legislation_repository.get_by_key_or_link(
                applicable_legislation_key, link
            )
        )

        if applicable_legislation:
            if organisation_id:
                assignments = self._applicable_legislation_assignment_repository.get_applicable_legislation_organisation_assignments(
                    applicable_legislation.key
                )
                if assignments and not self._has_assignment(
                    "applicable_legislation",
                    applicable_legislation.key,
                    organisation_id,
                    self._applicable_legislation_assignment_repository,
                ):
                    self._create_assignments(
                        "applicable_legislation",
                        applicable_legislation.key,
                        [organisation_id],
                        self._applicable_legislation_assignment_repository,
                    )
            return applicable_legislation.key

        new_applicable_legislation = ApplicableLegislation(
            key=applicable_legislation_key,
            eng_label=title or applicable_legislation_key,
            description=None,
            link=link or applicable_legislation_key,
            created_by_id=created_by_id,
        )
        self._applicable_legislation_repository.add(new_applicable_legislation)
        self._applicable_legislation_repository.commit()

        if organisation_id:
            self._create_assignments(
                "applicable_legislation",
                applicable_legislation_key,
                [organisation_id],
                self._applicable_legislation_assignment_repository,
            )

        dto = CreateApplicableLegislationFormFieldDto(
            eng_label=title or applicable_legislation_key,
            description=None,
            link=link or applicable_legislation_key,
            organisation_ids=[organisation_id] if organisation_id else [],
        )

        if source_instance and created_by_id:
            self._activity_log_service.log_external_applicable_legislation_import(
                user_id=created_by_id,
                applicable_legislation_key=applicable_legislation_key,
                source_instance=source_instance,
                label=title or applicable_legislation_key,
            )
        else:
            self._log_activity(
                "applicable_legislation", applicable_legislation_key, dto, created_by_id
            )

        return applicable_legislation_key

    def ensure_keywords_exist(
        self,
        keyword_values: Set[str],
        organisation_id: Optional[int] = None,
        created_by_id: Optional[int] = None,
        source_instance: Optional[str] = None,
    ) -> Set[str]:
        if not keyword_values:
            return set()

        result_keys = set()
        for keyword_value in keyword_values:
            keyword_key = self.ensure_keyword_exists(
                keyword_value, organisation_id, created_by_id, source_instance
            )
            result_keys.add(keyword_key)
        return result_keys

    def ensure_applicable_legislations_exist(
        self,
        applicable_legislation_keys: Set[str],
        organisation_id: Optional[int] = None,
        created_by_id: Optional[int] = None,
        source_instance: Optional[str] = None,
    ) -> Set[str]:
        if not applicable_legislation_keys:
            return set()

        result_keys = set()
        for applicable_legislation_key in applicable_legislation_keys:
            key = self.ensure_applicable_legislation_exists(
                applicable_legislation_key=applicable_legislation_key,
                organisation_id=organisation_id,
                created_by_id=created_by_id,
                title=None,
                link=applicable_legislation_key,
                source_instance=source_instance,
            )
            result_keys.add(key)
        return result_keys

    def ensure_applicable_legislations_with_titles_exist(
        self,
        applicable_legislation_data: dict[str, str],
        organisation_id: Optional[int] = None,
        created_by_id: Optional[int] = None,
        source_instance: Optional[str] = None,
    ) -> Set[str]:
        if not applicable_legislation_data:
            return set()

        result_keys = set()
        for link, title in applicable_legislation_data.items():
            key = self.ensure_applicable_legislation_exists(
                applicable_legislation_key=link,
                organisation_id=organisation_id,
                created_by_id=created_by_id,
                title=title,
                link=link,
                source_instance=source_instance,
            )
            result_keys.add(key)
        return result_keys

    # Import-specific behaviour overrides
    def _enforce_permissions_during_create(self) -> bool:
        """Imports run under a service account; skip UI permission checks."""
        return False

    def _lookup_existing_by_label(self) -> bool:
        """RDF payloads only contain keyword labels, so allow label lookups."""
        return True

    def _error_on_global_conflict(self) -> bool:
        """If a field already exists globally we just reuse it."""
        return False

    def _error_on_assignment_conflict(self) -> bool:
        """Re-importing may hit existing assignments; treat that as success."""
        return False

    def _should_log_create(self) -> bool:
        """Suppress standard logging when importing from external sources."""
        return not self._suppress_create_logging
