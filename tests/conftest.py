import os
import tempfile
from pathlib import Path

import pytest
from fastapi.testclient import TestClient

os.environ["CERTIFICATE_TEST_MODE"] = "1"

from app.main import app

@pytest.fixture
def client():
    return TestClient(app)
