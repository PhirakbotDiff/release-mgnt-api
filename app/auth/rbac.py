ROLE_ENV_MAP = {
    "developer": ["dev", "uat"],
    "lead": ["dev", "uat", "prod"],
    "sre": ["*"]
}

def check_env_permission(role: str, env: str):
    allowed = ROLE_ENV_MAP.get(role, [])
    if "*" in allowed:
        return True
    return env in allowed
