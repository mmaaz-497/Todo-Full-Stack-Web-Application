import pytest
import os
from pydantic import ValidationError


def test_settings_loads_from_environment(monkeypatch):
    """Test Settings class loads all required environment variables"""
    monkeypatch.setenv("DATABASE_URL", "postgresql://test:test@localhost/testdb")
    monkeypatch.setenv("GOOGLE_API_KEY", "test_key")
    monkeypatch.setenv("GEMINI_MODEL_NAME", "gemini-1.5-pro")
    monkeypatch.setenv("AUTH_SECRET", "test_secret")
    monkeypatch.setenv("AUTH_ISSUER", "https://auth.test.com")
    
    from app.config import Settings
    settings = Settings()
    
    assert settings.DATABASE_URL == "postgresql://test:test@localhost/testdb"
    assert settings.GOOGLE_API_KEY == "test_key"
    assert settings.GEMINI_MODEL_NAME == "gemini-1.5-pro"


def test_settings_raises_error_on_missing_database_url(monkeypatch):
    """Test Settings raises error when DATABASE_URL missing"""
    monkeypatch.delenv("DATABASE_URL", raising=False)
    monkeypatch.setenv("GOOGLE_API_KEY", "test_key")
    monkeypatch.setenv("AUTH_SECRET", "test_secret")
    monkeypatch.setenv("AUTH_ISSUER", "https://auth.test.com")
    
    with pytest.raises(ValidationError):
        from app.config import Settings
        Settings()


def test_settings_raises_error_on_missing_google_api_key(monkeypatch):
    """Test Settings raises error when GOOGLE_API_KEY missing"""
    monkeypatch.setenv("DATABASE_URL", "postgresql://test:test@localhost/testdb")
    monkeypatch.delenv("GOOGLE_API_KEY", raising=False)
    monkeypatch.setenv("AUTH_SECRET", "test_secret")
    monkeypatch.setenv("AUTH_ISSUER", "https://auth.test.com")
    
    with pytest.raises(ValidationError):
        from app.config import Settings
        Settings()


def test_settings_uses_defaults_for_optional_fields(monkeypatch):
    """Test Settings uses default values for optional configuration"""
    monkeypatch.setenv("DATABASE_URL", "postgresql://test:test@localhost/testdb")
    monkeypatch.setenv("GOOGLE_API_KEY", "test_key")
    monkeypatch.setenv("AUTH_SECRET", "test_secret")
    monkeypatch.setenv("AUTH_ISSUER", "https://auth.test.com")
    
    from app.config import Settings
    settings = Settings()
    
    assert settings.GEMINI_MODEL_NAME == "gemini-1.5-pro"  # Default
    assert settings.GEMINI_TEMPERATURE == 0.7  # Default
    assert settings.GEMINI_MAX_TOKENS == 2048  # Default
    assert settings.LOG_LEVEL == "INFO"  # Default
