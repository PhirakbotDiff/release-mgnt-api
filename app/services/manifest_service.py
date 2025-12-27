import yaml
from pathlib import Path

ALLOWED_BASE_PATH = "apps"

class ManifestService:

    def update_image_tag(self, service: str, env: str, tag: str):
        file_path = Path(
            f"{ALLOWED_BASE_PATH}/{service}/{env}/values.yaml"
        )

        if not file_path.exists():
            raise FileNotFoundError("Manifest file not found")

        with open(file_path) as f:
            data = yaml.safe_load(f)

        if "image" not in data:
            raise ValueError("Invalid manifest structure")

        data["image"]["tag"] = tag

        with open(file_path, "w") as f:
            yaml.safe_dump(data, f)

        return str(file_path)
