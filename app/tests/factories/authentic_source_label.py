from datetime import datetime, timezone
from models.authentic_source_label import AuthenticSourceLabel


def create_sample_authentic_source_label(
    id=1,
    name="Government Records",
    description="Official government databases and records",
    created_at=datetime.now(timezone.utc),
    created_by=1,
    is_deprecated=False,
):
    return AuthenticSourceLabel(
        id=id,
        name=name,
        description=description,
        created_at=created_at,
        created_by=created_by,
        is_deprecated=is_deprecated,
    )
