import json
import subprocess
import os
import logging

from fastapi import FastAPI, HTTPException
from pydantic import BaseModel, Field
from app.config import settings


logger = logging.getLogger("api")

docker_config = settings.TRIVY_CONFIG

def run_trivy(
    image: str, 
    severities: list[str] = settings.SEVERITIES, 
    insecure: bool = True
) -> dict:
    
    # this used for run os host
    cmd = [
        "trivy",
        "image",
        "--server", 
        settings.TRIVY_SERVER,
        "--format", 
        # "--username", settings.IMAGE_REGISTRY_USERNAME,
        # "--password", settings.IMAGE_REGISTRY_PASSWORD,
        "json",
        "--ignore-unfixed",
        "--severity", 
        ",".join(severities),
    ]

    # cmd = [
    #     "docker", "run", "--rm",
    #     "-v", f"{docker_config}:/root/.docker/config.json:ro",
    #     "-v", "/var/run/docker.sock:/var/run/docker.sock",
    #     "aquasec/trivy:latest",
    #     "image",
    #     "--ignore-unfixed",
    #     "--format", 
    #     "json",
    #     "--severity", 
    #     ",".join(severities)
    # ]

    if insecure:
        cmd.append("--insecure")

    cmd.append(image)

    try:
        result = subprocess.run(
            cmd,
            capture_output=True,
            text=True,
            timeout=600
        )
        logger.info("Trivy scan success")
    except subprocess.TimeoutExpired:
        logger.exception("Trivy scan timed out")
        raise HTTPException(
            status_code=504, 
            detail="Trivy scan timed out"
        )

    # Trivy exit codes:
    # 0 = no vulns
    # 5 = vulns found
    if result.returncode not in (0, 5):
        logger.exception(result.stderr.strip() or "Trivy execution failed")
        raise HTTPException(
            status_code=500,
            detail=result.stderr.strip() or "Trivy execution failed"
        )

    return json.loads(result.stdout)