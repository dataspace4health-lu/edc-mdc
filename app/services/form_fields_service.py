from fastapi import Depends, HTTPException
from services.form_fields_permission import FormFieldsPermissionsService
from repositories.keyword import KeywordRepository
from repositories.dataset import DatasetRepository
from repositories.applicable_legislation import ApplicableLegislationRepository
from repositories.distribution import DistributionRepository
from repositories.organisation import OrganisationRepository
from schemas.form_field import (
    CreateFormFieldDto,
    FormFieldDto,
    ResourceFormField,
    CreateApplicableLegislationFormFieldDto,
    ApplicableLegislationFormFieldDto,
    ApplicableLegislationFormField,
    PaginatedFormFieldResponse,
    PaginationMeta,
)
from typing import List, Union, Any, Optional, Tuple
from models.dataset import Keyword
from models.applicable_legislation import ApplicableLegislation
from models.keyword_assignment import KeywordAssignment
from models.applicable_legislation_assignment import ApplicableLegislationAssignment
from models.identity_context import IdentityContext
from services.activity_log import ActivityLogService
from sqlalchemy import exc
from services.emails.organisation_specific_email import (
    OrganisationSpecificEmailsService,
)
from repositories.keyword_assignment import KeywordAssignmentRepository
from repositories.applicable_legislation_assignment import (
    ApplicableLegislationAssignmentRepository,
)
from utils.key_generator import KeyGenerator


