import os
import tempfile
import shutil
from pathlib import Path
from typing import Generator, Dict, Any
import pytest
import yaml


@pytest.fixture
def temp_dir() -> Generator[Path, None, None]:
    """Create a temporary directory for test files."""
    temp_path = Path(tempfile.mkdtemp())
    try:
        yield temp_path
    finally:
        shutil.rmtree(temp_path, ignore_errors=True)


@pytest.fixture
def temp_file(temp_dir: Path) -> Generator[Path, None, None]:
    """Create a temporary file in the temp directory."""
    temp_file_path = temp_dir / "test_file.txt"
    temp_file_path.write_text("test content")
    yield temp_file_path


@pytest.fixture
def mock_config() -> Dict[str, Any]:
    """Provide a mock configuration dictionary."""
    return {
        "debug": True,
        "database": {
            "host": "localhost",
            "port": 5432,
            "name": "test_db",
            "user": "test_user",
            "password": "test_password"
        },
        "api": {
            "base_url": "http://localhost:8000",
            "timeout": 30,
            "retry_count": 3
        },
        "features": {
            "feature_a": True,
            "feature_b": False
        }
    }


@pytest.fixture
def mock_yaml_config(temp_dir: Path, mock_config: Dict[str, Any]) -> Path:
    """Create a temporary YAML configuration file."""
    config_path = temp_dir / "config.yaml"
    with open(config_path, 'w') as f:
        yaml.dump(mock_config, f)
    return config_path


@pytest.fixture
def mock_env_vars(monkeypatch) -> Dict[str, str]:
    """Set up mock environment variables."""
    env_vars = {
        "TEST_ENV": "testing",
        "DEBUG": "true",
        "API_KEY": "test_api_key_123",
        "DATABASE_URL": "postgresql://user:pass@localhost/testdb"
    }
    
    for key, value in env_vars.items():
        monkeypatch.setenv(key, value)
    
    return env_vars


@pytest.fixture
def clean_env(monkeypatch):
    """Remove specific environment variables for testing."""
    env_vars_to_remove = ["API_KEY", "DATABASE_URL", "SECRET_KEY"]
    for var in env_vars_to_remove:
        monkeypatch.delenv(var, raising=False)


@pytest.fixture
def mock_request_data() -> Dict[str, Any]:
    """Provide mock HTTP request data."""
    return {
        "headers": {
            "Content-Type": "application/json",
            "Authorization": "Bearer test_token",
            "User-Agent": "TestClient/1.0"
        },
        "body": {
            "id": 123,
            "name": "Test Item",
            "data": {"key": "value"}
        },
        "params": {
            "page": 1,
            "limit": 10,
            "sort": "created_at"
        }
    }


@pytest.fixture
def sample_data_list() -> list:
    """Provide a sample list of test data."""
    return [
        {"id": 1, "name": "Item 1", "value": 100},
        {"id": 2, "name": "Item 2", "value": 200},
        {"id": 3, "name": "Item 3", "value": 300},
    ]


@pytest.fixture(autouse=True)
def reset_singleton_instances():
    """Reset singleton instances between tests to ensure test isolation."""
    # This is a placeholder for resetting any singleton patterns
    # that might exist in the codebase
    yield


@pytest.fixture
def capture_logs(caplog):
    """Fixture to help capture and assert on log messages."""
    with caplog.at_level("DEBUG"):
        yield caplog


@pytest.fixture
def mock_datetime(monkeypatch):
    """Mock datetime for consistent testing."""
    from datetime import datetime
    
    class MockDatetime(datetime):
        @classmethod
        def now(cls, tz=None):
            return cls(2024, 1, 1, 12, 0, 0)
        
        @classmethod
        def utcnow(cls):
            return cls(2024, 1, 1, 12, 0, 0)
    
    monkeypatch.setattr("datetime.datetime", MockDatetime)
    return MockDatetime


# Markers for test organization
def pytest_configure(config):
    """Register custom markers."""
    config.addinivalue_line(
        "markers", "unit: mark test as a unit test"
    )
    config.addinivalue_line(
        "markers", "integration: mark test as an integration test"
    )
    config.addinivalue_line(
        "markers", "slow: mark test as slow running"
    )


# Skip slow tests unless explicitly requested
def pytest_collection_modifyitems(config, items):
    """Modify test collection to handle markers."""
    if config.getoption("--run-slow"):
        # --run-slow given in cli: do not skip slow tests
        return
    skip_slow = pytest.mark.skip(reason="need --run-slow option to run")
    for item in items:
        if "slow" in item.keywords:
            item.add_marker(skip_slow)


def pytest_addoption(parser):
    """Add custom command line options."""
    parser.addoption(
        "--run-slow", action="store_true", default=False, help="run slow tests"
    )