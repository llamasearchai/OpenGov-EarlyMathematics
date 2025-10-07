"""Additional tests for config validators."""

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent.parent / "src"))

from opengov_earlymathematics.config import Settings


def test_parse_cors_origins_from_string():
    s = Settings(cors_origins="http://a.com, http://b.com")
    assert s.cors_origins == ["http://a.com", "http://b.com"]

