import yaml # type: ignore
from pathlib import Path

import logging

logger = logging.getLogger("api")

ALLOWED_BASE_PATH = "./manifest-repo/charts"

class ManifestService:

    def update_image_tag(
        self, 
        manifest_repo_path: str, 
        service: str, 
        env: str, 
        tag: str,
        manifest_path: str # real manifest charts
    ):

        repo_root = Path(manifest_repo_path)
        file_path = Path(
            f"{repo_root}/{manifest_path}/values.yaml"
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
