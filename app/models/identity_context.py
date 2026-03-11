from pydantic import BaseModel


class IdentityContext(BaseModel):
    user_id: int
    permissions: list[str]
    current_organisation_id: int | None = None
