import re
import hashlib


class KeyGenerator:
    @staticmethod
    def generate_key_from_label(label: str, max_length: int = 100) -> str:
        if not label:
            return ""

        # Convert to lowercase and replace spaces/special chars with underscores
        key = re.sub(r"[^a-z0-9]", "_", label.lower())

        # Remove consecutive underscores
        key = re.sub(r"_+", "_", key)

        # Truncate to max length
        key = key[:max_length]

        # Remove trailing underscores
        key = key.rstrip("_")

        return key

    @staticmethod
    def generate_key_from_label_and_link(
        label: str, link: str, max_label_length: int = 80
    ) -> str:
        if not label:
            return ""

        # Generate base key from label
        base_key = KeyGenerator.generate_key_from_label(label, max_label_length)

        # If no link, return label-based key only
        if not link or not link.strip():
            return KeyGenerator.generate_key_from_label(label, 100)

        # Generate a short hash from the link for uniqueness
        link_hash = hashlib.sha256(link.encode("utf-8")).hexdigest()[:12]

        # Combine base key with link hash
        return f"{base_key}_{link_hash}"
