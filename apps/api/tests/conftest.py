import os

import pytest


@pytest.fixture(scope="session")
def integration_enabled() -> bool:
    return os.getenv("INTEGRATION") == "1"
