import json
import subprocess
from fastapi import FastAPI, HTTPException
from pydantic import BaseModel, Field
from app.config import settings
import logging


logger = logging.getLogger("api")


def run_trivy(
    image: str, 
    severities: list[str] = settings.SEVERITIES, 
    insecure: bool = True
) -> dict:
    
    cmd = [
        "trivy",
        "image",
        "--server", settings.TRIVY_SERVER,
        "--format", "json",
        "--severity", ",".join(severities),
    ]

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