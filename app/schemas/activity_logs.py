from dataclasses import dataclass
from models.activity_log import ActivityLog


@dataclass(frozen=True)
class ResourceActivityLog:
    id: int
    username: str
    action_type: str
    entity_type: str
    entity_id: str
    changes: str
    timestamp: str


def activity_log_entity_to_resource(activity_log: ActivityLog) -> ResourceActivityLog:
    if activity_log.user:
        username = activity_log.user.name
    elif activity_log.user_id is not None:
        username = f"Deleted user ({activity_log.user_id})"
    else:
        username = "Deleted user"
    return ResourceActivityLog(
        id=activity_log.id,
        username=username,
        action_type=activity_log.action_type,
        entity_type=activity_log.entity_type,
        entity_id=str(activity_log.entity_id),
        changes=activity_log.changes,
        timestamp=activity_log.timestamp.isoformat(),
    )
