import json
import os


def load_secrets_into_env() -> None:
    """Extension point: swap the plain `.env` file for a real secrets manager.

    Called once at import time by config.py, before `Settings()` reads the
    environment. No-op unless SECRETS_PROVIDER is set, so local dev/CI/the
    current .env-based deployment are unaffected. Populated values only fill
    in variables not already set (os.environ.setdefault), so an explicit env
    var always wins over the secrets backend.
    """
    provider = os.getenv("SECRETS_PROVIDER", "").lower()
    if not provider:
        return
    if provider == "aws":
        _load_from_aws_secrets_manager()
    else:
        raise ValueError(f"Unsupported SECRETS_PROVIDER: {provider!r}")


def _load_from_aws_secrets_manager() -> None:
    import boto3  # optional dependency: pip install boto3 (only needed for this provider)

    secret_id = os.environ["AWS_SECRET_ID"]
    client = boto3.client("secretsmanager", region_name=os.getenv("AWS_REGION", "us-east-1"))
    secret_string = client.get_secret_value(SecretId=secret_id)["SecretString"]
    for key, value in json.loads(secret_string).items():
        os.environ.setdefault(key, str(value))
