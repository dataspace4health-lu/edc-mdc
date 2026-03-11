import json
import os
from pathlib import Path
from typing import Any, Dict
from fastapi import Request
from jsonschema import validate, ValidationError, SchemaError


class ConfigService:
    def __init__(self, config_file_path: str):
        self.config_file_path = Path(config_file_path)
        self.schema_file_path = Path("./config.schema.json")
        self.config_data: Dict[str, Any] = {}
        self.original_config_data: Dict[str, Any] = {}  # Store original for reset
        self.load_config()

    def load_schema(self):
        with self.schema_file_path.open("r") as file:
            return json.load(file)

    def load_config(self):
        if not self.config_file_path.exists():
            raise FileNotFoundError(
                f"The config file {self.config_file_path} does not exist."
            )
        with self.config_file_path.open("r") as file:
            data = json.load(file)
            self.validate_config(data)
            self.config_data = data
            self.original_config_data = json.loads(json.dumps(data))

    def validate_config(self, data):
        schema = self.load_schema()
        try:
            validate(instance=data, schema=schema)
        except ValidationError as ve:
            raise ValueError(f"Configuration validation error: {ve}")
        except SchemaError as se:
            raise ValueError(f"Schema validation error: {se}")

    def update_config_value(self, key_path: str, value: Any):
        if os.getenv("ENVIRONMENT") != "end2end":
            raise ValueError("Config updates only allowed in end2end environment")

        keys = key_path.split(".")
        current = self.config_data

        # Navigate to the parent of the target key
        for key in keys[:-1]:
            if key not in current:
                raise KeyError(f"Key path '{key_path}' not found in config")
            current = current[key]

        # Set the final key
        final_key = keys[-1]
        if final_key not in current:
            raise KeyError(f"Key path '{key_path}' not found in config")

        current[final_key] = value

    def update_feature_flag(self, flag_name: str, enabled: bool):
        if os.getenv("ENVIRONMENT") != "end2end":
            raise ValueError("Feature flag updates only allowed in end2end environment")

        if "feature_flags" not in self.config_data:
            raise KeyError("feature_flags section not found in config")

        if flag_name not in self.config_data["feature_flags"]:
            raise KeyError(f"Feature flag '{flag_name}' not found in config")

        self.config_data["feature_flags"][flag_name] = enabled

    def reset_config(self):
        if os.getenv("ENVIRONMENT") != "end2end":
            raise ValueError("Config reset only allowed in end2end environment")

        self.config_data = json.loads(json.dumps(self.original_config_data))

    def get_app_title(self):
        return self.config_data.get("app_title", "Dataset Metadata Capture")

    def get_conventions(self):
        return self.config_data.get("conventions", [])

    def get_areas_of_work(self):
        return self.config_data.get("areas_of_work", [])

    def get_areas_of_competence(self):
        return self.config_data.get("areas_of_competence", [])

    def get_roles(self):
        return self.config_data.get("roles", [])

    def get_roles_path_in_access_token(self):
        return self.config_data.get("roles_path_in_access_token", [])

    def get_distribution_path(self):
        return self.config_data.get("distribution_path", [])

    def get_email_templates(self):
        return self.config_data.get("email_templates", {})

    def get_feature_flags(self):
        return self.config_data.get("feature_flags", {})

    def get_roles_by_permission(self, permission: str):
        return [
            role
            for role in self.get_roles()
            if permission in role.get("permissions", [])
        ]

    def get_default_themes(self):
        return self.config_data.get("default_themes", [])

    def get_show_notice_on_homepage(self):
        return self.config_data.get("show_notice_on_homepage", "")

    def get_roles_with_disable_email(self):
        return self.config_data.get("disable_email_for_roles", [])

    def get_unauthorised_message(self):
        return self.config_data.get("unauthorised_message", "")

    def get_technical_support_message(self):
        return self.config_data.get("technical_support_message", "")

    # def get_enable_multi_tenants(self) -> bool:
    #     return self.config_data.get("feature_flags")["enable_multi_tenants"]

    def get_enable_multi_tenants(self) -> bool:
        return bool(self.get_feature_flags().get("enable_multi_tenants", False))

    def get_enable_dual_instance(self) -> bool:
        return bool(self.get_feature_flags().get("enable_dual_instance", False))

    def get_catalogue(self):
        return self.config_data.get("catalogue", {})

    def get_health_data_access_body(self):
        return self.config_data.get("health_data_access_body", {})

    def is_ctie_instance(self) -> bool:
        return bool(os.getenv("SOURCE_INSTANCE_URL", ""))


def get_config_service(request: Request) -> ConfigService:
    return request.app.state.config_service