class FormFieldsService:
    def __init__(
        self,
        keyword_repository: KeywordRepository = Depends(KeywordRepository),
        keyword_assignment_repository: KeywordAssignmentRepository = Depends(
            KeywordAssignmentRepository
        ),
        dataset_repository: DatasetRepository = Depends(DatasetRepository),
        applicable_legislation_repository: ApplicableLegislationRepository = Depends(
            ApplicableLegislationRepository
        ),
        applicable_legislation_assignment_repository: ApplicableLegislationAssignmentRepository = Depends(
            ApplicableLegislationAssignmentRepository
        ),
        distribution_repository: DistributionRepository = Depends(
            DistributionRepository
        ),
        form_fields_permissions_service: FormFieldsPermissionsService = Depends(
            FormFieldsPermissionsService
        ),
        activity_log_service: ActivityLogService = Depends(ActivityLogService),
        organisation_repository: OrganisationRepository = Depends(
            OrganisationRepository
        ),
        email_service: OrganisationSpecificEmailsService = Depends(
            OrganisationSpecificEmailsService
        ),
    ):
        self._repositories = {
            "keyword": keyword_repository,
            "applicable_legislation": applicable_legislation_repository,
        }

        self._assignment_repositories = {
            "keyword": keyword_assignment_repository,
            "applicable_legislation": applicable_legislation_assignment_repository,
        }

        self._dataset_repository = dataset_repository
        self._distribution_repository = distribution_repository
        self._form_fields_permissions_service = form_fields_permissions_service
        self._activity_log_service = activity_log_service
        self._organisation_repository = organisation_repository
        self._email_service = email_service

        self._keyword_repository = keyword_repository
        self._keyword_assignment_repository = keyword_assignment_repository
        self._applicable_legislation_repository = applicable_legislation_repository
        self._applicable_legislation_assignment_repository = (
            applicable_legislation_assignment_repository
        )

    def get_all(self, field_type: str, identity: IdentityContext) -> Union[
        List[ResourceFormField],
        List[ApplicableLegislationFormField],
    ]:
        repository = self._get_repository(field_type)
        org_ids = self._form_fields_permissions_service.get_user_organisation_ids(
            identity
        )
        fields = repository.get_all(org_ids)
        return [self._format_response(field_type, field) for field in fields]

    def get_all_paginated(
        self,
        field_type: str,
        page: int = 1,
        page_size: int = 10,
        query: Optional[str] = None,
        organisation_filters: Optional[List[str]] = None,
        identity: IdentityContext = None,
    ) -> PaginatedFormFieldResponse:

        org_ids = self._form_fields_permissions_service.get_user_organisation_ids(
            identity
        )

        repository = self._get_repository(field_type)
        fields, total_count = repository.get_all_paginated(
            page=page,
            page_size=page_size,
            query=query,
            user_org_ids=org_ids,
            organisation_filters=organisation_filters,
        )

        # Format the response
        formatted_fields = [
            self._format_response(field_type, field) for field in fields
        ]

        # Calculate total pages
        total_pages = (total_count + page_size - 1) // page_size

        return PaginatedFormFieldResponse(
            items=formatted_fields,
            meta=PaginationMeta(
                total_items=total_count,
                page=page,
                page_size=page_size,
                total_pages=total_pages,
            ),
        )

    def create(
        self,
        field_type: str,
        dto: Union[
            CreateFormFieldDto,
            CreateApplicableLegislationFormFieldDto,
        ],
        identity: IdentityContext,
    ) -> Union[ResourceFormField, ApplicableLegislationFormField]:
        user_id = identity.user_id
        # For applicable legislation, include link in key generation to ensure uniqueness
        if field_type == "applicable_legislation":
            link = getattr(dto, "link", "")
            generated_key = KeyGenerator.generate_key_from_label_and_link(
                dto.eng_label, link
            )
        else:
            generated_key = KeyGenerator.generate_key_from_label(dto.eng_label)
        try:
            selected_org_ids = self._extract_org_ids(dto)
            if self._enforce_permissions_during_create():
                self._validate_creation_permissions(
                    field_type, selected_org_ids, identity
                )
            if field_type in ["keyword", "applicable_legislation"]:
                form_field, was_existing = self._handle_assignable_field(
                    field_type,
                    generated_key,
                    dto,
                    identity,
                    selected_org_ids,
                )
                if was_existing:
                    # Log as update since we're adding to existing field
                    repository = self._get_repository(field_type)
                    original_data = form_field.to_dict_for_diff()

                    # Create a DTO with existing values (preserve label, description, etc.)
                    if field_type == "applicable_legislation":
                        from schemas.form_field import ApplicableLegislationFormFieldDto

                        update_dto = ApplicableLegislationFormFieldDto(
                            key=form_field.key,
                            eng_label=form_field.eng_label,
                            description=form_field.description,
                            link=form_field.link,
                            organisation_ids=selected_org_ids,
                        )
                    else:  # keyword
                        from schemas.form_field import FormFieldDto

                        update_dto = FormFieldDto(
                            key=form_field.key,
                            eng_label=form_field.eng_label,
                            organisation_ids=selected_org_ids,
                        )

                    self._update_field_properties(
                        field_type, repository, update_dto, user_id, original_data
                    )
                else:
                    if self._should_log_create():
                        self._log_activity(field_type, generated_key, dto, user_id)
            else:
                raise ValueError(f"Unsupported field type: {field_type}")
            return self._format_response(field_type, form_field)
        except exc.IntegrityError:
            raise HTTPException(
                status_code=400,
                detail=f"Form Field with key {generated_key} already exists",
            )
        except Exception as e:
            raise HTTPException(status_code=400, detail=str(e))

    def _enforce_permissions_during_create(self) -> bool:
        return True

    def _lookup_existing_by_label(self) -> bool:
        return False

    def _error_on_global_conflict(self) -> bool:
        return True

    def _error_on_assignment_conflict(self) -> bool:
        return True

    def _should_log_create(self) -> bool:
        return True

    def update(
        self,
        field_type: str,
        dto: Union[FormFieldDto, ApplicableLegislationFormFieldDto],
        identity: IdentityContext,
    ) -> Union[ResourceFormField, ApplicableLegislationFormField]:
        user_id = identity.user_id
        user_org_id = identity.current_organisation_id
        self._form_fields_permissions_service.validate_edit_and_delete_permissions(
            field_type, dto.key, user_org_id, identity
        )
        repository = self._get_repository(field_type)

        original = repository.get(dto.key)
        if not original:
            raise HTTPException(
                status_code=404, detail=f"Form Field with key {dto.key} not found"
            )

        original_data = original.to_dict_for_diff()

        if field_type in ["keyword", "applicable_legislation"]:
            self._handle_update_assignments(field_type, dto, identity)

        form_field = self._update_field_properties(
            field_type, repository, dto, user_id, original_data
        )

        repository.commit()
        return self._format_response(field_type, form_field)

    def delete(self, field_type: str, key: str, identity: IdentityContext):
        user_id = identity.user_id
        user_org_id = identity.current_organisation_id

        repository = self._get_repository(field_type)
        form_field = repository.get(key)
        if form_field is None:
            raise HTTPException(status_code=404, detail=f"form_field[{key}] not found.")

        self._form_fields_permissions_service.validate_edit_and_delete_permissions(
            field_type, key, user_org_id, identity
        )

        self._check_field_dependencies(field_type, key)

        original_data = form_field.to_dict_for_diff()
        self._log_deletion_activity(field_type, key, user_id, original_data)

        repository.delete(form_field)

    def _extract_org_ids(self, dto) -> List[int]:
        selected_org_ids = getattr(dto, "organisation_ids", None)
        if selected_org_ids is None and hasattr(dto, "__dict__"):
            selected_org_ids = dto.__dict__.get("organisation_ids")
        return list(selected_org_ids or [])

    def _validate_creation_permissions(
        self, field_type: str, selected_org_ids: List[int], identity: IdentityContext
    ):
        if not selected_org_ids:
            if not self._form_fields_permissions_service.can_create_global_fields(
                identity
            ):
                raise HTTPException(
                    status_code=403,
                    detail="Only Catalogue Managers can create global form fields. Please select at least one organization.",
                )
        else:
            self._form_fields_permissions_service.validate_create_permissions(
                field_type, selected_org_ids, identity
            )

    def _handle_assignable_field(
        self,
        field_type: str,
        key: str,
        dto,
        identity: IdentityContext,
        selected_org_ids: List[int],
    ):
        repository, assignment_repo = self._get_repositories(field_type)

        # For applicable legislation, check by key OR link
        if field_type == "applicable_legislation":
            existing_field = repository.get_by_key_or_link(key, dto.link)
        else:
            existing_field = repository.get(key)
            if not existing_field and self._lookup_existing_by_label():
                existing_field = repository.get_by_eng_label(dto.eng_label)
                if existing_field:
                    key = existing_field.key

        if existing_field:
            self._validate_and_assign_to_existing(
                field_type,
                existing_field,
                selected_org_ids,
                assignment_repo,
                identity,
            )
            return existing_field, True  # was_existing = True

        form_field = self._create_field(field_type, key, dto, identity)
        repository.add(form_field)
        repository.commit()

        self._create_assignments(field_type, key, selected_org_ids, assignment_repo)
        return form_field, False  # was_existing = False

    def _handle_update_assignments(
        self, field_type: str, dto, identity: IdentityContext
    ):
        raw_ids = self._extract_org_ids(dto)
        if raw_ids is None:
            return  # No update to assignments

        selected_org_ids = list(raw_ids)
        if not selected_org_ids:
            if not self._form_fields_permissions_service.can_create_global_fields(
                identity
            ):
                raise HTTPException(
                    status_code=403,
                    detail="Only Catalogue Managers can make form fields global. Please select at least one organization.",
                )
        else:
            self._form_fields_permissions_service.validate_selected_organizations(
                identity, selected_org_ids
            )
        _, assignment_repo = self._get_repositories(field_type)
        self._replace_assignments(
            field_type, dto.key, selected_org_ids, assignment_repo
        )

    def _update_field_properties(
        self, field_type: str, repository, dto, user_id: int, original_data
    ):
        if field_type == "applicable_legislation":
            form_field = repository.update(
                dto.key, dto.eng_label, dto.description, dto.link
            )
            self._activity_log_service.log_applicable_legislation_activities(
                user_id=user_id,
                applicable_legislation_key=dto.key,
                applicable_legislation_data=original_data,
                updated_applicable_legislation_data=dto,
                action_type="update",
            )
        else:
            form_field = repository.update(dto.key, dto.eng_label)
            self._activity_log_service.log_keyword_activities(
                user_id=user_id,
                keyword_key=dto.key,
                keyword_data=original_data,
                updated_keyword_data=(
                    dto.model_dump() if hasattr(dto, "model_dump") else dto
                ),
                action_type="update",
            )
        return form_field

    def _check_field_dependencies(self, field_type: str, key: str):
        datasets = []
        distributions = []
        if field_type == "keyword":
            datasets = self._dataset_repository.get_datasets_by_keyword(key)
        elif field_type == "applicable_legislation":
            datasets = self._dataset_repository.get_datasets_by_applicable_legislation(
                key
            )
            distributions = self._distribution_repository.get_distributions_by_applicable_legislation(
                key
            )
        if datasets or distributions:
            raise HTTPException(
                status_code=400,
                detail=f"Cannot delete {field_type}, it is linked to existing datasets or distributions.",
            )

    def _log_deletion_activity(
        self, field_type: str, key: str, user_id: int, original_data
    ):
        if field_type == "keyword":
            self._activity_log_service.log_keyword_activities(
                user_id=user_id,
                keyword_key=key,
                keyword_data=original_data,
                updated_keyword_data={},
                action_type="delete",
            )
        elif field_type == "applicable_legislation":
            self._activity_log_service.log_applicable_legislation_activities(
                user_id=user_id,
                applicable_legislation_key=key,
                applicable_legislation_data=original_data,
                updated_applicable_legislation_data=ApplicableLegislationFormFieldDto(
                    key=key, eng_label="", description="", link="", organisation_ids=[]
                ),
                action_type="delete",
            )

    def _get_repositories(self, field_type: str) -> Tuple[Any, Optional[Any]]:
        if field_type == "keyword":
            return self._keyword_repository, self._keyword_assignment_repository
        elif field_type == "applicable_legislation":
            return (
                self._applicable_legislation_repository,
                self._applicable_legislation_assignment_repository,
            )
        return None, None

    def _get_repository(self, field_type: str):
        if field_type not in self._repositories:
            raise ValueError(f"Unsupported field type: {field_type}")
        return self._repositories[field_type]

    def _validate_and_assign_to_existing(
        self,
        field_type: str,
        existing_field,
        selected_org_ids: List[int],
        assignment_repo,
        identity: IdentityContext,
    ):
        existing_assignments = self._get_field_assignments(
            field_type, existing_field.key, assignment_repo
        )

        if not selected_org_ids:
            if existing_assignments:
                if not self._form_fields_permissions_service.can_create_global_fields(
                    identity
                ):
                    return
                for assignment in existing_assignments:
                    from sqlalchemy.orm import object_session

                    session = object_session(assignment)
                    if session:
                        session.delete(assignment)
                assignment_repo.commit()
                return
            if self._error_on_global_conflict():
                identifier = "label" if field_type == "keyword" else "key"
                value = (
                    existing_field.eng_label
                    if field_type == "keyword"
                    else existing_field.key
                )
                raise HTTPException(
                    status_code=400,
                    detail=f"A {field_type.replace('_', ' ')} with the {identifier} '{value}' already exists and is global.",
                )
            return

        if not existing_assignments:
            if self._error_on_global_conflict():
                identifier = "label" if field_type == "keyword" else "key"
                value = (
                    existing_field.eng_label
                    if field_type == "keyword"
                    else existing_field.key
                )
                raise HTTPException(
                    status_code=400,
                    detail=f"A {field_type.replace('_', ' ')} with the {identifier} '{value}' already exists and is global.",
                )
            return

        new_assignment_org_ids: List[int] = []
        for org_id in selected_org_ids:
            if self._has_assignment(
                field_type, existing_field.key, org_id, assignment_repo
            ):
                if self._error_on_assignment_conflict():
                    org = self._organisation_repository.get_organisation(org_id)
                    org_name = org.name if org else f"Org {org_id}"
                    identifier = "label" if field_type == "keyword" else "key"
                    value = (
                        existing_field.eng_label
                        if field_type == "keyword"
                        else existing_field.key
                    )
                    raise HTTPException(
                        status_code=400,
                        detail=f"A {field_type.replace('_', ' ')} with the {identifier} '{value}' already exists and is assigned to organisation '{org_name}'.",
                    )
                continue
            new_assignment_org_ids.append(org_id)

        if new_assignment_org_ids:
            self._create_assignments(
                field_type, existing_field.key, new_assignment_org_ids, assignment_repo
            )

    def _get_field_assignments(self, field_type: str, field_key: str, assignment_repo):
        if field_type == "keyword":
            return assignment_repo.get_keyword_organisation_assignments(field_key)
        elif field_type == "applicable_legislation":
            return assignment_repo.get_applicable_legislation_organisation_assignments(
                field_key
            )
        return []

    def _has_assignment(
        self, field_type: str, field_key: str, org_id: int, assignment_repo
    ) -> bool:
        if field_type == "keyword":
            assignment = assignment_repo.get_keyword_organisation_assignment(
                field_key, org_id
            )
        elif field_type == "applicable_legislation":
            assignment = (
                assignment_repo.get_applicable_legislation_organisation_assignment(
                    field_key, org_id
                )
            )
        else:
            return False
        return assignment is not None

    def _get_assignment(
        self, field_type: str, field_key: str, org_id: int, assignment_repo
    ):
        if field_type == "keyword":
            return assignment_repo.get_keyword_organisation_assignment(
                field_key, org_id
            )
        elif field_type == "applicable_legislation":
            return assignment_repo.get_applicable_legislation_organisation_assignment(
                field_key, org_id
            )
        return None

    def _create_field(self, field_type: str, key: str, dto, identity: IdentityContext):
        base_kwargs = {
            "key": key,
            "eng_label": dto.eng_label,
            "created_by_id": identity.user_id,
        }

        if field_type == "keyword":
            return Keyword(**base_kwargs)
        elif field_type == "applicable_legislation":
            return ApplicableLegislation(
                **base_kwargs, description=dto.description, link=dto.link
            )

    def _create_assignments(
        self,
        field_type: str,
        field_key: str,
        selected_org_ids: List[int],
        assignment_repo,
    ):
        if not selected_org_ids:
            return

        for org_id in selected_org_ids:
            if field_type == "keyword":
                assignment = KeywordAssignment(
                    keyword_key=field_key, organisation_id=org_id
                )
                assignment_repo.add_keyword_organisation_assignment(assignment)
            elif field_type == "applicable_legislation":
                assignment = ApplicableLegislationAssignment(
                    applicable_legislation_key=field_key, organisation_id=org_id
                )
                assignment_repo.add_applicable_legislation_organisation_assignment(
                    assignment
                )
        assignment_repo.commit()

    def _replace_assignments(
        self,
        field_type: str,
        field_key: str,
        selected_org_ids: List[int],
        assignment_repo,
    ):
        existing_assignments = self._get_field_assignments(
            field_type, field_key, assignment_repo
        )
        existing_org_ids = {a.organisation_id for a in existing_assignments}
        selected_org_ids_set = set(selected_org_ids)
        to_remove = existing_org_ids - selected_org_ids_set
        to_add = selected_org_ids_set - existing_org_ids

        if to_remove:
            for assignment in existing_assignments:
                if assignment.organisation_id in to_remove:
                    from sqlalchemy.orm import object_session

                    session = object_session(assignment)
                    if session:
                        session.delete(assignment)

        # Add new assignments
        for org_id in to_add:
            if field_type == "keyword":
                assignment = KeywordAssignment(
                    keyword_key=field_key, organisation_id=org_id
                )
                assignment_repo.add_keyword_organisation_assignment(assignment)
            elif field_type == "applicable_legislation":
                assignment = ApplicableLegislationAssignment(
                    applicable_legislation_key=field_key, organisation_id=org_id
                )
                assignment_repo.add_applicable_legislation_organisation_assignment(
                    assignment
                )

        if to_remove or to_add:
            assignment_repo.commit()

    def _log_activity(self, field_type: str, key: str, dto, user_id: int):
        log_methods = {
            "keyword": self._activity_log_service.log_keyword_activities,
            "applicable_legislation": self._activity_log_service.log_applicable_legislation_activities,
        }
        method = log_methods.get(field_type)
        if method:
            method(
                user_id=user_id,
                **{f"{field_type}_key": key},
                **{f"{field_type}_data": {}},
                **{
                    f"updated_{field_type}_data": (
                        dto.model_dump() if hasattr(dto, "model_dump") else dto
                    )
                },
                action_type="create",
            )

    def _format_response(
        self, field_type: str, field: Union[Keyword, ApplicableLegislation]
    ) -> Union[ResourceFormField, ApplicableLegislationFormField]:
        org_ids = []

        if field_type in ["keyword", "applicable_legislation"]:
            assignment_repo = self._assignment_repositories[field_type]
            if field_type == "keyword":
                assignments = assignment_repo.get_keyword_organisation_assignments(
                    field.key
                )
            else:
                assignments = (
                    assignment_repo.get_applicable_legislation_organisation_assignments(
                        field.key
                    )
                )
            org_ids = [assignment.organisation_id for assignment in assignments]

        if field_type == "applicable_legislation":
            return ApplicableLegislationFormField(
                key=field.key,
                eng_label=field.eng_label,
                description=field.description,
                link=field.link,
                organisation_ids=org_ids,
                created_by_id=field.created_by_id,
                created_by_name=(field.created_by.name if field.created_by else None),
            )
        else:
            return ResourceFormField(
                key=field.key,
                eng_label=field.eng_label,
                created_by_id=field.created_by_id,
                created_by_name=(field.created_by.name if field.created_by else None),
                organisation_ids=org_ids,
            )

    def promote_to_global(
        self, field_type: str, key: str, identity: IdentityContext
    ) -> Union[ResourceFormField, ApplicableLegislationFormField]:
        if not self._form_fields_permissions_service.can_create_global_fields(identity):
            raise HTTPException(
                status_code=403,
                detail="Only Catalogue Managers can promote form fields to global",
            )

        repository = self._get_repository(field_type)
        form_field = repository.get(key)

        if not form_field:
            raise HTTPException(
                status_code=404, detail=f"Form field with key '{key}' not found"
            )

        _, assignment_repo = self._get_repositories(field_type)
        existing_assignments = self._get_field_assignments(
            field_type, key, assignment_repo
        )

        if not existing_assignments:
            raise HTTPException(status_code=400, detail=f"Form field is already global")

        for assignment in existing_assignments:
            from sqlalchemy.orm import object_session

            session = object_session(assignment)
            if session:
                session.delete(assignment)

        assignment_repo.commit()

        original_data = {
            "organisation_assignments": [
                a.organisation_id for a in existing_assignments
            ]
        }
        if field_type == "keyword":
            self._activity_log_service.log_keyword_activities(
                user_id=identity.user_id,
                keyword_key=key,
                keyword_data=original_data,
                updated_keyword_data={"promoted_to_global": True},
                action_type="promote_to_global",
            )
        elif field_type == "applicable_legislation":
            self._activity_log_service.log_applicable_legislation_activities(
                user_id=identity.user_id,
                applicable_legislation_key=key,
                applicable_legislation_data=original_data,
                updated_applicable_legislation_data={"promoted_to_global": True},
                action_type="promote_to_global",
            )

        return self._format_response(field_type, form_field)
