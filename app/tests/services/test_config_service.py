import pytest
from services.config import ConfigService


@pytest.fixture(scope="function")
def config_service():
    return ConfigService("./config.json")


def test_load_config(config_service):
    assert (
        config_service.config_data["config_version"] == "1.0"
    ), "Config version should match the expected version"
    assert "roles" in config_service.config_data, "Config should contain roles"


def test_get_roles_by_permission(config_service):
    roles = config_service.get_roles_by_permission(
        "datasets:status-change:validate:group"
    )

    assert roles[0]["name"] == "GROUP_MANAGER", "Should return the correct role"
