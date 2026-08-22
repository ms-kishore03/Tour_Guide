import pytest

from app.core.secrets import load_secrets_into_env


def test_noop_without_secrets_provider(monkeypatch):
    monkeypatch.delenv("SECRETS_PROVIDER", raising=False)
    load_secrets_into_env()  # must not raise, must not touch anything


def test_unknown_provider_raises(monkeypatch):
    monkeypatch.setenv("SECRETS_PROVIDER", "not-a-real-provider")
    with pytest.raises(ValueError, match="Unsupported SECRETS_PROVIDER"):
        load_secrets_into_env()
